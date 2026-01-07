# downtime_parser.py
# -*- coding: utf-8 -*-
"""
پارس توقفات stops.txt بر اساس start_read_datetime

قواعدی که اعمال می‌شود:

1) اگر چند ردیف تکراری داشتیم که:
   - resourceID یکی باشد
   - stop_type یکی باشد
   - start_read_datetime یکی باشد
   => یک توقف حساب می‌کنیم (end = بزرگ‌ترین stop_read_datetime گروه)

2) اگر "پایان" داریم ولی "شروع" نداریم:
   - اول تلاش می‌کنیم با یک شروعِ بازِ قبلی match کنیم (همان line و همان stop_type)
   - اگر پیدا نشد، با آخرین شروع باز (صرف‌نظر از نوع) match می‌کنیم
   - اگر هیچ شروع بازی نبود، با آخرین شروعِ دیده‌شده قبل از این پایان match می‌کنیم

3) اگر "شروع" داریم و قبل از بسته‌شدنش دوباره "شروع" می‌آید:
   => شروع دوم، پایان توقف اول حساب می‌شود (auto-close)

4) شرط یکسان بودن stop_type:
   - اگر stop_type == 0 باشد، مثل wildcard عمل می‌کند و می‌تواند با هر stop_type دیگری match شود.
   - اگر stop_type != 0 باشد، شرط یکی بودن نوع توقف برقرار است.

نکته: پارس datetime tolerant است و زمان‌های خراب مثل 07:61:52.168662 را هم با overflow درست می‌کند.
"""

from __future__ import annotations

import ast
import datetime as dt
import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple, DefaultDict
from collections import defaultdict

_DT_FMT = "%Y-%m-%d %H:%M:%S.%f"

_DT_RE = re.compile(
    r"^(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})[ T]"
    r"(?P<h>\d{1,2}):(?P<mi>\d{1,2}):(?P<s>\d{1,2})"
    r"(?:\.(?P<us>\d{1,6}))?$"
)


@dataclass(frozen=True)
class StopEvent:
    resource_id: Any
    stop_type: int
    start_read_datetime: str  # برای trace/debug
    start: dt.datetime
    end: Optional[dt.datetime]

    @property
    def duration(self) -> Optional[dt.timedelta]:
        if self.end is None:
            return None
        return self.end - self.start


def load_stops_txt(path: str) -> List[Dict[str, Any]]:
    """هر خط فایل یک dict پایتونی است."""
    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            try:
                obj = ast.literal_eval(s)
                if isinstance(obj, dict):
                    rows.append(obj)
            except Exception:
                continue
    return rows


def _safe_int(x: Any, default: int = 0) -> int:
    try:
        if x is None:
            return default
        return int(x)
    except Exception:
        return default


def _dt_to_str(x: dt.datetime) -> str:
    try:
        return x.strftime(_DT_FMT)
    except Exception:
        return str(x)


def _parse_dt(x: Any) -> Optional[dt.datetime]:
    """
    پارس مقاوم datetime:
    - اول strptime استاندارد
    - بعد regex و ساخت datetime با overflow (minute/second > 59)
    - بعد fromisoformat
    """
    if x in (None, "", "null"):
        return None
    if isinstance(x, dt.datetime):
        return x
    if not isinstance(x, str):
        return None

    s = x.strip()

    # حالت استاندارد
    try:
        return dt.datetime.strptime(s, _DT_FMT)
    except Exception:
        pass

    # حالت tolerant با overflow
    m = _DT_RE.match(s)
    if m:
        y = int(m.group("y"))
        mo = int(m.group("m"))
        d = int(m.group("d"))
        hh = int(m.group("h"))
        mi = int(m.group("mi"))
        ss = int(m.group("s"))
        us_raw = m.group("us") or "0"
        us = int(us_raw.ljust(6, "0")[:6])

        try:
            base = dt.datetime(y, mo, d, 0, 0, 0, 0)
        except Exception:
            return None

        # overflowها اینجا خودشون اصلاح می‌شن
        return base + dt.timedelta(hours=hh, minutes=mi, seconds=ss, microseconds=us)

    # isoformat
    try:
        return dt.datetime.fromisoformat(s)
    except Exception:
        return None


def _collapse_rows(
    rows: Iterable[Dict[str, Any]],
    stop_type_optional_if_zero: bool = True,
) -> List[Dict[str, Any]]:
    """
    ردیف‌های تکراری را بر اساس (resourceID, stop_type, start_read_datetime) یکی می‌کند.

    خروجی هر آیتم:
      {
        "resource_id": rid,
        "stop_type": stype,
        "start": start_dt,
        "start_str": raw start_read_datetime string (یا فرمتی از start),
        "has_begin": bool,
        "end": end_dt or None
      }
    """
    groups: Dict[Tuple[Any, int, dt.datetime], Dict[str, Any]] = {}

    for r in rows:
        rid = r.get("resourceID")
        if rid is None:
            continue

        stype = _safe_int(r.get("stop_type"), 0)

        # اگر stop_type==0 باشد، wildcard است (ولی هنوز داخل کلید نگه می‌داریم =0)
        # (اختیاری بودن یعنی در match اجازه داریم با هر چیزی match کنیم)
        if not stop_type_optional_if_zero:
            # اگر خاموشش کنی، 0 هم مثل بقیه strict می‌شود
            pass

        start_dt = _parse_dt(r.get("start_read_datetime"))
        if start_dt is None:
            continue

        key = (rid, stype, start_dt)
        g = groups.get(key)
        if g is None:
            g = {
                "resource_id": rid,
                "stop_type": stype,
                "start": start_dt,
                "start_str": r.get("start_read_datetime") or _dt_to_str(start_dt),
                "has_begin": False,
                "end": None,
            }
            groups[key] = g

        # begin اگر stop_read_datetime نداشت
        if r.get("stop_read_datetime") in (None, "", "null"):
            g["has_begin"] = True
        else:
            end_dt = _parse_dt(r.get("stop_read_datetime"))
            if end_dt is not None:
                if g["end"] is None or end_dt > g["end"]:
                    g["end"] = end_dt

    items = list(groups.values())

    def _sort_k(x: Dict[str, Any]):
        # ترتیب پردازش: اساساً با زمان شروع، ولی اگر end-only بود، با زمان end هم کمک می‌گیریم
        start = x["start"]
        end = x["end"] or dt.datetime.max
        return (x["resource_id"], start, end)

    items.sort(key=_sort_k)
    return items


def build_events(
    rows: Iterable[Dict[str, Any]],
    include_open: bool = False,
    now: Optional[dt.datetime] = None,
    stop_type_optional_if_zero: bool = True,
) -> List[StopEvent]:
    """
    ساخت StopEvent با قوانین بالا (auto-close، end-without-begin، ...)

    - include_open=True => توقف‌های باز تا now بسته می‌شوند.
    """
    if now is None:
        now = dt.datetime.now()

    collapsed = _collapse_rows(rows, stop_type_optional_if_zero=stop_type_optional_if_zero)

    by_line: DefaultDict[Any, List[Dict[str, Any]]] = defaultdict(list)
    for g in collapsed:
        by_line[g["resource_id"]].append(g)

    all_events: List[StopEvent] = []

    for rid, items in by_line.items():
        # مرتب‌سازی برای پردازش: beginها با start، end-only ها با end
        def _evt_time(it: Dict[str, Any]) -> dt.datetime:
            if it["has_begin"]:
                return it["start"]
            return it["end"] or it["start"]

        items.sort(key=_evt_time)

        open_by_type: Dict[int, dt.datetime] = {}   # stop_type -> start_dt
        open_order: List[Tuple[dt.datetime, int]] = []  # (start_dt, stop_type)

        last_begin_any: Optional[dt.datetime] = None
        last_begin_by_type: Dict[int, dt.datetime] = {}

        def _add_open(stype: int, start_dt: dt.datetime):
            open_by_type[stype] = start_dt
            open_order.append((start_dt, stype))

        def _remove_open(stype: int) -> Optional[dt.datetime]:
            start_dt = open_by_type.pop(stype, None)
            if start_dt is None:
                return None
            for i, (sd, t) in enumerate(open_order):
                if t == stype and sd == start_dt:
                    open_order.pop(i)
                    break
            return start_dt

        def _latest_open() -> Optional[Tuple[dt.datetime, int]]:
            if not open_order:
                return None
            # بیشترین start_dt
            return max(open_order, key=lambda x: x[0])

        def _emit_event(ev_type: int, start_dt: dt.datetime, end_dt: dt.datetime):
            if end_dt <= start_dt:
                return
            all_events.append(
                StopEvent(
                    resource_id=rid,
                    stop_type=int(ev_type),
                    start_read_datetime=_dt_to_str(start_dt),
                    start=start_dt,
                    end=end_dt,
                )
            )

        for it in items:
            stype = int(it["stop_type"] or 0)
            start_dt = it["start"]
            end_dt = it["end"]
            has_begin = bool(it["has_begin"])

            if has_begin:
                # اگر همین نوع قبلاً باز بوده => auto-close با start_dt جدید
                if stype in open_by_type:
                    prev_start = open_by_type[stype]
                    _emit_event(stype, prev_start, start_dt)
                    _remove_open(stype)

                # اگر stop_type==0 باشد => wildcard: آخرین open را ببند
                if stype == 0:
                    latest = _latest_open()
                    if latest is not None:
                        prev_start, prev_type = latest
                        _emit_event(prev_type, prev_start, start_dt)
                        _remove_open(prev_type)

                # اگر end هم دارد، یعنی begin+end در یک گروه => event کامل
                if end_dt is not None:
                    _emit_event(stype, start_dt, end_dt)
                    # این begin را باز نگه نمی‌داریم
                else:
                    _add_open(stype, start_dt)

                last_begin_any = start_dt
                last_begin_by_type[stype] = start_dt
                continue

            # -----------------------
            # end-only
            # -----------------------
            if end_dt is None:
                continue

            match_start: Optional[dt.datetime] = None
            match_type: int = stype

            if stype != 0:
                # حالت strict: اول دنبال open هم‌نوع
                if stype in open_by_type:
                    match_start = open_by_type[stype]
                    match_type = stype
                    _remove_open(stype)
                else:
                    # اگر stop_type_optional_if_zero و open type 0 داریم => می‌تونه match بشه
                    if stop_type_optional_if_zero and 0 in open_by_type:
                        match_start = open_by_type[0]
                        match_type = stype  # نوع رو از end می‌گیریم (برای دسته‌بندی درست)
                        _remove_open(0)
                    else:
                        # fallback: آخرین open هرچی بود
                        latest = _latest_open()
                        if latest is not None:
                            prev_start, prev_type = latest
                            match_start = prev_start
                            match_type = stype  # نوع رو از end می‌گیریم
                            _remove_open(prev_type)
                        else:
                            # fallback: آخرین begin دیده‌شده قبل از این end
                            if stype in last_begin_by_type:
                                match_start = last_begin_by_type[stype]
                            elif last_begin_any is not None:
                                match_start = last_begin_any

            else:
                # end با stop_type==0 => wildcard: با آخرین open match
                latest = _latest_open()
                if latest is not None:
                    prev_start, prev_type = latest
                    match_start = prev_start
                    match_type = prev_type
                    _remove_open(prev_type)
                else:
                    match_start = last_begin_any
                    match_type = 0

            if match_start is not None:
                _emit_event(match_type, match_start, end_dt)

        # اگر توقف باز داریم و include_open=True => تا now ببند
        if include_open:
            for stype, st in list(open_by_type.items()):
                _emit_event(stype, st, now)

    # مرتب‌سازی نهایی
    all_events.sort(key=lambda e: (e.resource_id, e.start))
    return all_events


def events_of_line(
    rows: Iterable[Dict[str, Any]],
    line_id: Any,
    include_open: bool = False,
    now: Optional[dt.datetime] = None,
    stop_type_optional_if_zero: bool = True,
) -> List[StopEvent]:
    return [
        e for e in build_events(rows, include_open=include_open, now=now, stop_type_optional_if_zero=stop_type_optional_if_zero)
        if e.resource_id == line_id
    ]


def current_shift_window(now: Optional[dt.datetime] = None):
    if now is None:
        now = dt.datetime.now()
    h = now.hour
    if 7 <= h < 15:
        start = now.replace(hour=7, minute=0, second=0, microsecond=0)
        end = now.replace(hour=15, minute=0, second=0, microsecond=0)
    elif 15 <= h < 23:
        start = now.replace(hour=15, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=0, second=0, microsecond=0)
    else:
        if h >= 23:
            start = now.replace(hour=23, minute=0, second=0, microsecond=0)
            end = (now + dt.timedelta(days=1)).replace(hour=7, minute=0, second=0, microsecond=0)
        else:
            start = (now - dt.timedelta(days=1)).replace(hour=23, minute=0, second=0, microsecond=0)
            end = now.replace(hour=7, minute=0, second=0, microsecond=0)
    return start, end


def _merge_intervals(intervals: List[Tuple[dt.datetime, dt.datetime]]) -> List[Tuple[dt.datetime, dt.datetime]]:
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for a, b in intervals[1:]:
        la, lb = merged[-1]
        if a <= lb:
            merged[-1] = (la, max(lb, b))
        else:
            merged.append((a, b))
    return merged


def downtime_minutes_in_window(
    line_id: Any,
    rows: Iterable[Dict[str, Any]],
    window_start: dt.datetime,
    window_end: dt.datetime,
    now: Optional[dt.datetime] = None,
    stop_type_optional_if_zero: bool = True,
) -> int:
    if now is None:
        now = dt.datetime.now()

    events = events_of_line(
        rows,
        line_id=line_id,
        include_open=True,
        now=now,
        stop_type_optional_if_zero=stop_type_optional_if_zero,
    )

    intervals: List[Tuple[dt.datetime, dt.datetime]] = []
    for e in events:
        if e.end is None:
            continue
        a = max(e.start, window_start)
        b = min(e.end, window_end)
        if b > a:
            intervals.append((a, b))

    merged = _merge_intervals(intervals)
    total_minutes = sum((b - a).total_seconds() / 60.0 for a, b in merged)
    return int(total_minutes)


def downtime_minutes_current_shift(
    line_id: Any,
    rows: Iterable[Dict[str, Any]],
    now: Optional[dt.datetime] = None,
    stop_type_optional_if_zero: bool = True,
) -> int:
    if now is None:
        now = dt.datetime.now()
    s, e = current_shift_window(now)
    return downtime_minutes_in_window(
        line_id=line_id,
        rows=rows,
        window_start=s,
        window_end=e,
        now=now,
        stop_type_optional_if_zero=stop_type_optional_if_zero,
    )

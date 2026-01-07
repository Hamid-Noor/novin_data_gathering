import json
import crud
import datetime
import time
from collections import defaultdict
import downtime_parser as dp


data_types = {
    'id': 0,
    'lineNumber': '',
    'productName': 'بدون محصول',
    'produced': 0,
    'target': 0,
    'downtime': 0,
    'waste': 0,
    'status': ''
}


lineIDs = list(range(1, 12))

production_datas = []

for lineID in lineIDs:
    data = data_types.copy()
    data['id'] = lineID
    data['lineNumber'] = f"IM-{lineID}"
    production_datas.append(data)


def produced_all_data(line_ids):

    try:
        all_produced = crud.read_data_from_txt('data_entered/products.txt')

    except Exception:
        all_produced = []

    produced_by_line = defaultdict(list)
    for d in all_produced:
        rid = d.get('resourceID')
        if rid in line_ids:
            produced_by_line[rid].append(d)

    result_by_line = {}
    for line_id in line_ids:
        try:
            open_pack = crud.read_data_from_txt(
                f"data_entered/open_pack_{line_id}.txt")
        except Exception:
            open_pack = []
        result_by_line[line_id] = open_pack + produced_by_line.get(line_id, [])
    return result_by_line


all_produced = produced_all_data(lineIDs)
filtered_produced = [all_produced[i] for i in lineIDs]

all_products = crud.read_data_from_csv(
    0, 1, filename='filtered_datas/filtered_NewflexProducts.csv')
entered_products = crud.read_data_from_txt(
    'data_entered/product_identifications.txt')

downtimes = crud.read_data_from_txt('data_entered/stops.txt')
wastes = crud.read_data_from_txt('data_entered/wastes.txt')

all_molds = crud.read_data_from_csv(
    0, 1, 2, filename='filtered_datas/filtered_molds.csv')
entered_molds = crud.read_data_from_txt('data_entered/molds.txt')


def filter_data_by_shift(datas):
    filtered = []
    now = datetime.datetime.now()
    current_hour = now.hour
    if 7 <= current_hour < 15:
        start_shift = now.replace(hour=7, minute=0, second=0, microsecond=0)
        end_shift = now.replace(hour=15, minute=0, second=0, microsecond=0)
    elif 15 <= current_hour < 23:
        start_shift = now.replace(hour=15, minute=0, second=0, microsecond=0)
        end_shift = now.replace(hour=23, minute=0, second=0, microsecond=0)
    else:
        if current_hour >= 23:
            start_shift = now.replace(
                hour=23, minute=0, second=0, microsecond=0)
            end_shift = (now + datetime.timedelta(days=1)
                         ).replace(hour=7, minute=0, second=0, microsecond=0)
        else:
            start_shift = (now - datetime.timedelta(days=1)
                           ).replace(hour=23, minute=0, second=0, microsecond=0)
            end_shift = now.replace(hour=7, minute=0, second=0, microsecond=0)
    for data in datas:
        read_datetime = datetime.datetime.strptime(
            data['read_datetime'], '%Y-%m-%d %H:%M:%S.%f')
        if start_shift <= read_datetime <= end_shift:
            filtered.append(data)
    return filtered


def filter_txt_by_line(line_id, datas):
    filtered = []
    for data in datas:
        if data['resourceID'] == line_id:
            filtered.append(data)
    return filtered


def filter_csv_by_line(code, datas, col_index):
    for data in datas[1:]:
        if data[col_index] == str(code):
            return data


def calculate_target(mold_number):
    for i in all_molds:
        if i[0] == str(mold_number):
            cavity = int(i[2])
            cycle = float(i[1])
            target_per_hour = cavity * (3600 / cycle)*8  # 8 hours shift
            return int(target_per_hour)
    return 0


def is_stopped_or_logged_in(line_id, downtimes):
    line_downtimes = filter_txt_by_line(line_id, downtimes)
    is_stopped = False
    is_loggeed_in = True

    if not line_downtimes:
        return is_stopped, is_loggeed_in
    last_downtime = datetime.datetime.strptime(
        line_downtimes[-1]['start_read_datetime'], '%Y-%m-%d %H:%M:%S.%f')
    print(last_downtime,int(line_downtimes[-1]['stop_type']))
    if 'stop_read_datetime' not in line_downtimes[-1] or line_downtimes[-1]['stop_read_datetime'] is None:
        is_stopped = False
    else:
        if int(line_downtimes[-1]['stop_type']) != 60 and int(line_downtimes[-1]['stop_type']) != 61:
            last_uptime = datetime.datetime.strptime(
                line_downtimes[-1]['stop_read_datetime'], '%Y-%m-%d %H:%M:%S.%f')
            is_stopped = last_downtime > last_uptime
            print(last_uptime)
    if is_stopped == True and (int(line_downtimes[-1]['stop_type']) == 60 or int(line_downtimes[-1]['stop_type']) == 61):
        is_loggeed_in = True
    return is_stopped, is_loggeed_in


def status_of_line(isLoggedIn, isStopped, hasMold, hasBehco):
    if not isLoggedIn:
        return 'stop'
    if isStopped:
        return 'off'
    if isLoggedIn and hasBehco and hasMold:
        return 'on'
    return 'stop'


# =====================================================================
# ✅ اضافه شده: ساخت دیتا برای دو تاپیک جدید QC
# =====================================================================

OUT_FILE = "mqtt_payloads.json"

DOWNTIME_CATEGORIES = {
    "برنامه ریزی": [1, 2, 3, 4],
    "تولید":       [6, 7, 8],
    "کنترل کیفیت": [9, 10],
    "نت":          [11, 12, 13, 14],
    "آزمایشگاه":   [15],
    "نامشخص":      [60, 61, 0],  # 0 یعنی unknown
}

WASTE_TABS = {
    1: "ظاهری",
    2: "ابعادی",
    3: "تزریق ناقص",
    4: "راه گاه",
    5: "کلوخه",
    6: "ضرب روی ضرب",
}

# فقط برای ظاهری/ابعادی اگر خواستی دستی تعیین کنی:
# None => auto
# "کیلوگرم" => weight
# "تعداد" => count
WASTE_UNIT_OVERRIDE = {
    1: None,
    2: None,
}


def _merge_intervals(intervals):
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


def qc_downtime_tabs_payload(downtimes, line_ids, now):
    """
    duration/count برای هر دسته در شیفت جاری.
    منطق ساخت event ها از downtime_parser می‌آید (start_read_datetime + قوانین auto-close/fallback).
    """
    shift_start, shift_end = dp.current_shift_window(now)
    labels = [f"IM-{i}" for i in line_ids]

    # ✅ بهینه‌تر: فقط یک بار event ها را بساز
    events = dp.build_events(downtimes, include_open=True, now=now)

    events_by_line = defaultdict(list)
    for e in events:
        events_by_line[e.resource_id].append(e)

    out = {}
    for cat_name, types in DOWNTIME_CATEGORIES.items():
        values = []
        for line_id in line_ids:
            intervals = []
            cnt = 0

            for e in events_by_line.get(line_id, []):
                st = int(e.stop_type or 0)
                if st not in types:
                    continue

                if e.end is None:
                    continue

                a = max(e.start, shift_start)
                b = min(e.end, shift_end)
                if b > a:
                    intervals.append((a, b))
                    cnt += 1

            merged = _merge_intervals(intervals)
            minutes = int(sum((b - a).total_seconds() / 60.0 for a, b in merged))
            values.append({"duration": minutes, "count": cnt})

        out[cat_name] = {"unit": "دقیقه", "labels": labels, "values": values}

    return out


def qc_waste_tabs_payload(wastes, line_ids, now):
    """
    waste دیتا: (value, unitType)
      unitType=1 => تعدادی
      unitType=2 => گرمی
      unitType=0 => بعضی جاها ارسال می‌شود، امن‌ترین رفتار: گرمی حسابش می‌کنیم

    خروجی:
      برای ظاهری/ابعادی unit auto یا override
      برای سایر تب‌ها unit="کیلوگرم" (weight)
    """
    shift_start, shift_end = dp.current_shift_window(now)
    labels = [f"IM-{i}" for i in line_ids]

    # totals[(rid, waste_key)] = [grams_sum, count_sum]
    totals = defaultdict(lambda: [0, 0])

    for r in wastes:
        rid = r.get("resourceID")
        if rid not in line_ids:
            continue

        rd = dp._parse_dt(r.get("read_datetime")) if hasattr(dp, "_parse_dt") else None
        if rd is None:
            # fallback ساده
            try:
                rd = datetime.datetime.strptime(r.get("read_datetime"), "%Y-%m-%d %H:%M:%S.%f")
            except Exception:
                try:
                    rd = datetime.datetime.fromisoformat(r.get("read_datetime"))
                except Exception:
                    rd = None

        if rd is None:
            continue
        if not (shift_start <= rd <= shift_end):
            continue

        w = r.get("waste") or {}
        for k, v in w.items():
            try:
                value, unit_type = v
            except Exception:
                continue

            k = int(k)
            value = int(value or 0)
            unit_type = int(unit_type or 0)

            # 1=count / 2=grams / 0=unknown => treat as grams
            if unit_type == 1:
                totals[(rid, k)][1] += value
            else:
                totals[(rid, k)][0] += value

    out = {}
    for k, tab_name in WASTE_TABS.items():
        # تعیین unit/mode
        if k in (1, 2):
            override = WASTE_UNIT_OVERRIDE.get(k)

            grams_total_all = sum(totals[(line_id, k)][0] for line_id in line_ids)
            count_total_all = sum(totals[(line_id, k)][1] for line_id in line_ids)

            if override in ("کیلوگرم", "تعداد"):
                unit = override
                mode = "weight" if unit == "کیلوگرم" else "count"
            else:
                # auto
                if grams_total_all > 0:
                    unit = "کیلوگرم"
                    mode = "weight"
                elif count_total_all > 0:
                    unit = "تعداد"
                    mode = "count"
                else:
                    unit = "کیلوگرم"
                    mode = "weight"
        else:
            unit = "کیلوگرم"
            mode = "weight"

        values = []
        for line_id in line_ids:
            grams, cnt = totals[(line_id, k)]
            if mode == "count":
                values.append({"count": int(cnt)})
            else:
                values.append({"weight": (grams / 1000.0)})

        out[tab_name] = {"unit": unit, "labels": labels, "values": values}

    return out


def main():
    while True:
        all_produced = produced_all_data(lineIDs)
        filtered_produced = [all_produced[i] for i in lineIDs]
        downtimes = crud.read_data_from_txt('data_entered/stops.txt')
        entered_products = crud.read_data_from_txt(
            'data_entered/product_identifications.txt')
        entered_molds = crud.read_data_from_txt('data_entered/molds.txt')

        # ✅ فقط برای QC
        wastes = crud.read_data_from_txt('data_entered/wastes.txt')

        now = datetime.datetime.now()

        # ==========================
        # ✅ این بخش «دست نخورده» است (تاپیک اول)
        # ==========================
        for line in production_datas:
            line_product = filter_txt_by_line(line['id'], entered_products)
            behco = line_product[-1]['behco'] if len(line_product) > 0 else 0
            mold = filter_txt_by_line(line['id'], entered_molds)
            # last_product = line_product[-1] if len(line_product) > 0 else {}
            isStopped, isLoggedIn = is_stopped_or_logged_in(line['id'], downtimes)
            hasMold = len(mold) > 0
            hasBehco = behco != 0
            status = status_of_line(isLoggedIn, isStopped, hasMold, hasBehco)
            line['status'] = status
            print(line['id'] ,isLoggedIn, isStopped, hasMold, hasBehco)
            if status == 'on':
                line['produced'] = len(filter_data_by_shift(
                    filtered_produced[line['id']-1]))
                line['productName'] = filter_csv_by_line(
                    behco, all_products, 0)[1]
                line['target'] = calculate_target(mold[-1]['mold_barcode'])
            if hasBehco and hasMold:
                line['produced'] = len(filter_data_by_shift(
                    filtered_produced[line['id']-1]))
                line['productName'] = filter_csv_by_line(
                    behco, all_products, 0)[1]
                line['target'] = calculate_target(mold[-1]['mold_barcode'])

            # ✅ downtime با منطق جدید parser (start_read_datetime + auto-close/fallback)
            line['downtime'] = dp.downtime_minutes_current_shift(
                line['id'], downtimes, now=now)

            # print(line)

        with open("test.txt", "w", encoding="utf-8") as f:
            f.write(json.dumps(production_datas, ensure_ascii=False) + "\n")

        # =========================================
        # ✅ فقط اضافه شده: ساخت دو تاپیک جدید QC
        # =========================================
        qc_downtime = qc_downtime_tabs_payload(downtimes, lineIDs, now)
        qc_waste = qc_waste_tabs_payload(wastes, lineIDs, now)

        payloads = {
            "factory/novin/lines/live": production_datas,
            "factory/novin/qualityControl/downtime/live": qc_downtime,
            "factory/novin/qualityControl/nonConformity/live": qc_waste,
        }

        with open(OUT_FILE, "w", encoding="utf-8") as f:
            f.write(json.dumps(payloads, ensure_ascii=False))

        time.sleep(2)


if __name__ == "__main__":
    main()

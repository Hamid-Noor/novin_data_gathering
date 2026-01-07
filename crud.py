import ast
import os
import csv
import re
from typing import Any, Dict, List, Optional


def saveFile(filename, content, next_line='\n'):
    try:
        # بررسی اینکه فایل وجود دارد و در صورت نیاز ایجاد آن
        if not os.path.exists(filename):
            open(filename, 'w').close()
            os.chmod(filename, 0o666)  # تنظیم دسترسی

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content + next_line)
    except PermissionError:
        err = PermissionError
        # print(f"خطا: اجازه دسترسی به {filename} وجود ندارد. لطفاً با `sudo` اجرا کنید.")


def saveHistoryFile(filename, content):
    try:
        # بررسی اینکه فایل وجود دارد و در صورت نیاز ایجاد آن
        if not os.path.exists(filename):
            open(filename, 'w').close()
            os.chmod(filename, 0o666)  # تنظیم دسترسی

        with open(filename, "a", encoding="utf-8") as f:
            f.write(str(content) + '\n')
    except PermissionError:
        err = PermissionError
        # print(f"خطا: اجازه دسترسی به {filename} وجود ندارد. لطفاً با `sudo` اجرا کنید.")


def readFile(filename):
    if os.path.isfile(filename):
        with open(filename, 'r', encoding="utf-8") as f:
            lines = f.readlines()
            return lines
    else:
        return "0"


def read_data_from_csv(*index, filename):
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            data = []
            for row in list(reader):
                lst = []
                for i in index:
                    if i < len(row):
                        if row[i] != '':
                            lst.append(row[i])
                data.append(tuple(lst))
            return data
    except:
        return False


def write_data_to_csv(all_products, newfile_name='filtered_datas/all_newflex_products_behco.csv'):
    with open(newfile_name, 'w', newline='', encoding='utf-8') as newfile:
        writer = csv.writer(newfile)
        writer.writerows(all_products)
        return True
    return False

_unquoted_token_after_colon = re.compile(
    r"(:\s*)([0-9A-Za-z_./-]*[A-Za-z][0-9A-Za-z_./-]*)(\s*[,}])"
)

def safe_eval_dict_line(line: str) -> Optional[Dict[str, Any]]:
    line = line.strip()
    if not line:
        return None

    # تلاش اول
    try:
        obj = ast.literal_eval(line)
        return obj if isinstance(obj, dict) else None
    except Exception:
        pass

    # تلاش دوم: کوتیشن‌دار کردن توکن‌های بدون کوتیشن (که حداقل یک حرف دارند)
    fixed = _unquoted_token_after_colon.sub(r"\1'\2'\3", line)

    try:
        obj = ast.literal_eval(fixed)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None

def read_data_from_txt(filename: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(filename, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            d = safe_eval_dict_line(line)
            if d is None:
                continue
            # اگر خواستی مطمئن کنی pack_barcode همیشه رشته است:
            if "pack_barcode" in d:
                d["pack_barcode"] = str(d["pack_barcode"])
            rows.append(d)
    return rows


# production_per_line_data = {
#     "CompanyID": data.companyId,
#     "LineID": data.line_id,
#     "ReadDateTime": data.ReadDateTime,
#     "packet_id": data.packet_id,
#     "ProductSize": data.ProductSize,
#     "ProductLayer": data.ProductLayer,
#     "ProductType": data.ProductType,
#     "ProductColor": data.ProductColor,
#     "MixMaterial1": data.MixMaterial1,
#     "MixMaterial2": data.MixMaterial2,
#     "MixMaterial3": data.MixMaterial3,
#     "MixPercent1": data.MixPercent1,
#     "MixPercent2": data.MixPercent2,
#     "MixPercent3": data.MixPercent3,
#     "creator": creator,
# }
# # تبدیل به رشته JSON
# production_per_line_json_output = json.dumps(
#     production_per_line_data, ensure_ascii=False, indent=4)
# saveHistoryFile('production_per_line_data_For_DB.txt',
#                 production_per_line_json_output + "#;#")

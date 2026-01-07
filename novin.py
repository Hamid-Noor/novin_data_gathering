from pyModbusTCP.client import ModbusClient
import modules
import validation as val
import save_data as save
import time
import datetime
import threading
import subprocess

# =========================
# ✅ State per line (11 خط)
# =========================
LINE_COUNT = 11

# توقف‌های اپراتوری (start/end)
stop_open = [False for _ in range(LINE_COUNT)]
stop_begin_time = [None for _ in range(LINE_COUNT)]          # start_read_datetime (string)
stop_begin_hmi_time = ["" for _ in range(LINE_COUNT)]        # start_hmi_time (string)
stop_begin_type = [0 for _ in range(LINE_COUNT)]             # stop_type شروع
last_begin_time = [None for _ in range(LINE_COUNT)]          # آخرین شروع دیده‌شده (حتی اگر بسته شد)

# توقف ارتباط (offline)
offline_open = [False for _ in range(LINE_COUNT)]
offline_begin_time = [None for _ in range(LINE_COUNT)]       # start_read_datetime (string)

online_attempts = [0 for i in range(LINE_COUNT)]
all_molds = dict()


def _now_str():
    return str(datetime.datetime.now())


def check_called(client: ModbusClient,
                 companyID,
                 resourceID,
                 read_datetime,
                 online: bool = True,
                 status_address: str = "9.0",
                 user_address: int = 110,
                 action_status_address: int = 21,
                 waste_datas=[{1: 2060, 2: 2062, 3: 2064, 4: 2066,
                               5: 2068, 6: 2070}, {1: "8.3", 2: "8.4"}],
                 stop_address: int = 20,
                 end_stop_address: int = 2010,
                 mold_address: int = 70,
                 current_mold: int = 2110,
                 hmi_time_address: int = 2100,
                 product_identi_address: int = 80,
                 count_address: int = 92,
                 behco_address: int = 94,
                 product_name_address: int = 2120,
                 result_address: int = 6
                 ):
    scan_status = modules.read_bit_from_holding(client, status_address)

    # ❗️اینجا دیگه offline رو لاگ نمی‌کنیم (داخل linesDataGatherer کنترل میشه)
    # چون وقتی دستگاه unreachable هست، read_bit_from_holding ممکنه exception بده.

    if scan_status:
        print('IM-'+str(resourceID))
        print('user checking')
        valid_user, user = check_user(
            client, companyID, resourceID, read_datetime, user_address)
        result = 2
        if valid_user:
            print('user', user)
            action_status = client.read_holding_registers(
                action_status_address)[0]
            if action_status == 5:
                print('product scanning')
                result = 1
            elif action_status == 2:
                print('waste')
                w = waste(client, companyID, resourceID, read_datetime,
                          waste_datas[0], waste_datas[1], user)
                if w:
                    result = 1
                    print('waste added successfully')
            elif action_status == 3:
                print('stop begin')
                s = stop(client, companyID, resourceID, read_datetime, 1,
                         stop_address, hmi_time_address, user, mold_address, current_mold, online)
                if s:
                    result = 1
                    print('stop begin added successfully')
            elif action_status == 4:
                print('stop end')
                s = stop(client, companyID, resourceID, read_datetime, 2,
                         end_stop_address, hmi_time_address, user, mold_address, current_mold, online)
                if s:
                    result = 1
                    print('stop end added successfully')
            elif action_status == 1:
                print('product identification')
                pi = product_identification(
                    client, companyID, resourceID, read_datetime,
                    inp_product_address=product_identi_address,
                    behco_address=behco_address,
                    count_address=count_address,
                    current_mold=current_mold,
                    product_address=product_name_address,
                    user_barcode=user
                )
                if pi:
                    result = 1
                    print('product identification added successfully')
            elif action_status == 7:
                print('connection checking')
                result = 1
        else:
            print('user checking False')

        client.write_single_register(result_address, result)
        modules.write_bit_to_holding(client, status_address, False)
        return True

    return False


def packing_called(client: ModbusClient,
                   companyID,
                   resourceID,
                   read_datetime,
                   scanned_address: int = 10,
                   status_address: str = "50.0",
                   action_status_address: int = 144,
                   user_address: int = 110,
                   behco_address: int = 2012,
                   result_address: int = 140
                   ):
    scan_status = modules.read_bit_from_holding(client, status_address)
    if scan_status:
        print('IM-'+str(resourceID))
        print('user checking')
        valid_user, user = check_user(
            client, companyID, resourceID, read_datetime, user_address)
        result = 3
        if valid_user:
            print('user', user)
            action_status = client.read_holding_registers(
                action_status_address)[0]
            print('status', action_status)
            if action_status == 1:
                print('add product')
                valid_product, is_valid = check_product_barcode(
                    client, companyID, resourceID, read_datetime, scanned_address, behco_address, user)
                if valid_product is True:
                    result = is_valid
                    print('product added successfully')
            elif action_status == 2:
                print('add pack')
                valid_pack, is_valid = check_pack_barcode(
                    client, companyID, resourceID, read_datetime, scanned_address, user)
                if valid_pack is True:
                    result = is_valid
                    print('pack added successfully')
        else:
            print('user checking False')

        client.write_single_register(result_address, result)
        modules.write_bit_to_holding(client, status_address, False)
        return True

    return False


def molds(client: ModbusClient, resourceID, current_mold: int):
    global all_molds
    mold = modules.read_register_32bit_float(client, current_mold)
    mold_barcode = round(mold, 1) if mold else 0
    all_molds[resourceID] = val.validate_mold(mold_barcode)[1]
    return all_molds, mold_barcode


def check_user(client: ModbusClient, companyID, resourceID, read_datetime, user_address: int):
    user_barcode = modules.read_register_32bit_Little_Endian_HK(
        client, user_address)
    validator = val.validate_user(user_barcode)
    if validator == 1:
        save.logins(companyID, resourceID, read_datetime, user_barcode)
        return True, user_barcode
    else:
        return False, user_barcode


def check_mold(client: ModbusClient, companyID, resourceID, read_datetime, mold_address: int, user_barcode: int, current_mold: int):
    _molds = molds(client, resourceID, current_mold)[0]
    global all_molds
    print('mold checking')
    mold = modules.read_register_32bit_float(client, mold_address)
    mold_barcode = round(mold, 1) if mold else None
    validator, mold_behcos = val.validate_mold(mold_barcode)

    if validator == 1:
        save.mold(companyID, resourceID, read_datetime,
                  mold_barcode, user_barcode)
        all_molds[resourceID] = mold_behcos
        return True, mold_barcode
    return False, mold_barcode


def product_identification(client: ModbusClient, companyID, resourceID, read_datetime,
                           inp_product_address: int, behco_address: int, count_address: int,
                           current_mold: int, product_address: int, user_barcode: int):
    product = modules.readInputTextRegisterHolding(
        client, inp_product_address, 8)
    behco = modules.readInputTextRegisterHolding(client, behco_address, 5)
    count = client.read_holding_registers(count_address)
    all_molds = molds(client, resourceID, current_mold)

    print(product, behco, count, all_molds, sep=' | ')
    if str(behco) in all_molds[0][resourceID]:
        validator, name = val.validate_product_identification(
            behco, count, all_molds[1])
    else:
        return False

    product_name = name
    if validator == 1:
        modules.write_persian_text_to_holding(
            client, product_address, product_name.center(50))
        save.product_identification(companyID, resourceID, read_datetime,
                                    behco, count, all_molds[1], product_name, product, user_barcode)
        return True
    return False


def transform_barcode(barcode: str, mode: str):
    def decode_base36(s: str) -> str:
        num = int(s, 36)
        return str(num)[-14:].zfill(14)

    should_transform = False
    labelType = str(barcode[0:1]).upper()
    if mode == "product" and labelType.upper() == "P":
        should_transform = True
        if len(barcode) != 15:
            should_transform = False
    elif mode == "pack":
        return barcode

    if should_transform:
        scannedBarcode1 = decode_base36(str(barcode[1:10]))
        scannedBarcode2 = decode_base36(str(barcode[10:15]))
        num1 = int(scannedBarcode1)
        num2 = int(scannedBarcode2)
        formatted1 = f"{num1:014}"
        formatted2 = f"{num2:07}"
        scannedBarcode = labelType + str(formatted1) + str(formatted2)
        return scannedBarcode

    return False


def check_product_barcode(client: ModbusClient, companyID, resourceID, read_datetime, pruduct_address: int, behco_address: int, user_barcode: int):
    print('product barcode checking')
    behco = modules.readInputTextRegisterHolding(client, behco_address, 5)
    product_base = modules.readInputTextRegisterHolding(
        client, pruduct_address, 10)
    product_transformed = transform_barcode(
        product_base, 'product')
    if product_transformed is not False:
        validator = val.validate_product(product_transformed, behco)
        if validator == 1 and product_transformed is not False:
            is_valid = 1
        elif validator == 3:
            is_valid = 3
        else:
            is_valid = 2
        if is_valid == 1:
            save.products(companyID, resourceID, read_datetime,
                          product_base, product_transformed, user_barcode)
        return True, is_valid
    else:
        is_valid = 3
    return False, is_valid


def check_pack_barcode(client: ModbusClient, companyID, resourceID, read_datetime, pack_address: int, user_barcode: int):
    print('pack barcode checking')
    barcode_base36 = modules.readInputTextRegisterHolding(
        client, pack_address, 10)
    barcode_base10 = transform_barcode(barcode_base36, 'pack')
    if barcode_base10 is not False:
        validator = val.validate_pack(str(barcode_base36))
        if validator == 1 and barcode_base10 is not False:
            is_valid = 1
        elif barcode_base10 is False:
            is_valid = 3
        else:
            is_valid = 2
        if is_valid == 1:
            save.packs(companyID, resourceID, read_datetime,
                       barcode_base36, barcode_base10, user_barcode)
        return True, is_valid
    return False, is_valid


def waste(client: ModbusClient, companyID, resourceID, read_datetime, waste_data: dict, waste_types: dict, user_barcode: int):
    validator = val.validate_QC_confirmation(user_barcode)
    if validator == 1:
        waste = {}
        for i in waste_data:
            w_data = modules.read_register_32bit_Little_Endian_HK(
                client, waste_data[i])
            if i in waste_types:
                w_type = modules.read_bit_from_holding(
                    client, waste_types[i])
                waste[i] = (w_data, int(w_type))
            else:
                waste[i] = (w_data, 0)
        save.wastes(companyID, resourceID,
                    read_datetime, waste, user_barcode)
        return True
    return False


# ==========================================================
# ✅ stop() اصلاح شد:
# - per-line state
# - auto-close روی begin پشت سر هم
# - end بدون begin => last_begin
# - stop_type mismatch => با stop_type شروع (اگر هر دو !=0 و متفاوت)
# ==========================================================
def stop(client: ModbusClient, companyID, resourceID, read_datetime, status: int,
         stop_type_address: int, time_address: int,
         user_barcode: int, mold_number_address: int, current_mold: int, online: bool):

    idx = int(resourceID) - 1
    if idx < 0 or idx >= LINE_COUNT:
        return False

    if not online:
        # offline logging handled in linesDataGatherer (start/end)
        return False

    stop_type = client.read_holding_registers(stop_type_address)[0]
    hmi_parts = client.read_holding_registers(time_address, 3)
    stop_hmi_time = f'{hmi_parts[0]}:{hmi_parts[1]}:{hmi_parts[2]}'

    if status == 1:
        # ---------- BEGIN ----------
        # اگر قبلاً توقف باز داریم، طبق قانون: شروع جدید = پایان قبلی
        if stop_open[idx] and stop_begin_time[idx] is not None:
            prev_start = stop_begin_time[idx]
            prev_type = stop_begin_type[idx]
            prev_hmi = stop_begin_hmi_time[idx] or ""

            # پایان قبلی را با همین read_datetime ببند
            save.stops(companyID, resourceID,
                       prev_start, prev_type, prev_hmi,
                       read_datetime, user_barcode=user_barcode)

        # شروع جدید
        stop_open[idx] = True
        stop_begin_time[idx] = read_datetime
        stop_begin_hmi_time[idx] = stop_hmi_time
        stop_begin_type[idx] = int(stop_type or 0)
        last_begin_time[idx] = read_datetime

        save.stops(companyID, resourceID,
                   read_datetime, stop_type, stop_hmi_time, user_barcode=user_barcode)
        return True

    elif status == 2:
        # ---------- END ----------
        # start_ref را پیدا کن
        if stop_begin_time[idx] is not None:
            start_ref = stop_begin_time[idx]
        elif last_begin_time[idx] is not None:
            start_ref = last_begin_time[idx]
        else:
            # هیچ شروعی نداریم، بدترین حالت: خود همین زمان
            start_ref = read_datetime

        # اگر توقف باز داشتیم ولی stop_type end با stop_type begin نمی‌خونه
        # و هر دو غیرصفرن، نوع را از BEGIN می‌گیریم (برای اینکه دسته‌بندی خراب نشود)
        used_type = int(stop_type or 0)
        if stop_open[idx]:
            btype = int(stop_begin_type[idx] or 0)
            if used_type != 0 and btype != 0 and used_type != btype:
                used_type = btype

        # برای consistency start_hmi_time همون begin اگر داشتیم
        used_hmi = stop_begin_hmi_time[idx] if stop_begin_hmi_time[idx] else stop_hmi_time

        if used_type == 13:
            is_mold_valid, mold_number = check_mold(
                client, companyID, resourceID, read_datetime, mold_number_address, user_barcode, current_mold)
            print(is_mold_valid, mold_number)
            if is_mold_valid is True:
                # توجه: ترتیب پارامترها رو مثل کد خودت نگه داشتم
                save.stops(companyID, resourceID,
                           start_ref, used_type, used_hmi,
                           read_datetime, mold_number, user_barcode)
            else:
                return False
        else:
            save.stops(companyID, resourceID,
                       start_ref, used_type, used_hmi,
                       read_datetime, user_barcode=user_barcode)

        # بستن state
        stop_open[idx] = False
        stop_begin_time[idx] = None
        stop_begin_hmi_time[idx] = ""
        stop_begin_type[idx] = 0

        return True

    return False


def is_device_reachable_windows(ip, timeout=50):
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", str(timeout), ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except Exception:
        print('error connection:', Exception)
        return False


# ==========================================================
# ✅ linesDataGatherer اصلاح شد:
# - offline stop (type=61) را start/end ثبت می‌کند
# - فقط یک بار شروع و یک بار پایان
# ==========================================================
def linesDataGatherer(resourceID, HMI_IP, companyID=49):

    idx = int(resourceID) - 1
    client = ModbusClient(HMI_IP, port=502, timeout=2)

    while True:
        global online_attempts
        now = str(datetime.datetime.now())
        reached = is_device_reachable_windows(HMI_IP)

        if reached:
            # اگر قبلش offline بوده، اینجا offline رو می‌بندیم
            if offline_open[idx] and offline_begin_time[idx] is not None:
                try:
                    save.stops(companyID, resourceID,
                               offline_begin_time[idx], 61, '',
                               now, user_barcode=None)
                except Exception as e:
                    print("error closing offline stop:", e)

                offline_open[idx] = False
                offline_begin_time[idx] = None

            online_attempts[idx] = 0

            try:
                called = check_called(
                    client, companyID, resourceID, now, online=reached)
                if called:
                    print('check_called:', called, '| line number:', resourceID)

                packing = packing_called(client, companyID, resourceID, now)
                if packing:
                    print('packing_called:', packing, '| line number:', resourceID)

                time.sleep(0.5)

            except Exception as x:
                print('error all functions', x, '| line number:', resourceID)

        else:
            online_attempts[idx] += 1

            if online_attempts[idx] == 10 and not offline_open[idx]:
                offline_open[idx] = True
                offline_begin_time[idx] = now
                try:
                    save.stops(companyID, resourceID, now, 61, '')
                except Exception as e:
                    print("error opening offline stop:", e)

            time.sleep(0.5)



# factory_lines = []
# for i in range(10, 21):
#     factory_lines.append((i, f"10.9.41.{i}"))

# if __name__ == "__main__":
#     threads = []
#     for line in factory_lines:
#         t = threading.Thread(target=linesDataGatherer,
#                              args=(line[0]-9, line[1]))
#         threads.append(t)
#         t.start()

# for thread in threads:
#     thread.join()

# تست تک خط:
t = threading.Thread(target=linesDataGatherer, args=(2, '10.17.2.49'))
t.start()
t.join()

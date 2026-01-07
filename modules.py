import datetime
import time
import json
import os
import random
from pyModbusTCP.client import ModbusClient
from datetime import datetime
# from dateutil import parser
import socket
import uuid
import threading
import struct

class LineThreadData:
    def __init__(self):
        self.companyId = 0
        self.ReadDateTime = ''
        self.line_id = 0
        self.packet_id = 0
        self.hostname = '10.15.34.45'
        self.port = 22
        self.username = 'pi'
        self.password = 'raspberry'
        self.file_path = '/home/pi/AzinPacking/L8AvgSpeed.txt'
        self.Line8PackedCount_file_path = '/home/pi/AzinPacking/Line8PackedCount.txt'
        self.Hauloff_controller_state = 0
        self.tvProductionType = ""
        self.NoScrewSpeed = False
        self.tvProductionMaterial = "نام ماده"
        self.NoMaterial = False
        self.NoHauloffSpeed = False
        self.NoThroughputQuality = False
        self.weight_per_meter = 0.0
        self.Current_throughput = 0.0
        self.Mass_consumption_2 = 0.0
        self.LineOutputMeter = 0.0
        self.Current_feedrate = 0.0
        self.Current_RPM = 0.0
        self.productionReportDetailWastages = []
        self.DozingRate1 = -999
        self.DozingRate2 = -999
        self.DozingSpeed1 = -999
        self.DozingSpeed2 = -999
        self.DozingEncode1 = -999
        self.DozingEncode2 = -999
        self.totallineOutputMeter = 0.0
        self.mSDC = []
        self.regCurrentLenght = None
        self.regCutCount = None
        self.regCutSetLenght = None
        self.regCurrentSpeed = None
        self.ProductionOrderDetailId = 0
        self._ProductionHour = 0
        self._ProductionMinutes = 0
        self._wieghtForMeterQC = 0
        self._sumQCWaste = 0
        self._EMCount = 0
        self._QCCallCount = 0
        self._SupervisorCallCount = 0
        self._Waste1 = 0
        self._Waste2 = 0
        self._Waste3 = 0
        self._Waste4 = 0
        self._Waste5 = 0
        self._Waste6 = 0
        self._Waste7 = 0
        self._Waste8 = 0
        self._Waste9 = 0
        self._Waste10 = 0
        self._Waste11 = 0
        self._Waste12 = 0
        self._ResourceFailPlace = 0
        self._ResourceFailType = 0
        self.matWeight = 0
        self.prodWeight = 0
        self.packCount = 0
        self.lineCount = 0
        self.lineSpeed = 0
        self.timespend = 0
        self.LowSpeed = 0
        self.StopLine = 0
        self.NormalSpeedLine = 0
        self.ManualControll = 0
        self.ManualControllCount = 0
        self.ManualControllChanged = 1
        self.NoScrewSpeedTime = 0
        self.NoScrewSpeedCount = 0
        self.NoScrewSpeedChanged = 0
        self.NoMaterialTime = 0
        self.NoMaterialCount = 0
        self.NoMaterialChanged = 0
        self.NoHauloffSpeedTime = 0
        self.NoHauloffSpeedCount = 0
        self.NoHauloffSpeedChanged = 0
        self.NoThroughputQualityTime = 0
        self.NoThroughputQualityCount = 0
        self.NoThroughputQualityChanged = 0
        self.LineAllTempState = "OK"
        self.TempAcceptableDiffrencePercent = 0.15
        self.CutterStopChanged = 0
        self.CutterStopTime = 0
        self.CutterStopCount = 0
        self.CutterUnder4Changed = 0
        self.CutterUnder4Time = 0
        self.CutterUnder4Count = 0
        self.unplannedChanged = 0
        self.unPlannedTime = 0
        self.unPlannedCount = 0
        self.NoScrewSpeedLastTime = 0
        self.NoScrewSpeedFirstTime = 0
        self.ManualControllLastTime = 0
        self.NoMaterialLastTime = 0
        self.NoHauloffSpeedLastTime = 0
        self.NoThroughputQualityLastTime = 0
        self.CutterStopLastTime = 0
        self.CutterUnder4LastTime = 0
        self.unPlannedLastTime = 0
        self.StopLineLastTime = 0
        self.LowSpeedLastTime = 0
        self.NormalSpeedLineLastTime = 0
        self.productedMeterByHour = 0
        self.productedMeterByHourLast = 0
        self.productedMeterByHourLastReadTime = 0
        self.productMeterReference = -999
        self.productMeterCurrent = 0
        self.productMeterTolerance = 0
        self.Mass_consumption_1 = 0
        self.LinerSpeedList1 = []
        self.LinerSpeedList2 = []
        self.VaccumList1 = []
        self.VaccumList2 = []
        self.pipe_temp_list = []
        self.L8LineSpeedList = []
        self.Vaccum1_Temp = -999
        self.Vaccum2_Temp = -999
        self.AmbientTemp = -999
        self.Air_Pressure = -999
        self.Vaccum1_Pressure = -999
        self.Vaccum2_Pressure = -999
        self.Pipe_Temperature = -999
        self.Water_Tank = -999
        self.Inlet_Water = -999
        self.Outlet_Water = -999
        self.Liner1Speed = -999
        self.Liner2Speed = -999
        self.Mould1Temp = -999
        self.Mould2Temp = -999
        self.Mould3Temp = -999
        self.Mould4Temp = -999
        self.Mould5Temp = -999
        self.Mould6Temp = -999
        self.Zone1Temp = -999
        self.Zone2Temp = -999
        self.Zone3Temp = -999
        self.Zone4Temp = -999
        self.Zone5Temp = -999
        self.ThroatTemp = -999
        self.BlueLinerMouldTemp = -999
        self.BlueLinerZone1Temp = -999
        self.BlueLinerZone2Temp = -999
        self.RedLinerMouldTemp = -999
        self.RedLinerZone1Temp = -999
        self.RedLinerZone2Temp = -999
        self.Mould1TempSet = -999
        self.Mould2TempSet = -999
        self.Mould3TempSet = -999
        self.Mould4TempSet = -999
        self.Mould5TempSet = -999
        self.Mould6TempSet = -999
        self.Zone1TempSet = -999
        self.Zone2TempSet = -999
        self.Zone3TempSet = -999
        self.Zone4TempSet = -999
        self.Zone5TempSet = -999
        self.ThroatTempSet = -999
        self.BlueLinerMouldTempSet = -999
        self.BlueLinerZone1TempSet = -999
        self.BlueLinerZone2TempSet = -999
        self.RedLinerMouldTempSet = -999
        self.RedLinerZone1TempSet = -999
        self.RedLinerZone2TempSet = -999
        self.CT1 = -999
        self.CT2 = -999
        self.CT3 = -999
        self.Motor_Speed = -999
        self.Screw_Speed = -999
        self.FlowMeter = -999
        self.opcconnectionerror = ""
        self.SupervisorId = 0
        self.QCSupervisorId = 0
        self.PackingSupervisorId = 0
        self.LineOperatorId = 0
        self.StopStartDate = None
        self.ProductionStopStartDate = None
        self.ProductionStopStartDate1 = None
        self.ProductionStopStartDate2 = None
        self.ProductionStopStartDate3 = None
        self.ProductionStopStartDate4 = None
        self.ProductionStopStartDate5 = None
        self.ProductionStopStartDate6 = None
        self.ProductionStopStartDate7 = None
        self.ProductionStopStartDate8 = None
        self.ProductionStopStartDate9 = None
        self.ProductionStopStartDate10 = None
        self.ProductionStopStartDate11 = None
        self.ProductionStopStartDate12 = None
        self.ProductionStopStartDate13 = None
        self.ProductionStopStartDate14 = None
        self.QCHmi = None
        self.ProductionHmi = None
        self.ProductSize = 0
        self.ProductLayer = 0
        self.ProductType = 0
        self.ProductColor = 0
        self.MixMaterial1 = 0
        self.MixMaterial2 = 0
        self.MixMaterial3 = 0
        self.MixPercent1 = 0
        self.MixPercent2 = 0
        self.MixPercent3 = 0
        self.lastVisionDataGet = ''
        self.mesagging_loginToken = ''
        self.mesagging_fullName = ''
        self.mesagging_userId = 0

def read_register_32bit_float_all(client, address):
    regs = client.read_holding_registers(address, 2)
    if not (isinstance(regs, (list, tuple)) and len(regs) == 2):
        return None
    
    results = {}
    # حالت‌های مختلف word و byte order
    combos = [
        ("big", "high"),
        ("big", "low"),
        ("little", "high"),
        ("little", "low"),
    ]
    
    for byteorder, wordorder in combos:
        if wordorder == "high":
            raw = (regs[0] << 16) | regs[1]
        else:
            raw = (regs[1] << 16) | regs[0]
        
        if byteorder == "big":
            value = struct.unpack('>f', struct.pack('>I', raw))[0]
        else:
            value = struct.unpack('<f', struct.pack('<I', raw))[0]
        
        results[f"{byteorder}-{wordorder}"] = value
    
    return results


def read_register_32bit_float(client, address, byteorder="big", wordorder="low"):
    # خواندن دو رجیستر 16 بیتی
    regs = client.read_holding_registers(address, 2)
    
    if isinstance(regs, (list, tuple)) and len(regs) == 2:
        # ترتیب word ها (بعضی دستگاه‌ها low word اول می‌فرستن)
        if wordorder == "high":
            raw = (regs[0] << 16) | regs[1]
        else:
            raw = (regs[1] << 16) | regs[0]
        
        # تبدیل به float با توجه به ترتیب بایت‌ها
        if byteorder == "big":
            value = struct.unpack('>f', struct.pack('>I', raw))[0]
        else:
            value = struct.unpack('<f', struct.pack('<I', raw))[0]
        
        return value
    else:
        return None

def parse_bit_address(address_str):
    """تبدیل رشته مثل '40.4' به (رجیستر، بیت) → (40, 4)"""
    parts = address_str.strip().split('.')
    if len(parts) != 2:
        raise ValueError("آدرس نامعتبر است. باید به صورت 'رجیستر.بیت' باشد.")
    return int(parts[0]), int(parts[1])

def read_bit_from_holding(client, address_str):
    """
    خواندن بیت خاص از یک رجیستر Holding (مثل 40.4)
    """
    reg_addr, bit_index = parse_bit_address(address_str)
##    print(reg_addr)
    regs = client.read_holding_registers(reg_addr, 1)
##    print(regs)
    if regs:
        value = (regs[0] >> bit_index) & 1
        return bool(value)
    return None

def write_bit_to_holding(client, address_str, bit_value: bool):
    """
    نوشتن روی یک بیت خاص از رجیستر Holding (مثل 40.4)
    """
    reg_addr, bit_index = parse_bit_address(address_str)
    regs = client.read_holding_registers(reg_addr, 1)
    if not regs:
        return False
    current_value = regs[0]
    
    if bit_value:
        new_value = current_value | (1 << bit_index)
    else:
        new_value = current_value & ~(1 << bit_index)

    return client.write_multiple_registers(reg_addr, [new_value])


def read_m_as_byte(client,address):
    """
    مقدار کامل 1 بایتی از آدرس مربوط به M40 رو به صورت عدد صحیح برمی‌گردونه.
    فرض: M40 به صورت رجیستر Holding در آدرس 40 مپ شده.
    """
    regs = client.read_holding_registers(address, 1)
    if regs:
        return regs[0] & 0x00FF  # فقط 8 بیت پایین رو می‌گیریم
    return None


def read_m40_bits(client):
    """
    خواندن بایت M40 (بیت‌های M40.0 تا M40.7) از Coil 400 تا 407
    """
    start_address = 720  # فرض: M40.0 → 400
    result = client.read_coils(start_address, 8)
    if result and len(result) == 8:
        return {
            f"M40.{i}": bit for i, bit in enumerate(result)
        }
    return None


def read_m_bit(client, bit_index):
    """
    خواندن بیت از محدوده‌ی حافظه‌ی Coil (مثلاً M50.0 تا M50.7 → آدرس‌های 4050 تا 4057)
    """
    base_address = 4000  # فرضی؛ بسته به تنظیمات PLC باید اصلاح شود
    coil_address = base_address + bit_index  # مثلاً M50.0 → 4050، M50.1 → 4051
    result = client.read_coils(coil_address, 1)
    if result:
        return result[0]
    return None

def read_m_bit_all(client, m_address):
    """خواندن بیت از محدوده‌ی Coils در Modbus معادل Mx.x بیت‌های PLC"""
    result = client.read_coils(m_address, 1)
    if result:
        return result[0]
    return None

def read_register_32bit_HW(client, address):
    regs = client.read_input_registers(address)  # خواندن دو رجیستر 16 بیتی
    if len(regs) >= 1:
        return regs[0]
    return regs

def read_register_32bit_Little_Endian_HW(client, address):
    regs = client.read_input_registers(address, 2)  # خواندن دو رجیستر 16 بیتی
    if regs and len(regs) == 2:
        data_bytes = struct.pack("<HH", regs[0], regs[1])  # little-endian
        return struct.unpack("<I", data_bytes)[0]  # تبدیل به مقدار 32 بیتی بدون علامت
    return None  # در صورت عدم موفقیت در خواندن

def read_register_32bit_HK(client, address):
    regs = client.read_holding_registers(address)  # خواندن دو رجیستر 16 بیتی
    if len(regs) >= 1:
        return regs[0]
    return regs

def read_register_32bit_Single_HK(client, address):
    regs = client.read_holding_registers(address)  # خواندن دو رجیستر 16 بیتی
    if len(regs) >= 1:
        return regs[0]
    else:
        return regs

def read_register_32bit_Little_Endian_HK(client, address):
    regs = client.read_holding_registers(address, 2)  # خواندن دو رجیستر 16 بیتی
    if regs and len(regs) == 2:
        data_bytes = struct.pack("<HH", regs[0], regs[1])  # little-endian
        return struct.unpack("<I", data_bytes)[0]  # تبدیل به مقدار 32 بیتی بدون علامت
    return None  # در صورت عدم موفقیت در خواندن

def write_register_32bit_little_endian_HW(client: ModbusClient, address: int) -> bool:
    """Writes a 32-bit little-endian zero value to a Modbus register."""
    try:
        data_bytes = struct.pack("<I", 0)  # مقدار 0 به‌صورت Little Endian
        regs = struct.unpack("<HH", data_bytes)  # تبدیل به دو مقدار 16 بیتی
        client.write_multiple_registers(address, list(regs))  # استفاده از متد صحیح
        return True
    except Exception as e:
        print(f"خطا در نوشتن رجیسترها: {e}")
    return False  # مقدار False در صورت شکست عملیات

def read_register_32bit_DWord_HK(client, address):
    regs = client.read_holding_registers(address, 2)  # خواندن دو رجیستر 16 بیتی
    if isinstance(regs, (list, tuple)) and len(regs) >= 2:
        high = regs[0]
        low = regs[1]
        dword = (high << 16) | low  # ترکیب به صورت DWORD
        return dword
    return None

def readInputTextRegister(client,address,bitcount):
    response = client.read_input_registers(address, bitcount)
    if response:
        # تبدیل داده‌ها به بایت با ترتیب **Little-Endian**
        data_le = b''.join(struct.pack("<H", x) for x in response)
##        print(data_le)
        # حذف کاراکترهای `NULL` و فضاهای اضافی
        if data_le[0:1] == b'\x00':
            return ""
        cleaned_data = data_le.rstrip(b"\x00").rstrip(b"\x9e").decode("utf8", errors="ignore").strip()
        #print(data_le[0:1])
        if cleaned_data is None:
            return ""
        return cleaned_data
    return None

def readInputTextRegisterHolding(client,address,bitcount):
    response = client.read_holding_registers(address, bitcount)
    if response:
        # تبدیل داده‌ها به بایت با ترتیب **Little-Endian**
        data_le = b''.join(struct.pack("<H", x) for x in response)
##        print(data_le)
        # حذف کاراکترهای `NULL` و فضاهای اضافی
        if data_le[0:1] == b'\x00':
            return ""
        cleaned_data = data_le.rstrip(b"\x00").rstrip(b"\x9e").decode("utf8", errors="ignore").strip()
        #print(data_le[0:1])
        if cleaned_data is None:
            return ""
        return cleaned_data
    return None

def read_delta_m_register(client, m_address):
    """
    خواندن مقدار رجیستر M از HMI دلتا (Modbus TCP/RTU)
    """
    regs = client.read_holding_registers(m_address, 1)
    if regs:
        return regs[0]
    return None

def try_read_m6(client):
    for addr in [6, 40006, 40005]:
        try:
            val = client.read_holding_registers(addr, 1)
            print(f"Holding Register {addr} →", val[0] if val else "⛔️ خوانده نشد")
        except Exception as e:
            print(f"🔴 خطا برای آدرس {addr}: {e}")

    # تست به صورت بیت (Coil)
    try:
        val = client.read_coils(6, 1)
        print("Coil 6 →", val[0] if val else "⛔️ خوانده نشد")
    except Exception as e:
        print(f"🔴 خطا در خواندن Coil 6: {e}")

def try_read_m_variable(client, base_address=6):
    try:
        coil = client.read_coils(base_address, 1)
        print(f"🔹 Coil[{base_address}]:", coil[0] if coil else "❌")
    except:
        print("❌ Coil Read Error")

    try:
        reg = client.read_holding_registers(base_address, 1)
        print(f"🔹 Holding[{base_address}]:", reg[0] if reg else "❌")
    except:
        print("❌ Holding Read Error")

def generate_codes(base_str, count):
    if not base_str.isdigit():
        raise ValueError("کد پایه باید فقط شامل اعداد باشد.")
    
    codes = []
    for i in range(1, count + 1):
        suffix = f"{i:03d}"  # سه رقم با صفرهای پیشوندی
        full_code = base_str + suffix
        codes.append(full_code)
    
    return codes


def write_persian_text_to_holding(client, start_address, text):
    """
    ارسال متن فارسی به PLC از طریق رجیسترهای Holding با استفاده از UTF-16LE
    هر رجیستر 16 بیتی → 2 بایت
    """
    # تبدیل متن به بایت‌های UTF-16LE
    encoded_bytes = text.encode('UTF-8')
    #encoded_bytes = text.encode('UTF-16LE')

    # تقسیم بایت‌ها به رجیسترهای 16 بیتی
    registers = []
    for i in range(0, len(encoded_bytes), 2):
        if i + 1 < len(encoded_bytes):
            reg = encoded_bytes[i] | (encoded_bytes[i + 1] << 8)
        else:
            reg = encoded_bytes[i]  # اگر تعداد بایت فرد باشد
        registers.append(reg)

    # نوشتن در رجیسترهای Holding
    success = client.write_multiple_registers(start_address, registers)
    return success

def read_persian_text_from_holding(client, start_address, length):
    """
    خواندن متن فارسی از رجیسترهای Holding
    length: تعداد کاراکترهای مورد انتظار (هر کاراکتر → 2 بایت → 1 رجیستر)
    """
    regs = client.read_holding_registers(start_address, length)
    if not regs:
        return None

    # تبدیل رجیسترها به بایت‌ها
    byte_array = bytearray()
    for reg in regs:
        byte_array.append(reg & 0xFF)
        byte_array.append((reg >> 8) & 0xFF)

    # تبدیل بایت‌ها به رشته‌ی UTF-16LE
    try:
        #return byte_array.decode('UTF-16LE')
        return byte_array.decode('UTF-8')
    except UnicodeDecodeError:
        return None

def read_persian_text_from_input(client, start_address, length):
    """
    خواندن متن فارسی از رجیسترهای Input
    length: تعداد رجیسترهایی که باید خوانده شوند (هر رجیستر → 2 بایت)
    """
    regs = client.read_input_registers(start_address, length)
    if not regs:
        return None

    # تبدیل رجیسترها به بایت‌ها
    byte_array = bytearray()
    for reg in regs:
        byte_array.append(reg & 0xFF)
        byte_array.append((reg >> 8) & 0xFF)

    # تبدیل بایت‌ها به رشته‌ی UTF-16LE
    try:
        #return byte_array.decode('UTF-16LE')
        return byte_array.decode('UTF-8')
    except UnicodeDecodeError:
        return None

def read_register_64bit_Little_Endian_HK(client, address):
    regs = client.read_holding_registers(address, 4)  # خواندن چهار رجیستر 16 بیتی
    if regs and len(regs) == 4:
        data_bytes = struct.pack("<HHHH", regs[0], regs[1], regs[2], regs[3])  # little-endian
        return struct.unpack("<Q", data_bytes)[0]  # تبدیل به مقدار 64 بیتی بدون علامت
    return None  # در صورت عدم موفقیت در خواندن

def read_register_32bit_Single_HK(client, address):
    regs = client.read_holding_registers(address)  # خواندن دو رجیستر 16 بیتی
    if isinstance(regs, (list, tuple)) and len(regs) >= 1:
        return regs[0]
    else:
        return regs
    
# نمونه استفاده
##base_code = "11122532030417087"  # قسمت ثابت کد بدون سه رقم پایانی
##repeat_count = 10
##new_codes = generate_codes(base_code, repeat_count)

##for code in new_codes:
##    print("کد جدید:", code)
# from opcua import Client
# import json

# def normalize_global_key(key: str) -> str:
#     if key.startswith("Global > "):
#         key = key.replace("Global > ", "")
#     return key.replace(" ", "")

# def read_global_values(plc_address: str):
#     plcClient = Client("opc.tcp://" + plc_address + ":4840")
#     plcClient.connect()

#     global_nodes = {
#         "Global > Water Pressure": "ns=4;i=3001",
#         "Global > Air Pressure": "ns=4;i=3002",
#         "Global > Inlet Chilled Water Temperature": "ns=4;i=3003",
#         "Global > Outlet Chilled Water Temperature": "ns=4;i=3004",
#         "Global > Inlet Cooling Tower Water Temperature": "ns=4;i=3005",
#         "Global > Outlet Cooling Tower Water Temperature": "ns=4;i=3006",
#         "Global > Ambient Temperature": "ns=4;i=3007"
#     }

#     results = {}
#     for name, node_id in global_nodes.items():
#         try:
#             node = plcClient.get_node(node_id)
#             results[normalize_global_key(name)] = node.get_value()
#         except Exception as e:
#             print(f"⚠️ خطا در خواندن {name}: {e}")
#             results[normalize_global_key(name)] = None

#     plcClient.disconnect()

#     plc_global_json = json.dumps(results, ensure_ascii=False, indent=4)
# ##    saveHistoryFile("plc_global_data.txt", plc_global_json + "#;#")
#     print(plc_global_json)

#     return results

# StopStartDate = 5556
# LineNumber = 1

# QCHmi = ModbusClient(host="10.15.34.57", port=502, unit_id=1, auto_open=True) ## For Sarem

##print(f'2180 : {read_register_32bit_Little_Endian_HK(QCHmi, 2180)}')
##t = time.time()
##data = LineThreadData()
####data.QCHmi = ModbusClient("10.15.34.44", port=502, unit_id=1, timeout=0.01)
##data.ProductionHmi = ModbusClient("10.15.34.57", port=502, unit_id=1, timeout=0.01)
##timespend = time.time() - t
##t = time.time()
##data.companyId = 2
##data.line_id = 2
##data.ReadDateTime = str(datetime.today())
##data.packet_id = data.packet_id + 1
##
##line_id = 2
##while True:
##    # saveHistoryFile('stopFaultCode.txt', str(stopFaultCode) + "#;#" + str(LineNumber))
##    stopFaultCode = read_register_32bit_Single_HK(data.ProductionHmi, 2040 + int(LineNumber))
##    if not stopFaultCode is None and int(stopFaultCode) > 0:
##        personelCode = read_register_32bit_Little_Endian_HK(data.ProductionHmi, 2500 + (2 * (int(LineNumber) - 1)))
##        # lastReg = int(LineNumber) * 3
##        # stopFaultHour = read_register_32bit_Single_HK(data.ProductionHmi,119 + (lastReg - 2))
##        # stopFaultMinute = read_register_32bit_Single_HK(data.ProductionHmi,119 + (lastReg - 1))
##        # stopFaultSecond = read_register_32bit_Single_HK(data.ProductionHmi, 119 + lastReg)
##        stopFaultHour = read_register_32bit_Single_HK(data.ProductionHmi, 2300 + int(LineNumber))
##        stopFaultMinute = read_register_32bit_Single_HK(data.ProductionHmi, 2320 + int(LineNumber))
##        stopFaultSecond = read_register_32bit_Single_HK(data.ProductionHmi, 2340 + int(LineNumber))
##        netStopFaultCode = 0
##        netHasStopLine = 0
##        if int(stopFaultCode) < 14:
##            netStopFaultCode = read_register_32bit_Single_HK(data.ProductionHmi, 2210 + int(LineNumber))
##            netHasStopLine = read_register_32bit_Single_HK(data.ProductionHmi, 2230 + int(LineNumber))
##        # def createStopForMISServiceModelList(_ProductionReportDetailId,_StoppingReasonId,_StopFromTime,_StopToTime,_StopTime,_Description):
##        stopFromTimeStart = str(stopFaultHour) + ":" + str(stopFaultMinute) + ":" + str(stopFaultSecond)
##        finishStop = read_register_32bit_Single_HK(data.ProductionHmi, 2250 + int(LineNumber))
##        ProductionStopStartDate = None
##        if int(LineNumber) == 1:
##            ProductionStopStartDate = data.ProductionStopStartDate1
##        elif int(LineNumber) == 2 :
##            ProductionStopStartDate = data.ProductionStopStartDate2
##        elif int(LineNumber) == 3 :
##            ProductionStopStartDate = data.ProductionStopStartDate3
##        elif int(LineNumber) == 4 :
##            ProductionStopStartDate = data.ProductionStopStartDate4
##        elif int(LineNumber) == 5 :
##            ProductionStopStartDate = data.ProductionStopStartDate5
##        elif int(LineNumber) == 6 :
##            ProductionStopStartDate = data.ProductionStopStartDate6
##        elif int(LineNumber) == 7 :
##            ProductionStopStartDate = data.ProductionStopStartDate7
##        elif int(LineNumber) == 8 :
##            ProductionStopStartDate = data.ProductionStopStartDate8
##        elif int(LineNumber) == 9 :
##            ProductionStopStartDate = data.ProductionStopStartDate9
##        elif int(LineNumber) == 10 :
##            ProductionStopStartDate = data.ProductionStopStartDate10
##        elif int(LineNumber) == 11 :
##            ProductionStopStartDate = data.ProductionStopStartDate11
##        elif int(LineNumber) == 12 :
##            ProductionStopStartDate = data.ProductionStopStartDate12
##        elif int(LineNumber) == 13 :
##            ProductionStopStartDate = data.ProductionStopStartDate13
##        elif int(LineNumber) == 14 :
##            ProductionStopStartDate = data.ProductionStopStartDate14
##
##        print(f'ProductionStopStartDate : {ProductionStopStartDate}')
##        if ProductionStopStartDate is None or finishStop == 2:
##            ProductionStopStartDate = str(datetime.now())
##            if int(LineNumber) == 1 :
##                data.ProductionStopStartDate1 = ProductionStopStartDate
##            elif int(LineNumber) == 2 :
##                data.ProductionStopStartDate2 = ProductionStopStartDate
##            elif int(LineNumber) == 3 :
##                data.ProductionStopStartDate3 = ProductionStopStartDate
##            elif int(LineNumber) == 4 :
##                data.ProductionStopStartDate4 = ProductionStopStartDate
##            elif int(LineNumber) == 5 :
##                data.ProductionStopStartDate5 = ProductionStopStartDate
##            elif int(LineNumber) == 6 :
##                data.ProductionStopStartDate6 = ProductionStopStartDate
##            elif int(LineNumber) == 7 :
##                data.ProductionStopStartDate7 = ProductionStopStartDate
##            elif int(LineNumber) == 8 :
##                data.ProductionStopStartDate8 = ProductionStopStartDate
##            elif int(LineNumber) == 9 :
##                data.ProductionStopStartDate9 = ProductionStopStartDate
##            elif int(LineNumber) == 10 :
##                data.ProductionStopStartDate10 = ProductionStopStartDate
##            elif int(LineNumber) == 11 :
##                data.ProductionStopStartDate11 = ProductionStopStartDate
##            elif int(LineNumber) == 12 :
##                data.ProductionStopStartDate12 = ProductionStopStartDate
##            elif int(LineNumber) == 13 :
##                data.ProductionStopStartDate13 = ProductionStopStartDate
##            elif int(LineNumber) == 14 :
##                data.ProductionStopStartDate14 = ProductionStopStartDate
##            stopping_data = {
##                "CompanyID": data.companyId,
##                "LineID": line_id,
##                "ReadDateTime": data.ReadDateTime,
##                "packet_id": data.packet_id,
##                "StopFaultCode": stopFaultCode,
##                "StartPersonelCode": personelCode,
##                "StopTimeStart": stopFromTimeStart,
##                "StopFaultHour": stopFaultHour,
##                "StopFaultMinute": stopFaultMinute,
##                "StopFaultSecond": stopFaultSecond,
##                "NetStopFaultCode": netStopFaultCode,
##                "NetHasStopLine": netHasStopLine,
##                "FinishedPersonelCode": 0,
##                "finishedDateTime": "",
##                "startDateTime": ProductionStopStartDate,
##            }
##            # تبدیل به رشته JSON
##            stopping_json_output = json.dumps(stopping_data, ensure_ascii=False, indent=4)
##    ##        saveHistoryFile('stopping_data_For_DB.txt', stopping_json_output + "#;#")
##            print(f'stopping_json_output : {stopping_json_output}')
##            data.ProductionHmi.write_multiple_registers(2250 + int(LineNumber),[0])
##            if int(stopFaultCode) < 14:
##                ErrTitle = ''
##                ErrPartTitle = ''
##                if int(stopFaultCode) == 1:
##                    ErrTitle = 'اکسترودر'
##                elif int(stopFaultCode) == 2:
##                    ErrTitle = 'خط زن'
##                elif int(stopFaultCode) == 3:
##                    ErrTitle = 'قالب'
##                elif int(stopFaultCode) == 4:
##                    ErrTitle = 'دوزینگ'
##                elif int(stopFaultCode) == 5:
##                    ErrTitle = 'وکیوم'
##                elif int(stopFaultCode) == 6:
##                    ErrTitle = 'کشنده'
##                elif int(stopFaultCode) == 7:
##                    ErrTitle = 'کاتر'
##                elif int(stopFaultCode) == 8:
##                    ErrTitle = 'گراویمتر'
##                elif int(stopFaultCode) == 9:
##                    ErrTitle = 'پرینتر'
##                elif int(stopFaultCode) == 10:
##                    ErrTitle = 'بسته بندی'
##                elif int(stopFaultCode) == 11:
##                    ErrTitle = 'ویژن'
##                elif int(stopFaultCode) == 12:
##                    ErrTitle = 'اولتراسونیک'
##                elif int(stopFaultCode) == 13:
##                    ErrTitle = 'هاپر'
##                
##                if int(netStopFaultCode) == 1:
##                    ErrPartTitle = 'برق'
##                elif int(netStopFaultCode) == 2:
##                    ErrPartTitle = 'مکانیک'
##                elif int(netStopFaultCode) == 3:
##                    ErrPartTitle = 'تاسیسات'
##                elif int(netStopFaultCode) == 4:
##                    ErrPartTitle = 'آماده سازی'
##                # netMessage = f'برای خط MN{LineNumber} خطای {ErrPartTitle} روی زیرتجهیز {ErrTitle} ثبت گردید.'
##                netMessage = ''
##                netMessage += f'ثبت توقف نت\n'
##                netMessage += f'MN{LineNumber}\n'
##                netMessage += f'زیرتجهیز : {ErrTitle}\n'
##                netMessage += f'خطا : {ErrPartTitle}\n'
##                LoginSMS(data)
##                result = SendMessage(
##                    token=data.mesagging_loginToken,
##                    full_name=data.mesagging_fullName,
##                    user_id=data.mesagging_userId,
##                    mobiles=["09135924955", "09133103892"],
##                    message=netMessage
##                )
##                
##        finishedPersonelCode = 0
##        finishedDateTime = ""
##        if finishStop == 1:
##            # time.sleep(1)
##            finishedDateTime = str(datetime.now())
##            finishedPersonelCode = read_register_32bit_Single_HK(data.ProductionHmi, 2530 + (2 * (int(LineNumber) - 1)))
##            data.ProductionHmi.write_multiple_registers(2250 + int(LineNumber),[0])
##            data.ProductionHmi.write_multiple_registers(2040 + int(LineNumber),[0])
##            data.ProductionHmi.write_multiple_registers(2160 + int(LineNumber),[0])
##            data.ProductionHmi.write_multiple_registers(2300 + int(LineNumber),[0])
##            data.ProductionHmi.write_multiple_registers(2320 + int(LineNumber),[0])
##            data.ProductionHmi.write_multiple_registers(2340 + int(LineNumber),[0])
##            # data.ProductionHmi.write_multiple_registers(119 + (lastReg - 2),[0])
##            # data.ProductionHmi.write_multiple_registers(119 + (lastReg - 1),[0])
##            # data.ProductionHmi.write_multiple_registers(119 + (lastReg),[0])
##            data.ProductionHmi.write_multiple_registers(2210 + int(LineNumber),[0])
##            data.ProductionHmi.write_multiple_registers(2230 + int(LineNumber),[0])
##            data.ProductionHmi.write_multiple_registers(2360 + int(LineNumber),[0])
##            # data.ProductionHmi.write_multiple_registers(32,[0])
##            stopping_data = {
##                "CompanyID": data.companyId,
##                "LineID": line_id,
##                "ReadDateTime": data.ReadDateTime,
##                "packet_id": data.packet_id,
##                "StopFaultCode": stopFaultCode,
##                "StartPersonelCode": personelCode,
##                "StopTimeStart": stopFromTimeStart,
##                "StopFaultHour": stopFaultHour,
##                "StopFaultMinute": stopFaultMinute,
##                "StopFaultSecond": stopFaultSecond,
##                "NetStopFaultCode": netStopFaultCode,
##                "NetHasStopLine": netHasStopLine,
##                "FinishedPersonelCode": finishedPersonelCode,
##                "finishedDateTime": finishedDateTime,
##                "startDateTime": ProductionStopStartDate,
##            }
##            if int(LineNumber) == 1 :
##                data.ProductionStopStartDate1 = None
##            elif int(LineNumber) == 2 :
##                data.ProductionStopStartDate2 = None
##            elif int(LineNumber) == 3 :
##                data.ProductionStopStartDate3 = None
##            elif int(LineNumber) == 4 :
##                data.ProductionStopStartDate4 = None
##            elif int(LineNumber) == 5 :
##                data.ProductionStopStartDate5 = None
##            elif int(LineNumber) == 6 :
##                data.ProductionStopStartDate6 = None
##            elif int(LineNumber) == 7 :
##                data.ProductionStopStartDate7 = None
##            elif int(LineNumber) == 8 :
##                data.ProductionStopStartDate8 = None
##            elif int(LineNumber) == 9 :
##                data.ProductionStopStartDate9 = None
##            elif int(LineNumber) == 10 :
##                data.ProductionStopStartDate10 = None
##            elif int(LineNumber) == 11 :
##                data.ProductionStopStartDate11 = None
##            elif int(LineNumber) == 12 :
##                data.ProductionStopStartDate12 = None
##            elif int(LineNumber) == 13 :
##                data.ProductionStopStartDate13 = None
##            elif int(LineNumber) == 14 :
##                data.ProductionStopStartDate14 = None
##            # تبدیل به رشته JSON
##            stopping_json_output = json.dumps(stopping_data, ensure_ascii=False, indent=4)
##            print(f'stopping_json_output : {stopping_json_output}')
##    time.sleep(2)

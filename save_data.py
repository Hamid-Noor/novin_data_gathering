import crud


def logins(companyID, resourceID, read_datetime, user_barcode):
    crud.saveHistoryFile("data_entered/logins.txt", {'companyID': companyID, 'resourceID': resourceID,
                         'read_datetime': read_datetime, "user_barcode": user_barcode})
    return True


def mold(companyID, resourceID, read_datetime, user_barcode, mold_barcode):
    crud.saveHistoryFile("data_entered/molds.txt", {'companyID': companyID, 'resourceID': resourceID,
                         'read_datetime': read_datetime, "mold_barcode": mold_barcode, "user_barcode": user_barcode})
    return True


def product_identification(companyID, resourceID, read_datetime, behco, count, mold_number, product_name, product, user_barcode):
    crud.saveHistoryFile("data_entered/product_identifications.txt", {"companyID": companyID, "resourceID": resourceID, "read_datetime": read_datetime, "behco": behco,
                                                         "count": count, "mold_number": mold_number, "product_name": product_name, "product": product, "user_barcode": user_barcode})
    return True


def products(companyID, resourceID, read_datetime, product_base, product_transformed, user_barcode, pack_barcode='' ):
    crud.saveHistoryFile("data_entered/product_barcodes.txt", product_transformed)
    crud.saveHistoryFile(f"data_entered/open_pack_{resourceID}.txt", {'companyID': companyID, 'resourceID': resourceID,
                         'read_datetime': read_datetime,
                                           'barcode_base36': product_base, 'barcode_base10': product_transformed, 'pack_barcode': pack_barcode , "user_barcode": user_barcode})
    return True


def packs(companyID, resourceID, read_datetime, barcode_base36, barcode_base10, user_barcode):
    crud.saveHistoryFile("data_entered/packs.txt", {"companyID": companyID, "resourceID": resourceID,
                         "read_datetime": read_datetime, "barcode_base36": barcode_base36, "barcode_base10": barcode_base10, "user_barcode": user_barcode})
    crud.saveHistoryFile("data_entered/pack_barcodes.txt", barcode_base10)
    products = crud.readFile(f"data_entered/open_pack_{resourceID}.txt")
    for i in products:
        line = i[:-1].replace("''", f'"{barcode_base36}"')
        crud.saveHistoryFile("data_entered/products.txt", line)
    crud.saveFile(f"data_entered/open_pack_{resourceID}.txt", '', '')
    return True


def wastes(companyID, resourceID, read_datetime, waste, user_barcode):
    crud.saveHistoryFile("data_entered/wastes.txt", {
                         "companyID": companyID, "resourceID": resourceID, "read_datetime": read_datetime, "waste": waste, "user_barcode": user_barcode})
    return True


def stops(companyID, resourceID, start_read_datetime, stop_type, stop_begin_hmi_time, stop_read_datetime=None, user_barcode=None, mold_number=None):
    crud.saveHistoryFile("data_entered/stops.txt", {
                         "companyID": companyID, "resourceID": resourceID, "start_read_datetime": start_read_datetime, "stop_type": stop_type, "start_hmi_time": stop_begin_hmi_time, "stop_read_datetime": stop_read_datetime, "personal_barcode": user_barcode, "mold_number": mold_number})
    return True

def logout(companyID, resourceID, read_datetime, user_barcode):
    crud.saveHistoryFile("data_entered/logouts.txt", {'companyID': companyID, 'resourceID': resourceID,
                         'read_datetime': read_datetime, "user_barcode": user_barcode})
    return True

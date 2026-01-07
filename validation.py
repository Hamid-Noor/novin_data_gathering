import crud


def check_len(char, min=1, max=6):
    if max >= len(str(char)) >= min:
        return True
    return False


def validate_user(barcode):
    if check_len(barcode):
        return 1
    return 2


def validate_mold(mold_number):
    if check_len(mold_number, max=9):
        molds = crud.read_data_from_csv(3, 6, 2, 4, 5, filename='base_datas/molds.csv')
        new_file = 'filtered_datas/filtered_molds.csv'
        crud.write_data_to_csv(molds, new_file)
        filtered_molds = crud.read_data_from_csv(
            0, 1, 2, 3, 4, filename=new_file)
        for i in filtered_molds:
            if str(mold_number) == str(i[0]):
                return 1, i[3:]
    return 2, []


def validate_product_identification(behco, count, mold_number):
    products_all_datas = crud.read_data_from_csv(
        1, 2, filename='base_datas/NewflexProducts.csv')
    newfile = "filtered_datas/filtered_NewflexProducts.csv"
    crud.write_data_to_csv(products_all_datas, newfile)
    if check_len(behco, max=9) and check_len(count[0], max=4) and check_len(mold_number, max=8):
        for i in products_all_datas:
            if str(behco) == i[0]:
                return 1, i[1]
    return 2, " "


def is_repeated(barcode, file):
    products = crud.readFile(file)
    for i in products:
        if str(barcode).lower() in str(i).lower():
            return True
    return False


def validate_product(barcode, behco):
    if check_len(barcode, max=23):
        product_code = None
        mapped_data = crud.read_data_from_csv(
            0, 1, filename='base_datas/product_mapping.csv')
        for i in mapped_data:
            if i[0] == str(behco):
                product_code = i[1]
                break
        if str(barcode[5:9]) == product_code:
            if is_repeated(barcode, "data_entered/product_barcodes.txt") == True:
                return 2
            else:
                return 1
    return 3


def validate_pack(barcode):
    if check_len(barcode, max=50):
        if is_repeated(barcode, "data_entered/pack_barcodes.txt") == True:
            return 2
        else:
            return 1
    return 3


def validate_QC_confirmation(barcode):
    # if True:
    #     return 1
    # return 2
    barcode= barcode
    return 1

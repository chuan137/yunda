# -*- coding: utf-8 -*-
from xlrd import open_workbook
import types

_bianhao_clumn = {
    'bianhao':0,
    }
_parcel_column = {    
    'ref':1,
    'sender_name':2,
    'sender_company':3,
    'sender_street':4,
    'sender_hause_number':5,
    'sender_add':6,
    'sender_postcode':7,
    'sender_city':8,
    'sender_tel':9,
    
    'receiver_name':10,
    'receiver_company':11,
    'receiver_province':12,
    'receiver_city':13,
    'receiver_district':14,
    'receiver_address':15,
    'receiver_postcode':16,
    'receiver_mobile':17,
    
    'weight_kg':18,
    'length_cm':19,
    'width_cm':20,
    'height_cm':21,
            }
_goodsdetail_column = {
    'description':22,
    'cn_customs_tax_catalog_name':23,
    'cn_customs_tax_name':24,
    'qty':25,
    'item_net_weight_kg':26,
    'item_price_eur':27,
            }

def get_parcel_infos_from_excel(excel_binary):
    try:
        excel = open_workbook(file_contents=excel_binary)
        asheet = excel.sheet_by_index(0)
    
        # 读取包裹信息
        parcel_infos = {}
        parcel_errors = []
        for current_row in range(3, asheet.nrows):
            if not asheet.cell(current_row, _bianhao_clumn['bianhao']).value: break
            d_bianhao, dinfo, derrors = _get_a_goods_detail_info(asheet, current_row)
            if d_bianhao in parcel_infos.keys():
                parcel_infos[d_bianhao]['goodsdetails'].append(dinfo)
                if derrors:
                    parcel_errors.append(derrors)
                    
            else:            
                p_bianhao, pinfo, perrors = _get_a_parcel_info(asheet, current_row)
                parcel_infos[d_bianhao] = pinfo
                parcel_infos[d_bianhao]['goodsdetails']=[dinfo]
                if derrors:
                    parcel_errors.append(derrors)
                if perrors:
                    parcel_errors.append(perrors)
        return parcel_infos,parcel_errors
    except:
        return False,False

def trimString(value):
    if type(value) is types.UnicodeType:
        return value.strip()
    else:
        return str(value).strip()

def _get_a_goods_detail_info(asheet, row_no):
    errors = {}
    dinfos = {}
    # # bianhao    
    val, error = _get_int_value('bianhao', _bianhao_clumn, asheet, row_no)
    if error:
        errors['bianhao'] = ["输入数据有误。"]
    else:
        if val:
            bianhao = val
        else:
            errors['bianhao'] = ["输入数据不能为空。"]
    
    # # description
    val, error = _get_text_value('description', _goodsdetail_column, asheet, row_no)
    if error:
        errors['description'] = ["输入数据有误。"]
    else:
        dinfos['description'] = val
    
    # # cn_customs_tax_catalog_name
    val, error = _get_text_value('cn_customs_tax_catalog_name', _goodsdetail_column, asheet, row_no)
    if error:
        errors['cn_customs_tax_catalog_name'] = ["输入数据有误。"]
    else:
        dinfos['cn_customs_tax_catalog_name'] = val
    
    # # cn_customs_tax_name
    val, error = _get_text_value('cn_customs_tax_name', _goodsdetail_column, asheet, row_no)
    if error:
        errors['cn_customs_tax_name'] = ["输入数据有误。"]
    else:
        dinfos['cn_customs_tax_name'] = val
    
    # # qty
    val, error = _get_int_value('qty', _goodsdetail_column, asheet, row_no)
    if error:
        errors['qty'] = ["输入数据有误。"]
    else:
        dinfos['qty'] = val
    
    # # item_net_weight_kg
    val, error = _get_float_value('item_net_weight_kg', _goodsdetail_column, asheet, row_no)
    if error:
        errors['item_net_weight_kg'] = ["输入数据有误。"]
    else:
        dinfos['item_net_weight_kg'] = val
    
    # # item_price_eur
    val, error = _get_float_value('item_price_eur', _goodsdetail_column, asheet, row_no)
    if error:
        errors['item_price_eur'] = ["输入数据有误。"]
    else:
        dinfos['item_price_eur'] = val
    
    dinfos['row_no'] = row_no + 1
    if errors:
        return bianhao,dinfos,{'row_no':row_no + 1,
                               'errors':errors}
    else:
        return bianhao, dinfos, False

def _get_int_value(field_name, column_numbers, asheet, row_no):
    try:
        val = asheet.cell(row_no, column_numbers[field_name]).value
        if type(val) is types.FloatType:
            val = str(int(val))
        val = trimString(val)
        return val, False
    except:
        return '', True

def _get_text_value(field_name, column_numbers, asheet, row_no):
    try:
        val = asheet.cell(row_no, column_numbers[field_name]).value
        val = trimString(val)
        return val, False
    except:
        return '', True

def _get_float_value(field_name, column_numbers, asheet, row_no):
    try:
        val = asheet.cell(row_no, column_numbers[field_name]).value
        if type(val) is types.FloatType:
            val = str(val)
        val = trimString(val)
        val.replace(',', '.')
        return val, False
    except:
        return '', True
    

def _get_a_parcel_info(asheet, row_no): 
    errors = {}
    pinfos = {}
    # # bianhao    
    val, error = _get_int_value('bianhao', _bianhao_clumn, asheet, row_no)
    if error:
        errors['bianhao'] = ["输入数据有误。"]
    else:
        if val:
            bianhao = val
        else:
            errors['bianhao'] = ["输入数据不能为空。"]
    
    # # ref
    val, error = _get_int_value('ref', _parcel_column, asheet, row_no)
    if error:
        errors['ref'] = ["输入数据有误。"]
    else:
        pinfos['ref'] = val
    # # sender_name
    val, error = _get_text_value('sender_name', _parcel_column, asheet, row_no)
    if error:
        errors['sender_name'] = ["输入数据有误。"]
    else:
        pinfos['sender_name'] = val
    
    # # sender_company
    val, error = _get_text_value('sender_company', _parcel_column, asheet, row_no)
    if error:
        errors['sender_company'] = ["输入数据有误。"]
    else:
        pinfos['sender_company'] = val
    
    # # sender_street
    val, error = _get_text_value('sender_street', _parcel_column, asheet, row_no)
    if error:
        errors['sender_street'] = ["输入数据有误。"]
    else:
        pinfos['sender_street'] = val
        
    # # sender_hause_number
    val, error = _get_int_value('sender_hause_number', _parcel_column, asheet, row_no)
    if error:
        errors['sender_hause_number'] = ["输入数据有误。"]
    else:
        pinfos['sender_hause_number'] = val
    
    # # sender_add
    val, error = _get_text_value('sender_add', _parcel_column, asheet, row_no)
    if error:
        errors['sender_add'] = ["输入数据有误。"]
    else:
        pinfos['sender_add'] = val
    
    # # sender_postcode
    val, error = _get_int_value('sender_postcode', _parcel_column, asheet, row_no)
    if error:
        errors['sender_postcode'] = ["输入数据有误。"]
    else:
        pinfos['sender_postcode'] = val
    
    # # sender_city
    val, error = _get_text_value('sender_city', _parcel_column, asheet, row_no)
    if error:
        errors['sender_city'] = ["输入数据有误。"]
    else:
        pinfos['sender_city'] = val
        
    # # sender_tel
    val, error = _get_int_value('sender_tel', _parcel_column, asheet, row_no)
    if error:
        errors['sender_tel'] = ["输入数据有误。"]
    else:
        pinfos['sender_tel'] = val
        
    # # receiver_name
    val, error = _get_text_value('receiver_name', _parcel_column, asheet, row_no)
    if error:
        errors['receiver_name'] = ["输入数据有误。"]
    else:
        pinfos['receiver_name'] = val
        
    # # receiver_company
    val, error = _get_text_value('receiver_company', _parcel_column, asheet, row_no)
    if error:
        errors['receiver_company'] = ["输入数据有误。"]
    else:
        pinfos['receiver_company'] = val
        
    # # receiver_province
    val, error = _get_text_value('receiver_province', _parcel_column, asheet, row_no)
    if error:
        errors['receiver_province'] = ["输入数据有误。"]
    else:
        pinfos['receiver_province'] = val
        
    # # receiver_city
    val, error = _get_text_value('receiver_city', _parcel_column, asheet, row_no)
    if error:
        errors['receiver_city'] = ["输入数据有误。"]
    else:
        pinfos['receiver_city'] = val
        
    # # receiver_district
    val, error = _get_text_value('receiver_district', _parcel_column, asheet, row_no)
    if error:
        errors['receiver_district'] = ["输入数据有误。"]
    else:
        pinfos['receiver_district'] = val
        
    # # receiver_address
    val, error = _get_text_value('receiver_address', _parcel_column, asheet, row_no)
    if error:
        errors['receiver_address'] = ["输入数据有误。"]
    else:
        pinfos['receiver_address'] = val
    
    # # receiver_postcode
    val, error = _get_int_value('receiver_postcode', _parcel_column, asheet, row_no)
    if error:
        errors['receiver_postcode'] = ["输入数据有误。"]
    else:
        pinfos['receiver_postcode'] = val
        
    # # receiver_mobile
    val, error = _get_int_value('receiver_mobile', _parcel_column, asheet, row_no)
    if error:
        errors['receiver_mobile'] = ["输入数据有误。"]
    else:
        pinfos['receiver_mobile'] = val
        
    # # weight_kg
    val, error = _get_float_value('weight_kg', _parcel_column, asheet, row_no)
    if error:
        errors['weight_kg'] = ["输入数据有误。"]
    else:
        pinfos['weight_kg'] = val
        
    # # length_cm
    val, error = _get_float_value('length_cm', _parcel_column, asheet, row_no)
    if error:
        errors['length_cm'] = ["输入数据有误。"]
    else:
        pinfos['length_cm'] = val
    
    # # width_cm
    val, error = _get_float_value('width_cm', _parcel_column, asheet, row_no)
    if error:
        errors['width_cm'] = ["输入数据有误。"]
    else:
        pinfos['width_cm'] = val
    
    # # height_cm
    val, error = _get_float_value('height_cm', _parcel_column, asheet, row_no)
    if error:
        errors['height_cm'] = ["输入数据有误。"]
    else:
        pinfos['height_cm'] = val
        
        
#     try:   
#         bianhao = asheet.cell(row_no, _moban_column['bianhao']).value
#         if type(bianhao) is types.FloatType:
#             bianhao = str(int(bianhao))
#         bianhao = trimString(bianhao)
#         if not bianhao:
#             errors['bianhao'] = ["输入数据不能为空。"]
#         else:
#             pinfos['bianhao'] = bianhao
#     except:
#         errors['bianhao'] = ["输入数据有误。"]
#     # # /bianhao
#     
#     # # sender_name
#     try:   
#         bianhao = asheet.cell(row_no, _moban_column['sender_name']).value
#         if type(bianhao) is types.FloatType:
#             bianhao = str(int(bianhao))
#         bianhao = trimString(bianhao)
#         if not bianhao:
#             errors['bianhao'] = ["输入数据不能为空。"]
#         else:
#             pinfos['bianhao'] = bianhao
#     except:
#         errors['bianhao'] = ["输入数据有误。"]
#     
#     # # /sender_name
#     
#     sender_hause_number = asheet.cell(row_no, _moban_column['sender_hause_number']).value
#     if type(sender_hause_number) is types.FloatType:
#         sender_hause_number = int(sender_hause_number)
#         
#     sender_postcode = asheet.cell(row_no, _moban_column['sender_postcode']).value
#     if type(sender_postcode) is types.FloatType:
#         sender_postcode = int(sender_postcode)
#         
#     sender_tel = asheet.cell(row_no, _moban_column['sender_tel']).value
#     if type(sender_tel) is types.FloatType:
#         sender_tel = int(sender_tel)
#         
#     receiver_postcode = asheet.cell(row_no, _moban_column['receiver_postcode']).value
#     if type(receiver_postcode) is types.FloatType:
#         receiver_postcode = int(receiver_postcode)
#         
#     receiver_mobile = asheet.cell(row_no, _moban_column['receiver_mobile']).value
#     if type(receiver_mobile) is types.FloatType:
#         receiver_mobile = int(receiver_mobile)
#         
#         
#     ref = asheet.cell(row_no, _moban_column['ref']).value
#     if type(ref) is types.FloatType:
#         ref = int(ref)
#         
#     pinfo = {
#         'ref':ref,
#         'sender_name':asheet.cell(row_no, _moban_column['sender_name']).value,
#         'sender_company':asheet.cell(row_no, _moban_column['sender_company']).value,
#         'sender_street':asheet.cell(row_no, _moban_column['sender_street']).value,
#         'sender_hause_number':sender_hause_number,
#         'sender_add':asheet.cell(row_no, _moban_column['sender_add']).value,
#         'sender_postcode':sender_postcode,
#         'sender_city':asheet.cell(row_no, _moban_column['sender_city']).value,
#         'sender_tel':sender_tel,
#         
#         'receiver_name':asheet.cell(row_no, _moban_column['receiver_name']).value,
#         'receiver_company':asheet.cell(row_no, _moban_column['receiver_company']).value,
#         'receiver_province':asheet.cell(row_no, _moban_column['receiver_province']).value,
#         'receiver_city':asheet.cell(row_no, _moban_column['receiver_city']).value,
#         'receiver_district':asheet.cell(row_no, _moban_column['receiver_district']).value,
#         'receiver_address':asheet.cell(row_no, _moban_column['receiver_address']).value,
#         'receiver_postcode':receiver_postcode,
#         'receiver_mobile':receiver_mobile,
#         
#         'weight_kg':asheet.cell(row_no, _moban_column['weight_kg']).value,
#         'length_cm':asheet.cell(row_no, _moban_column['length_cm']).value,
#         'width_cm':asheet.cell(row_no, _moban_column['width_cm']).value,
#         'height_cm':asheet.cell(row_no, _moban_column['height_cm']).value,
#         }
#     for key in pinfo.keys():
#         pinfo[key] = trimString(pinfo[key])
#     pinfo['weight_kg'] = pinfo['weight_kg'].replace(',', '.')
#     pinfo['length_cm'] = pinfo['weight_kg'].replace(',', '.')
#     pinfo['width_cm'] = pinfo['weight_kg'].replace(',', '.')
#     pinfo['height_cm'] = pinfo['weight_kg'].replace(',', '.')
    pinfos['row_no'] = row_no + 1
    if errors:
        return bianhao,pinfos,{'row_no':row_no + 1,
                               'errors':errors}
    else:
        return bianhao, pinfos, False




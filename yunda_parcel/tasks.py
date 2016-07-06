#from celery import task
from django.shortcuts import  get_object_or_404

from yunda_parcel import models as parcel_models

from django.conf import settings
import xmlrpclib
import pytz
from datetime import datetime

import logging
logger = logging.getLogger('yunda.django.async')

#@task
def intl_parcel_sync_to_erp(parcel):
    
    parcel.sync_status = 'waiting_to_sync'
    parcel.save()
    
    # TODO sync 
    
    url = getattr(settings, 'ODOO_URL', 'localhost:8069')
    username = getattr(settings, 'ODOO_USERNAME', '')
    password = getattr(settings, 'ODOO_PASSWORD', '')
    db = getattr(settings, 'ODOO_DB', '')
    company_code = getattr(settings, 'ODOO_COMPANY_CODE', 'de-kuaidi')
    common = xmlrpclib.ServerProxy('%s/xmlrpc/2/common' % url)
    uid = common.authenticate(db, username, password, {})
    models = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % url)
    detail_infos = []
    
    try:
        for detail in parcel.details.all():
            detail_infos.append({
                'description': detail.description,
                'cn_name':detail.cn_customs_tax.cn_name,
                'cn_custom_number':detail.cn_customs_tax.cn_custom_number,
                'hs_code':detail.cn_customs_tax.hs_code,
                'tax_rate':detail.cn_customs_tax.tax_rate,
                'standard_unit_price_cny':detail.cn_customs_tax.standard_unit_price_cny,
                'charge_by_weight':detail.cn_customs_tax.charge_by_weight,
                'qty':int(detail.qty),
                'item_net_weight_kg':detail.item_net_weight_kg,
                'item_price_eur':detail.item_price_eur,
                'original_country':detail.original_country or 'DE',
                                 })
        id = models.execute_kw(db, uid, password, 'yunda2.zhuanyun.yuanxiangshanyun', 'create', [{
            'sender_name':parcel.sender_name,
            'sender_name2':parcel.sender_name2 or "",
            'sender_company':parcel.sender_company or "",
            'sender_state':parcel.sender_state or "",
            'sender_city':parcel.sender_city or "",
            'sender_postcode':parcel.sender_postcode or "",
            'sender_street':parcel.sender_street or "",
            'sender_add':parcel.sender_add or "",
            'sender_hause_number':parcel.sender_hause_number or "",
            'sender_tel':parcel.sender_tel or "",
            'sender_email':parcel.sender_email or "",
            'sender_country':parcel.sender_country or "",
            
            'receiver_name':parcel.receiver_name or "",
            'receiver_company':parcel.receiver_company or "",
            'receiver_province':parcel.receiver_province or "",
            'receiver_city':parcel.receiver_city or "",
            'receiver_district':parcel.receiver_district or "",
            'receiver_postcode':parcel.receiver_postcode or "",
            'receiver_address':parcel.receiver_address or "",
            'receiver_address2':parcel.receiver_address2 or "",
            'receiver_mobile':parcel.receiver_mobile or "",
            'receiver_email':parcel.receiver_email or "",
            'receiver_country':parcel.receiver_country or "",
            
            
            'ref':parcel.ref or "",
        
            'weight_kg':parcel.weight_kg or 0.01,
            'length_cm':parcel.length_cm or 1,
            'width_cm':parcel.width_cm or 1,
            'height_cm':parcel.height_cm or 1,
            
            'start_price_eur':parcel.start_price_eur or 10,
            'start_weight_kg':parcel.start_weight_kg or 1,
            'continuing_price_eur':parcel.continuing_price_eur or 2.5,
            'continuing_weight_kg':parcel.continuing_weight_kg or 0.5,
            'volume_weight_rate':parcel.volume_weight_rate or 6000,
            
            'currency_type':"eur",
            
            'yde_number':parcel.yde_number or "",
            'created_at':parcel.created_at or "",
            'printed_at':parcel.printed_at or "",
            'sender_pay_cn_customs':parcel.sender_pay_cn_customs or False,
            'fee_paid_eur':parcel.fee_paid_eur or 0,
            'state':"validated",
            'customer_number':parcel.user.userprofile.customer_number,
            'company_code':company_code,
            
            'detail_infos':detail_infos,
            }])
        logger.info('Intl parcel synced to erp')
        parcel.sync_status = 'synced'
        parcel.save()
    except Exception as e:
        logger.error(e)
        parcel.sync_status = 'error'
        parcel.save()

    return u'%s synced to erp' % parcel.yde_number

#@task
def get_history_from_erp():
    logger.debug("cron called")
    local_tz = getattr(settings, 'TIME_ZONE', 'Asia/Shanghai')
    local = pytz.timezone(local_tz)
#     local_dt=local.localize(messenge.created_at, is_dst=None)
#     utc_dt=local_dt.astimezone(pytz.utc)
    url = getattr(settings, 'ODOO_URL', 'localhost:8069')
    username = getattr(settings, 'ODOO_USERNAME', '')
    password = getattr(settings, 'ODOO_PASSWORD', '')
    db = getattr(settings, 'ODOO_DB', '')
    common = xmlrpclib.ServerProxy('%s/xmlrpc/2/common' % url)
    uid = common.authenticate(db, username, password, {})
    models = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % url)
    
    
    try:
        histories = models.execute_kw(db, uid, password,
                                 'yunda2.zhuanyun.history',
                                 'get_histories',
                                 [])
        print histories;
        
#         for history in histories:
#             yuanxiangshanyun = get_object_or_404(yuanxiangshanyun_models.YuanXiangShanYunTask, yde_number=history['yde_number'])
#             dt = datetime.strptime(history['created_at'], "%Y-%m-%d %H:%M:%S")
#             utc_dt = pytz.utc.localize(dt, is_dst=None)
#             
#             obj = yuanxiangshanyun_models.History(zhuanyun_task=yuanxiangshanyun,
#                                     created_at=utc_dt.astimezone(local),
#                                     description=history['description'],)
#             obj.save()            
#         
#             logger.debug('yuanxiangshanyun history synced from erp')
        
    except Exception as e:
        logger.error(e)

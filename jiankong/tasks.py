# -*- coding: utf-8 -*-
from celery import task
from jiankong.models import IntlParcelJiankong
from parcel.tools import tracking_fetch
from jiankong import settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('django')

@task
def do_jiankong_gss_v2(start, end):
    result = 0
    mail_nos = []
    for jk in IntlParcelJiankong.objects.filter(type_code__icontains='yd', finished_jiankong=False)[start:end]:
        mail_nos.append({'mail_no':jk.tracking_number})
    if len(mail_nos) < 1:
        raise Exception('No mail numbers')
    try:
        trackings = tracking_fetch(mail_nos)
        if len(trackings) < 1:
            raise Exception("No scan info feched")
        for tracking in trackings:
            try:
                jk = IntlParcelJiankong.objects.get(tracking_number=tracking['tracking_number'])
                scan_infos = tracking['scan_infos']
                status = jk.status
                if not jk.opc_arrived_at:
                    dt = _search_texts_in_scan_info(settings.OPC_ARRIVED_MARKS, scan_infos)
                    if dt:
                        jk.opc_arrived_at = dt
                        status = "opc_arrived"
                
                if not jk.opc_export_ready_at:
                    dt = _search_texts_in_scan_info(settings.OPC_EXPORT_READY_MARKS, scan_infos)
                    if dt:
                        jk.opc_export_ready_at = dt
                        status = "opc_export_ready"
                
                if not jk.opc_export_customs_finished_at:
                    dt = _search_texts_in_scan_info(settings.OPC_EXPORT_CUSTOMS_FINISHED_MARKS, scan_infos)
                    if dt:
                        jk.opc_export_customs_finished_at = dt
                        status = "opc_export_customs_finished"
                        
                if not jk.opc_flied_at:
                    dt = _search_texts_in_scan_info(settings.OPC_FLIED_MARKS, scan_infos)
                    if dt:
                        jk.opc_flied_at = dt
                        status = "opc_flied"
                
                if not jk.destination_country_arrived_at:
                    dt = _search_texts_in_scan_info(settings.DESTINATION_COUNTRY_ARRIVED_MARKS, scan_infos)
                    if dt:
                        jk.destination_country_arrived_at = dt
                        status = "destination_country_arrived"
                        
                if not jk.import_customs_finished_at:
                    dt = _search_texts_in_scan_info(settings.IMPORT_CUSTOMS_FINISHED_MARKS, scan_infos)
                    if dt:
                        jk.import_customs_finished_at = dt
                        status = "import_customs_finished"
                        
                if not jk.local_opc_received_at:
                    dt = _get_first_time_in_destination_country(scan_infos)
                    if dt:
                        jk.local_opc_received_at = dt
                        status = "local_opc_received"
                        
                if not jk.delivery_staff_asigned_at:
                    dt = _search_all_texts_in_scan_info(settings.DELIVERY_STAFF_ASIGNED_MARKS, scan_infos)
                    if dt:
                        jk.delivery_staff_asigned_at = dt
                        status = "delivery_staff_asigned"
                        
                if not jk.deliveried_at:
                    dt = _search_texts_in_scan_info(settings.DELIVERIED_MARKS, scan_infos)
                    if dt:
                        jk.deliveried_at = dt
                        status = "deliveried"
                        jk.finished_jiankong = True
                
                if status == "local_opc_received":
                    jk.newest_datetime = datetime.strptime(scan_infos[0]['time'], '%Y-%m-%d %H:%M:%S')
                jk.status = status
                jk.last_checked_at = datetime.now()
                jk.save()
                
                ######################
                # check if problem
                #####################
                now = datetime.now()
                now = datetime(now.year, now.month, now.day)
                days_delayed = 0
                if jk.status == "delivery_staff_asigned":
                    jkdt = datetime(jk.delivery_staff_asigned_at.year, jk.delivery_staff_asigned_at.month, jk.delivery_staff_asigned_at.day)
                    dt = now - timedelta(days=settings.STATUSES['delivery_staff_asigned'])
                    if jkdt < dt:
                        days_delayed = (now - jkdt).days
                        
                elif jk.status == "local_opc_received":
                    jkdt = datetime(jk.newest_datetime.year, jk.newest_datetime.month, jk.newest_datetime.day)
                    dt = now - timedelta(days=settings.STATUSES['local_opc_received'])
                    if jkdt < dt:
                        days_delayed = (now - jkdt).days
                         
                elif jk.status == "import_customs_finished":
                    jkdt = datetime(jk.import_customs_finished_at.year, jk.import_customs_finished_at.month, jk.import_customs_finished_at.day)
                    dt = now - timedelta(days=settings.STATUSES['import_customs_finished'])
                    if jkdt < dt:
                        days_delayed = (now - jkdt).days
                 
                elif jk.status == "destination_country_arrived":
                    jkdt = datetime(jk.destination_country_arrived_at.year, jk.destination_country_arrived_at.month, jk.destination_country_arrived_at.day)
                    dt = now - timedelta(days=settings.STATUSES['destination_country_arrived'])
                    if jkdt < dt:
                        days_delayed = (now - jkdt).days
                         
                elif jk.status == "opc_flied":
                    jkdt = datetime(jk.opc_flied_at.year, jk.opc_flied_at.month, jk.opc_flied_at.day)
                    dt = now - timedelta(days=settings.STATUSES['opc_flied'])                 
                    if jkdt < dt:
                        days_delayed = (now - jkdt).days
                    
                elif jk.status == "opc_export_customs_finished":
                    jkdt = datetime(jk.opc_export_customs_finished_at.year, jk.opc_export_customs_finished_at.month, jk.opc_export_customs_finished_at.day)
                    dt = now - timedelta(days=settings.STATUSES['opc_export_customs_finished'])                 
                    if jkdt < dt:
                        days_delayed = (now - jkdt).days
                                         
                elif jk.status == "opc_export_ready":
                    jkdt = datetime(jk.opc_export_ready_at.year, jk.opc_export_ready_at.month, jk.opc_export_ready_at.day)
                    dt = now - timedelta(days=settings.STATUSES['opc_export_ready'])
                    if jkdt < dt:
                        days_delayed = (now - jkdt).days
                    
                elif jk.status == "opc_arrived":
                    jkdt = datetime(jk.opc_arrived_at.year, jk.opc_arrived_at.month, jk.opc_arrived_at.day)
                    dt = now - timedelta(days=settings.STATUSES['opc_arrived'])                
                    if jkdt < dt:
                        days_delayed = (now - jkdt).days
                      
                elif jk.status == "created":
                    jkdt = datetime(jk.created_at.year, jk.created_at.month, jk.created_at.day)
                    dt = now - timedelta(days=settings.STATUSES['created'])
                    if jkdt < dt:
                        days_delayed = (now - jkdt).days
                jk.days_delayed=days_delayed
                jk.save()
                # #end 
                
            except IntlParcelJiankong.DoesNotExist:
                logger.error("do jiankong:feched tracking number does not exist")
            except IntlParcelJiankong.MultipleObjectsReturned:
                logger.error('do_jiankong: feched tracking number duplicated')
            except Exception as e:
                logger.error("[do_jiankong_gss__after_tracking_fethed]" + e)
        # return result
    except Exception as e:
        logger.error("[do_jiankong_gss]" + e)

def _search_texts_in_scan_info(texts, scan_infos):
    for text in texts:
        for scan_info in scan_infos:
            if text in scan_info['remark']:
                return datetime.strptime(scan_info['time'], '%Y-%m-%d %H:%M:%S')
    return False

def _search_all_texts_in_scan_info(texts, scan_infos):
    for scan_info in scan_infos:
        if (texts[0] in scan_info['remark']) and (texts[1] in scan_info['remark']):
            return datetime.strptime(scan_info['time'], '%Y-%m-%d %H:%M:%S')
    return False

def _get_first_time_in_destination_country(scan_infos):
    for scan_info in scan_infos:
        if scan_info['remark'][:5] in settings.LOCAL_OPC_RECEIVED_MARKS:
            return datetime.strptime(scan_info['time'], '%Y-%m-%d %H:%M:%S')
    return False

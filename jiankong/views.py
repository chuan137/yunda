# -*- coding: utf-8 -*-
from django.shortcuts import render
from yunda_commen.decorators import json_response
from userena.decorators import secure_required
from django.contrib.admin.views.decorators import staff_member_required
from parcel.models import IntlParcel, Mawb
from jiankong.models import IntlParcelJiankong

from datetime import datetime, timedelta
from jiankong import settings 
import logging
from django.db.utils import IntegrityError
from xlwt.Workbook import Workbook
from django.http.response import HttpResponse
from jiankong.tasks import do_jiankong_gss_v2
import pytz
from parcel.views import get_parcel_info
from django.contrib.auth.models import User
import math
from django.db.models import Q
from yunda_commen.commen_tasks import send_email
import json

logger = logging.getLogger('django')
# Create your views here.
@json_response
@secure_required
@staff_member_required
def add_to_jiankong(request):
    start = int(request.GET.get('start', "0"))
    end = int(request.GET.get('end', "0"))    
    if not start:
        start = 0
    if (end and end < start) or (not end):
        end = start + 100
    count = IntlParcel.objects.filter(is_deleted=False).exclude(tracking_number__isnull=True).exclude(tracking_number__exact='').count()
    return {'added':add_parcel_to_jiankong(start, end),
            'total_parcels':count,
            'start':start,
            'end':end
            }

def add_parcel_to_jiankong(start, end):
    result = 0
    for parcel in IntlParcel.objects.filter(is_deleted=False).exclude(tracking_number__isnull=True).exclude(tracking_number__exact='')[start:end]:
        try:
            IntlParcelJiankong.objects.create(
                yid=parcel.yid,
                customer_number=parcel.user.userprofile.customer_number,
                tracking_number=parcel.tracking_number,
                type_code=parcel.type.code,
                created_at=parcel.created_at,
                status="created"
                                              )
            result += 1
        except IntegrityError:
            # 重复项不再加入
            pass
        except Exception as e:
            logger.error(e)       
    return result

@json_response
@secure_required
@staff_member_required
def jiankong(request):    
    try:
        ##add all intl parcels to jiankong
        parcels_added_to_jiankong=0
        for parcel in IntlParcel.objects.filter(is_deleted=False).exclude(tracking_number__isnull=True).exclude(tracking_number__exact=''):
            try:
                IntlParcelJiankong.objects.create(
                    yid=parcel.yid,
                    customer_number=parcel.user.userprofile.customer_number,
                    tracking_number=parcel.tracking_number,
                    type_code=parcel.type.code,
                    created_at=parcel.created_at,
                    status="created"
                                                  )
                parcels_added_to_jiankong += 1
            except IntegrityError:
                # 重复项不再加入
                pass
            except Exception as e:
                logger.error(e)
        ##connect mawb and jiankong record
        mawbs = Mawb.objects.filter(Q(status__iexact='warehouse_closed') | Q(status__iexact='warehouse_open'))
        errors_cant_set_mawb_to_jiankong = []
        errors_duplicated_in_mawb = []
        for mawb in mawbs:
            yids = []
            for batch in mawb.batches.all():
                yids += batch.yids
            jks = IntlParcelJiankong.objects.filter(yid__in=yids)
            jks_yids = []
            for jk in jks:
                if jk.mawb and jk.mawb != mawb:
                    errors_duplicated_in_mawb.append({'tracking_number':jk.tracking_number,
                                               'mawb1':mawb.mawb_number,
                                               'mawb2':jk.mawb.mawb_number,
                                               })
                else:
                    jk.mawb = mawb
                    jks_yids.append(jk.yid)
                    jk.save()
            errors_cant_set_mawb_to_jiankong.append({'mawb':mawb.mawb_number,
                            'error_parcels':subtract_list(yids, jks_yids)
                            })

        start_jiankong()        
        result= {
                'state':'success',
                'parcels_added_to_jiankong':parcels_added_to_jiankong,
                'errors_cant_set_mawb_to_jiankong':errors_cant_set_mawb_to_jiankong,
                'errors_duplicated_in_mawb':errors_duplicated_in_mawb,
                }
        send_email.delay("Starting monitoring report", json.dumps(result), to_emails=['Lik Li<lik.li@yunda-express.eu>'])
        return result
    except Exception as e:
        logger.error(e)
        return {'state':"error",'msg':e}

def start_jiankong():
    number_once = 50
    result = 0
    try:
        amount = IntlParcelJiankong.objects.filter(type_code__icontains='yd', finished_jiankong=False).count()
        for start in range(0, amount, number_once):
            do_jiankong_gss_v2.delay(start, start + number_once)
        return result
    except Exception as e:
        logger.error(e)
    

@json_response
@secure_required
@staff_member_required
def set_mawb(request):
    try:
        is_all = request.GET.get('is_all', 'no')
        if is_all == 'yes':
            mawbs = Mawb.objects.all()
        else:
            mawbs = Mawb.objects.filter(status__iexact='warehouse_closed')
        results = []
        duplicated_in_mawb = []
        for mawb in mawbs:
            yids = []
            for batch in mawb.batches.all():
                yids += batch.yids
            jks = IntlParcelJiankong.objects.filter(yid__in=yids)
            jks_yids = []
            for jk in jks:
                if jk.mawb and jk.mawb != mawb:
                    duplicated_in_mawb.append({'tracking_number':jk.tracking_number,
                                               'mawb1':mawb.mawb_number,
                                               'mawb2':jk.mawb.mawb_number,
                                               })
                else:
                    jk.mawb = mawb
                    jks_yids.append(jk.yid)
                    jk.save()
            results.append({'mawb':mawb.mawb_number,
                            'error_parcels':subtract_list(yids, jks_yids)
                            })
        results.append(duplicated_in_mawb)
        return results
    except Exception as e:
        logger.error(e)
        return e
    
            
def subtract_list(list1, list2):
    result = []
    for a in list1:
        if a not in list2:
            result.append(a)
    return result

@json_response
@secure_required
@staff_member_required
def json_need_check(request):
    pass


@secure_required
@staff_member_required
def excel_need_check(request):
    book = Workbook()
    sheet = book.add_sheet('Jiankong')
    row = 0
    sheet.write(row, 0, u'Tracking number\n跟踪号码')
    sheet.write(row, 1, u'Mawb name\n批号')
    sheet.write(row, 2, u'Mawb number\n主单号')
    sheet.write(row, 3, u'Customer number\n客户编号')
    sheet.write(row, 4, u'Latest time\n最新状态时间')
    sheet.write(row, 5, u'CN desc\n中文描述')
    sheet.write(row, 6, u'Days delayed\n距离最新状态天数')
    sheet.write(row, 7, u'Checked at\n检查时间')
    sheet.write(row, 8, u'Comments\n备注记录')
    row += 1
    try:
        for jk in IntlParcelJiankong.objects\
            .exclude(status__iexact="deliveried").exclude(finished_jiankong=True).order_by("-status","mawb__mawb_number","customer_number"):
            now = datetime.now()
            now = datetime(now.year, now.month, now.day)
            
            if jk.status == "delivery_staff_asigned":
                jkdt = datetime(jk.delivery_staff_asigned_at.year, jk.delivery_staff_asigned_at.month, jk.delivery_staff_asigned_at.day)
                dt = now - timedelta(days=settings.STATUSES['delivery_staff_asigned'])
                if jkdt < dt:
                    jk_write_to_sheet(sheet, row, jk, jk.delivery_staff_asigned_at, u"已指定快递小哥投递", (now - jkdt).days, now)
                    row += 1
                    
            elif jk.status == "local_opc_received":
                jkdt = datetime(jk.newest_datetime.year, jk.newest_datetime.month, jk.newest_datetime.day)
                dt = now - timedelta(days=settings.STATUSES['local_opc_received'])
                if jkdt < dt:
                    jk_write_to_sheet(sheet, row, jk, jk.newest_datetime, u"已进入国内中转", (now - jkdt).days, now)
                    row += 1
                     
            elif jk.status == "import_customs_finished":
                jkdt = datetime(jk.import_customs_finished_at.year, jk.import_customs_finished_at.month, jk.import_customs_finished_at.day)
                dt = now - timedelta(days=settings.STATUSES['import_customs_finished'])
                if jkdt < dt:
                    jk_write_to_sheet(sheet, row, jk, jk.import_customs_finished_at, u"国内清关已完成", (now - jkdt).days, now)
                    row += 1
             
            elif jk.status == "destination_country_arrived":
                jkdt = datetime(jk.destination_country_arrived_at.year, jk.destination_country_arrived_at.month, jk.destination_country_arrived_at.day)
                dt = now - timedelta(days=settings.STATUSES['destination_country_arrived'])
                if jkdt < dt:
                    jk_write_to_sheet(sheet, row, jk, jk.destination_country_arrived_at, u"已抵达国内机场", (now - jkdt).days, now)
                    row += 1
                     
            elif jk.status == "opc_flied":
                jkdt = datetime(jk.opc_flied_at.year, jk.opc_flied_at.month, jk.opc_flied_at.day)
                dt = now - timedelta(days=settings.STATUSES['opc_flied'])                 
                if jkdt < dt:
                    jk_write_to_sheet(sheet, row, jk, jk.opc_flied_at, u"已离港起飞", (now - jkdt).days, now)
                    row += 1
                
            elif jk.status == "opc_export_customs_finished":
                jkdt = datetime(jk.opc_export_customs_finished_at.year, jk.opc_export_customs_finished_at.month, jk.opc_export_customs_finished_at.day)
                dt = now - timedelta(days=settings.STATUSES['opc_export_customs_finished'])                 
                if jkdt < dt:
                    jk_write_to_sheet(sheet, row, jk, jk.opc_export_customs_finished_at, u"离岸清关已完成", (now - jkdt).days, now)
                    row += 1
                                     
            elif jk.status == "opc_export_ready":
                jkdt = datetime(jk.opc_export_ready_at.year, jk.opc_export_ready_at.month, jk.opc_export_ready_at.day)
                dt = now - timedelta(days=settings.STATUSES['opc_export_ready'])
                if jkdt < dt:
                    jk_write_to_sheet(sheet, row, jk, jk.opc_export_ready_at, u"库房处理已完成", (now - jkdt).days, now)
                    row += 1
                
            elif jk.status == "opc_arrived":
                jkdt = datetime(jk.opc_arrived_at.year, jk.opc_arrived_at.month, jk.opc_arrived_at.day)
                dt = now - timedelta(days=settings.STATUSES['opc_arrived'])                
                if jkdt < dt:
                    jk_write_to_sheet(sheet, row, jk, jk.opc_arrived_at, u"已抵达库房", (now - jkdt).days, now)
                    row += 1
                  
            elif jk.status == "created":
                jkdt = datetime(jk.created_at.year, jk.created_at.month, jk.created_at.day)
                dt = now - timedelta(days=settings.STATUSES['created'])
                if jkdt < dt:
                    jk_write_to_sheet(sheet, row, jk, jk.created_at, u"客户已生成订单", (now - jkdt).days, now)
                    row += 1
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=jiankong-%s.xls' % datetime.now().strftime('%Y%m%d%H%M%S')
        book.save(response)
        return response
            
    except Exception as e:
        logger.error(e)
        return HttpResponse(e)

def jk_write_to_sheet(sheet, row, jk, lastest_time, text, days, checked_at):
    sheet.write(row, 0, jk.tracking_number)
    sheet.write(row, 1, jk.mawb and jk.mawb.mawb_number or '')
    sheet.write(row, 2, jk.mawb and jk.mawb.number or '')
    sheet.write(row, 3, jk.customer_number)    
    sheet.write(row, 4, lastest_time.strftime('%Y-%m-%d %H:%M:%S'))
    sheet.write(row, 5, text)
    sheet.write(row, 6, days)
    sheet.write(row, 7, checked_at.strftime('%Y-%m-%d'))
    messages = ""
    if jk.messages:
        for msg in jk.messages:
            if msg["datetime"] and msg["text"]:
                messages += msg["datetime"] + " " + msg["text"] + "\n"
            else:
                messages+=json.dumps(msg)+"\n"
    sheet.write(row, 8, messages)

@json_response
@secure_required
@staff_member_required
def json_get_jiankong(request):
    tracking_number = request.GET.get('tracking_number', False)   
    if tracking_number:
        try:
            tz = getattr(settings, 'TIME_ZONE', 'Asia/Shanghai')
            local = pytz.timezone(tz)
            
            jk = IntlParcelJiankong.objects.get(tracking_number=tracking_number)
            result = {
                'id':jk.id,
                'yid':jk.yid,
                'customer_number':jk.customer_number,
                'tracking_number':jk.tracking_number,
                'type_code':jk.type_code,
                'mawb_number':jk.mawb and jk.mawb.number or '',
                'mawb_name':jk.mawb and jk.mawb.mawb_number or '',
                'finished_jiankong':jk.finished_jiankong,
                'created_at':jk.created_at and jk.created_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                'opc_arrived_at':jk.opc_arrived_at and jk.opc_arrived_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                'opc_export_ready_at':jk.opc_export_ready_at and jk.opc_export_ready_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                'opc_export_customs_finished_at':jk.opc_export_customs_finished_at and jk.opc_export_customs_finished_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                'opc_flied_at':jk.opc_flied_at and jk.opc_flied_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                'destination_country_arrived_at':jk.destination_country_arrived_at and jk.destination_country_arrived_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                'import_customs_finished_at':jk.import_customs_finished_at and jk.import_customs_finished_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                'local_opc_received_at':jk.local_opc_received_at and jk.local_opc_received_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                'delivery_staff_asigned_at':jk.delivery_staff_asigned_at and jk.delivery_staff_asigned_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                'deliveried_at':jk.deliveried_at and jk.deliveried_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                
                'status':jk.status,
                'newest_datetime':jk.newest_datetime and jk.newest_datetime.strftime('%Y-%m-%d %H:%M:%S') or '',
                'last_checked_at':jk.last_checked_at and jk.last_checked_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                'messages':jk.messages or [],
                'days_delayed':jk.days_delayed,
            }          
            parcel = IntlParcel.objects.get(yid=jk.yid)
            parcel_infos = get_parcel_info(parcel, local)
            # 实际重量等信息
            parcel_infos['real_weight_kg']= parcel.real_weight_kg or 0
            parcel_infos['real_length_cm']= parcel.real_length_cm or 0
            parcel_infos['real_width_cm']= parcel.real_width_cm or 0
            parcel_infos['real_height_cm']= parcel.real_height_cm or 0
            parcel_infos['booked_fee']= parcel.booked_fee or 0
            parcel_infos['json_prices']= parcel.json_prices
            details = []
            for detail in parcel.goodsdetails.all():
                details.append({
                    "description":detail.description,
                    "cn_customs_tax_catalog_name":detail.cn_customs_tax_catalog_name,
                    "cn_customs_tax_name":detail.cn_customs_tax_name,
                    "qty":detail.qty,
                    "item_net_weight_kg":detail.item_net_weight_kg,
                    "item_price_eur":detail.item_price_eur, })
            parcel_infos['details'] = details
            result['parcel'] = parcel_infos            
            
            return {"state":'success', "jiankong":result}           
            
        except IntlParcelJiankong.DoesNotExist:
            logger.error("no intl parcel found")
            return dict(state="error", msg=u"No intl parcel found")
        except Exception as e:
            logger.error(e)
            return dict(state="error", msg=e)

@json_response
@secure_required
@staff_member_required
def json_edit_jiankong(request):
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)
    if request.method == "POST":
        tracking_number = request.POST.get('tracking_number', False)
        if tracking_number:
            try:
                jk = IntlParcelJiankong.objects.get(tracking_number=tracking_number)
                finished_jiankong = request.POST.get('finished_jiankong', False)
                if finished_jiankong and finished_jiankong == 'yes':
                    jk.finished_jiankong = True
                    jk.days_delayed=0
                elif finished_jiankong and finished_jiankong == 'no':
                    jk.finished_jiankong = False
                
                msg = request.POST.get('msg', '').strip()
                if msg:
                    messages = jk.messages or []
                    messages.append({
                                        'datetime':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                        'staff':user.get_full_name(),
                                        'text':msg                                        
                                        })
                    jk.messages = messages
                jk.save()
                return dict(state="success")
            
            except IntlParcelJiankong.DoesNotExist:
                logger.error("no intl parcel found")
                return dict(state="error", msg=u"No Jiankong record found")
            except Exception as e:
                logger.error(e)
                return dict(state="error", msg=e)

@json_response
@secure_required
@staff_member_required
def json_search_jiankong(request):
    if request.method == 'GET': 
        q = IntlParcelJiankong.objects
        page = int(request.GET.get('page', 1) or 1)
        rows = int(request.GET.get('rows', 10) or 10)
        if page < 1:
            page = 1
        if rows < 1:
            rows = 10
           
        customer_number = request.GET.get('customer_number', False)
        tracking_number = request.GET.get('tracking_number', False)
        type_code = request.GET.get('type_code', False)
        mawb_name = request.GET.get('mawb_name', False)
        mawb_number = request.GET.get('mawb_number', False)
        finished_jiankong = request.GET.get('finished_jiankong', False)        
        status = request.GET.get('status', False)
        
        is_delayed = request.GET.get('is_delayed', False)
                
        
        if customer_number:
            q = q.filter(customer_number__icontains=customer_number)
        if tracking_number:
            q = q.filter(tracking_number__icontains=tracking_number)
        if type_code:
            q = q.filter(type_code__icontains=type_code)
        if mawb_name:
            q = q.filter(mawb__mawb_number__icontains=mawb_name)
        if mawb_number:
            q = q.filter(mawb__number__icontains=mawb_number)
        if finished_jiankong:
            if finished_jiankong == "yes":
                q = q.filter(finished_jiankong=True)
            elif finished_jiankong == "no":
                q = q.filter(finished_jiankong=False)
        
        if status:
            q = q.filter(status__iexict=status)
        if is_delayed:
            if is_delayed == "yes":
                q = q.filter(days_delayed__gt=0)
            elif is_delayed == "no":
                q = q.filter(Q(days_delayed__lte=0) | Q(days_delayed__isnull=True))
        
        results = {}
        count = q.count()
        results['count'] = count or 0
        results['jiankongs'] = []
        if count == 0:            
            return results
        last_page = int(math.ceil(float(count) / float(rows)))
        if page * rows > count:
            page = last_page
        
        start = (page - 1) * rows
        end = page * rows
        if end > count:
            end = count
        results['start'] = start
        results['end'] = end
        results['page'] = page
        results['rows'] = rows
        results['last_page'] = last_page
        for jk in q.order_by('status','-mawb','customer_number')[start:end]:
            results['jiankongs'].append(
                {
                    'id':jk.id,
                    'yid':jk.yid,
                    'customer_number':jk.customer_number,
                    'tracking_number':jk.tracking_number,
                    'type_code':jk.type_code,
                    'mawb_number':jk.mawb and jk.mawb.number or '',
                    'mawb_name':jk.mawb and jk.mawb.mawb_number or '',
                    'finished_jiankong':jk.finished_jiankong,
                    'created_at':jk.created_at and jk.created_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                    'opc_arrived_at':jk.opc_arrived_at and jk.opc_arrived_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                    'opc_export_ready_at':jk.opc_export_ready_at and jk.opc_export_ready_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                    'opc_export_customs_finished_at':jk.opc_export_customs_finished_at and jk.opc_export_customs_finished_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                    'opc_flied_at':jk.opc_flied_at and jk.opc_flied_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                    'destination_country_arrived_at':jk.destination_country_arrived_at and jk.destination_country_arrived_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                    'import_customs_finished_at':jk.import_customs_finished_at and jk.import_customs_finished_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                    'local_opc_received_at':jk.local_opc_received_at and jk.local_opc_received_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                    'delivery_staff_asigned_at':jk.delivery_staff_asigned_at and jk.delivery_staff_asigned_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                    'deliveried_at':jk.deliveried_at and jk.deliveried_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                    
                    'status':jk.status,
                    'newest_datetime':jk.newest_datetime and jk.newest_datetime.strftime('%Y-%m-%d %H:%M:%S') or '',
                    'last_checked_at':jk.last_checked_at and jk.last_checked_at.strftime('%Y-%m-%d %H:%M:%S') or '',
                    'messages':jk.messages or [],
                    'days_delayed':jk.days_delayed,
                })        
        return results

@json_response
@secure_required
@staff_member_required
def set_mawb_intl_parcel(request):
    try:
        is_all = request.GET.get('is_all', 'no')
        if is_all == 'yes':
            mawbs = Mawb.objects.all()
        else:
            mawbs = Mawb.objects.filter(status__iexact='warehouse_closed')
        results = []
        duplicated_in_mawb = []
        for mawb in mawbs:
            exported_at=None
            for history in mawb.histories:
                if history["status"]=="flied_to_dest":
                    try:
                        dt, _a, _us= history["datetime"].partition(".")
                        exported_at=datetime.strptime( dt, "%Y-%m-%dT%H:%M:%S" )
                    except:
                        exported_at=datetime.strptime( dt, "%Y-%m-%d %H:%M:%S" )
            yids = []
            for batch in mawb.batches.all():
                yids += batch.yids
            jks = IntlParcel.objects.filter(yid__in=yids)
            jks_yids = []
            for jk in jks:
                if jk.mawb and jk.mawb != mawb:
                    duplicated_in_mawb.append({'tracking_number':jk.tracking_number,
                                               'mawb1':mawb.mawb_number,
                                               'mawb2':jk.mawb.mawb_number,
                                               })
                else:
                    jk.mawb = mawb
                    jk.exported_at=exported_at
                    jks_yids.append(jk.yid)
                    jk.save()
            results.append({'mawb':mawb.mawb_number,
                            'error_parcels':subtract_list(yids, jks_yids)
                            })
        results.append(duplicated_in_mawb)
        return results
    except Exception as e:
        logger.error(e)
        return e

################################
# 20151224

def _excel_mawb_report_write_title(sheet):
    sheet.write(0, 0, u"主单号")
    sheet.write(0, 1, u"韵达欧洲单号")
    sheet.write(0, 2, u"韵达中国单号")
    sheet.write(0, 3, u"客户编号")
    sheet.write(0, 4, u"寄件人姓名")
    sheet.write(0, 5, u"寄件人联系方式")
    sheet.write(0, 6, u"寄件人地址")
    sheet.write(0, 7, u"收件人姓名")
    sheet.write(0, 8, u"收件人联系方式")
    sheet.write(0, 9, u"收件人省份")
    sheet.write(0, 10, u"收件人地址")
    sheet.write(0, 11, u"邮单建立时间")  # created
    sheet.write(0, 12, u"到仓时间")  # opc_arrived
    sheet.write(0, 13, u"出仓时间")  # export_ready
    sheet.write(0, 14, u"航班起飞时间")  # flied
    sheet.write(0, 15, u"航班到达时间")  #
    sheet.write(0, 16, u"出关时间")
    sheet.write(0, 17, u"到达国内韵达时间")
    sheet.write(0, 18, u"妥投时间")
    sheet.write(0, 19, u"客户填写重量")
    sheet.write(0, 20, u"客户填写体积重量")
    sheet.write(0, 21, u"实际重量")
    sheet.write(0, 22, u"实际体积重量")
    sheet.write(0, 23, u"实际收费CNY")
    sheet.write(0, 24, u"运营成本分摊CNY")
    sheet.write(0, 25, u"库房至机场运费CNY")
    sheet.write(0, 26, u"空运费用CNY")
    sheet.write(0, 27, u"清关费CNY")
    sheet.write(0, 28, u"国内派送费CNY")
    sheet.write(0, 29, u"税金CNY")
    
@secure_required
@staff_member_required
def excel_mawb_report(request):
    if request.method == 'GET':
        ids = request.GET.get('ids', False)
    if request.method == 'POST':
        ids = request.POST.get('ids', False)
    if ids:
        ids = ids.split('.')
        book = Workbook()
        sheet = book.add_sheet('Parcels info')
        remark_sheet = book.add_sheet("Remarks")
        _excel_mawb_report_write_title(sheet)
        row = 1
        remarks = []
        if ids:
            try:
                for mawb in Mawb.objects.filter(id__in=ids):
                    yids = []
                    for batch in mawb.batches.all():
                        yids += batch.yids
                    parcels = IntlParcel.objects.filter(yid__in=yids)
                    if len(yids) != parcels.count():
                        remarks.append("MAWB %s: qty not match: qty in all batches  %d, found %d" % (mawb.mawb_number, len(yids), parcels.count()))
                    for parcel in parcels:
                        jiankong = IntlParcelJiankong.objects.get(yid=parcel.yid)
                        customer_number = parcel.user.userprofile.customer_number
                        sheet.write(row, 0, mawb.mawb_number)
                        sheet.write(row, 1, parcel.yde_number)
                        sheet.write(row, 2, parcel.tracking_number)
                        sheet.write(row, 3, customer_number)
                        sheet.write(row, 4, parcel.sender_name)
                        sheet.write(row, 5, parcel.sender_tel)
                        sheet.write(row, 6, u"%s %s %s" % (parcel.sender_street, parcel.sender_hause_number, parcel.sender_city))
                        sheet.write(row, 7, parcel.receiver_name)
                        sheet.write(row, 8, parcel.receiver_mobile)
                        sheet.write(row, 9, parcel.receiver_province)
                        sheet.write(row, 10, u"%s%s%s" % (parcel.receiver_city or "", parcel.receiver_district or "", parcel.receiver_address))
                        sheet.write(row, 11, jiankong.created_at and jiankong.created_at.strftime('%Y-%m-%d %H:%M:%S') or "")  # created
                        sheet.write(row, 12, jiankong.opc_arrived_at and jiankong.opc_arrived_at.strftime('%Y-%m-%d %H:%M:%S') or "")  # opc_arrived
                        sheet.write(row, 13, jiankong.opc_export_ready_at and jiankong.opc_export_ready_at.strftime('%Y-%m-%d %H:%M:%S') or "")  # export_ready
                        sheet.write(row, 14, jiankong.opc_flied_at and jiankong.opc_flied_at.strftime('%Y-%m-%d %H:%M:%S') or "")  # flied
                        sheet.write(row, 15, jiankong.destination_country_arrived_at and jiankong.destination_country_arrived_at.strftime('%Y-%m-%d %H:%M:%S') or "")  #
                        sheet.write(row, 16, jiankong.import_customs_finished_at and jiankong.import_customs_finished_at.strftime('%Y-%m-%d %H:%M:%S') or "")
                        sheet.write(row, 17, jiankong.local_opc_received_at and jiankong.local_opc_received_at.strftime('%Y-%m-%d %H:%M:%S') or "")
                        sheet.write(row, 18, jiankong.deliveried_at and jiankong.deliveried_at.strftime('%Y-%m-%d %H:%M:%S') or "")
                        sheet.write(row, 19, "%.2f" % parcel.weight_kg)
                        sheet.write(row, 20, "%.2f" % (parcel.width_cm * parcel.length_cm * parcel.height_cm / 6000))
                        sheet.write(row, 21, "%.2f" % parcel.real_weight_kg)
                        real_vw = parcel.real_width_cm * parcel.real_length_cm * parcel.real_height_cm / 6000
                        if real_vw < parcel.real_weight_kg:
                            real_vw = parcel.real_weight_kg
                        sheet.write(row, 22, "%.2f" % real_vw)
                        real_fee = parcel.booked_fee
                        if "K" in customer_number:
                            real_fee = real_fee * 7
                        sheet.write(row, 23, u"%.2f" % real_fee)
                        #sheet.write(row, 24, u"运营成本分摊CNY")
                        #sheet.write(row, 25, u"库房至机场运费CNY")
                        #sheet.write(row, 26, u"空运费用CNY")
                        #sheet.write(row, 27, u"清关费CNY")
                        #sheet.write(row, 28, u"国内派送费CNY")
                        #sheet.write(row, 29, u"税金CNY")
                        row += 1

                r_row=0
                for remark in remarks:
                    remark_sheet.write(r_row,0,remark)
                    r_row+=1
                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename=statistics-%s.xls' % datetime.now().strftime('%Y%m%d%H%M%S')
                book.save(response)
                return response
            
            except Exception as e:
                logger.error(e)
                return HttpResponse(e)
    return HttpResponse("No ids found")


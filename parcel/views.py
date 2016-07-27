# -*- coding: utf-8 -*-
from yunda_commen.decorators import json_response
from userena.decorators import secure_required
from django.contrib.auth.decorators import login_required
from userena.models import UserProfile
from django.contrib.auth.models import User
from parcel.models import Level, ParcelType, PriceLevel, IntlParcel, History, \
    add_to_mawb, Mawb, Batch, ProductMainCategory, ProductCategory, ProductBrand, \
    Product, GoodsDetail, CnCustoms
from parcel.forms import IntlParcelForm, ParcelDetailForm, MawbForm, BatchForm
import hashlib
from yunda_parcel.models import SenderTemplate, ReceiverTemplate, \
    DhlRetoureLabel, RetoureHistory, CnCustomsTax
import re
from yunda_commen.commen_utils import get_seq_by_code, get_retoure_price
from datetime import datetime
import math
import pytz
from django.conf import settings
from django.db.models import Q
from yunda_parcel.forms import DhlRetoureLabelForm, SenderTemplateForm, \
    ReceiverTemplateForm
from wkhtmltopdf.views import PDFTemplateView
from django.utils.decorators import method_decorator
from django.http import Http404
from parcel.tools import  get_parcel_numbers, tracking_push, \
    tracking_fetch, query_parcel, create_retoure_label
from django.views.decorators.csrf import csrf_exempt
from parcel.excel_import import get_parcel_infos_from_excel
from django.contrib.admin.views.decorators import staff_member_required
from messenge.models import write_new_subject_to_customer
from xlwt import Workbook
from django.http.response import HttpResponse
from xlrd import open_workbook
import types
from yunda_commen.models import Settings as YundaCommenSettings

import logging
import base64
from contextlib import closing
from PIL import Image
import os
import xlwt
from yunda_commen import imagekit
from django.template import loader, Context
from yunda_user.models import DepositTransferNew
logger = logging.getLogger('django.parcel')
from django.core.mail.message import EmailMessage
from email.mime.base import MIMEBase
from StringIO import StringIO
import zipfile
from decimal import Decimal
try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

# Create your views here.

################################################################################
# # part retoure label
# #
################################################################################
@json_response
@secure_required
@login_required
def json_post_retoure(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        parcel_form = DhlRetoureLabelForm(request.POST, request.FILES)

        is_valid = True

        if not parcel_form.is_valid():
            is_valid = False
            parcel_errors = parcel_form.errors

        if is_valid:
            parcel_clean_data = parcel_form.clean()
            yid = request.POST.get('yid', False)
            if yid:
                # edit a parcel
                try:
                    parcel = DhlRetoureLabel.objects.get(user_id=user_id, yid=yid, is_deleted=False)
                    if parcel.status in ['draft']:
                        # update intel parcel
                        update_parcel_form = DhlRetoureLabelForm(request.POST, instance=parcel)
                        update_parcel_form.save()



                        # create sender and receiver template if checked
                        if parcel_clean_data['save_sender'] == "true":
                            try:
                                template = SenderTemplate.objects.create(
                                    user=user,
                                    sender_name=parcel_clean_data['sender_name'],
                                    sender_name2=parcel_clean_data['sender_name2'],
                                    sender_company=parcel_clean_data['sender_company'],
                                    sender_city=parcel_clean_data['sender_city'],
                                    sender_postcode=parcel_clean_data['sender_postcode'],
                                    sender_street=parcel_clean_data['sender_street'],
                                    sender_add=parcel_clean_data['sender_add'],
                                    sender_hause_number=parcel_clean_data['sender_hause_number'],
                                    sender_tel=parcel_clean_data['sender_tel'],
                                    sender_email=parcel_clean_data['sender_email'],
                                    )
                                template.yid = hashlib.md5("sendertemplate%d" % template.id).hexdigest()
                                template.save()
                            except Exception as e:
                                logger.debug(e)


                        return dict(state="success",
                            yid=parcel.yid)

                    else:
                        return dict(state="error",
                            msg=u"回邮单已提交，不能被修改")
                except DhlRetoureLabel.DoesNotExist:
                    return dict(state="error",
                            msg=u"回邮单不存在或者已被删除")
            else:
                # create a new parcel

                parcel = parcel_form.save(commit=False)
                parcel.user_id = user_id
                currency_type = user.userprofile.deposit_currency_type
                parcel.currency_type = currency_type
                parcel.price = get_retoure_price(currency_type)
                parcel.created_at = datetime.now()
                parcel.save()
                parcel.yid = hashlib.md5("retoure%d" % parcel.id).hexdigest()
                parcel.save()


                if parcel_clean_data['save_sender'] == "true":
                    try:
                        template = SenderTemplate.objects.create(
                            user=user,
                            sender_name=parcel_clean_data['sender_name'],
                            sender_name2=parcel_clean_data['sender_name2'],
                            sender_company=parcel_clean_data['sender_company'],
                            sender_city=parcel_clean_data['sender_city'],
                            sender_postcode=parcel_clean_data['sender_postcode'],
                            sender_street=parcel_clean_data['sender_street'],
                            sender_add=parcel_clean_data['sender_add'],
                            sender_hause_number=parcel_clean_data['sender_hause_number'],
                            sender_tel=parcel_clean_data['sender_tel'],
                            sender_email=parcel_clean_data['sender_email'],
                            )
                        template.yid = hashlib.md5("sendertemplate%d" % template.id).hexdigest()
                        template.save()
                    except Exception as e:
                        logger.debug(e)

                return dict(state="success",
                            yid=parcel.yid)
        else:
            return dict(state='error',
                        parcel_errors=parcel_errors)

            # user = form.save()
    else:
        return {'error':True}

def get_retoure_info(parcel, local=None):
    logger.info('')
    result = {}

    if not local:
        tz = getattr(settings, 'TIME_ZONE', 'Asia/Shanghai')
        local = pytz.timezone(tz)
    local_dt = parcel.created_at.astimezone(local)

    result['created_at'] = parcel.created_at.astimezone(local).strftime("%Y-%m-%d %H:%M")

    result['sender_name'] = parcel.sender_name
    result['sender_name2'] = parcel.sender_name2
    result['sender_company'] = parcel.sender_company
    result['sender_city'] = parcel.sender_city
    result['sender_postcode'] = parcel.sender_postcode
    result['sender_street'] = parcel.sender_street
    result['sender_add'] = parcel.sender_add
    result['sender_hause_number'] = parcel.sender_hause_number
    result['sender_tel'] = parcel.sender_tel
    result['sender_email'] = parcel.sender_email

    result['yde_number'] = parcel.retoure_yde_number or u"草稿,未生成订单号"
    result['yid'] = parcel.yid

    result['tracking_number'] = parcel.tracking_number

    result['status'] = parcel.status
    result['currency_type'] = parcel.currency_type
    result['price'] = parcel.price
    return result

@json_response
@secure_required
@login_required
def json_get_retoure(request, yid):
    logger.info('')
    user_id = request.session.get('_auth_user_id')

    if yid:
        try:
            tz = getattr(settings, 'TIME_ZONE', 'Asia/Shanghai')
            local = pytz.timezone(tz)

            parcel = DhlRetoureLabel.objects.get(yid=yid, user_id=user_id, is_deleted=False)
            result = get_retoure_info(parcel, local)


            histories = []
            for history in parcel.histories.filter(visible_to_customer=True).order_by('created_at'):
                histories.append({
                    "created_at":history.created_at.astimezone(local).strftime("%Y-%m-%d %H:%M"),
                    "description":history.description, })
            result['histories'] = histories

            return {"state":'success', "parcel":result}



        except DhlRetoureLabel.DoesNotExist:
            return dict(state="error", msg=u"未找到该回邮单")


@json_response
@secure_required
@login_required
def json_confirm_retoure(request):
    logger.info('')
    if request.method == 'POST':
        results = []
        user_id = request.session.get('_auth_user_id')
        user = User.objects.get(id=user_id)
        yids = request.POST.get('yids', False)
        p = re.compile(u'^[a-zA-Z0-9\+]+$')
        if yids and p.match(yids):
            yids = yids.split('+')
            for yid in yids:
                try:
                    parcel = DhlRetoureLabel.objects.get(yid=yid, user_id=user_id, status='draft')
                    if not parcel.retoure_yde_number:
                        parcel.retoure_yde_number = get_seq_by_code('drn_seq', True)
                    parcel.save()
                    # 扣款
                    (success, msg) = user.userprofile.deposit_deduct(parcel.price or 3.9, parcel.retoure_yde_number, u"德国境内回邮单。订单号：" + parcel.retoure_yde_number,)
                    if success:
                        # 扣款成功
                        # TODO
                        #attributes = {'idc':'123456789789',
                        #            'routingCode':'64546.211.011.33 7'
                        #            }
                        #pdf = "abc"
                        attributes, pdf = create_retoure_label(parcel.retoure_yde_number, parcel)
                        if attributes:
                            parcel.status = 'confirmed'
                            RetoureHistory.objects.create(description=u"扣款成功，生成回邮单。追踪号：" + attributes['idc'],
                                       retoure=parcel,
                                       created_at=datetime.now())
                            parcel.tracking_number = attributes['idc']
                            parcel.routing_code = attributes['routingCode']
                            parcel.created_at = datetime.now()
                            parcel.pdf_file = pdf
                            parcel.save()

                            results.append({'yid':yid,
                                        'yde_number':parcel.retoure_yde_number,
                                        'tracking_number':attributes['idc']})

                        else:  # 未生成回邮单号，退回扣款
                            user.userprofile.deposit_increase(parcel.price or 3.9, parcel.retoure_yde_number, u"德国境内回邮单。订单号：" + parcel.retoure_yde_number,)


                    else:
                        # 扣款不成功
                        pass

                except DhlRetoureLabel.DoesNotExist:
                    logger.error("retoure not exist")
                except Exception as e:
                    logger.error(e)
            return results
@json_response
@secure_required
@login_required
def json_remove_retoure(request):
    logger.info('')
    if request.method == 'POST':
        results = []
        user_id = request.session.get('_auth_user_id')
        yids = request.POST.get('yids', False)
        p = re.compile(u'^[a-zA-Z0-9\+]+$')
        if yids and p.match(yids):
            yids = yids.split('+')
            for yid in yids:
                try:
                    parcel = DhlRetoureLabel.objects.get(yid=yid, user_id=user_id, status='draft')
                    parcel.is_deleted = True
                    parcel.save()
                    results.append({'yid':yid})
                except DhlRetoureLabel.DoesNotExist:
                    pass  # TODO make log
            return results
@json_response
@secure_required
@login_required
def json_search_retoure(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')

    if request.method == 'GET':
        q = DhlRetoureLabel.objects.filter(user_id=user_id, is_deleted=False)
        page = int(request.GET.get('page', 1))
        rows = int(request.GET.get('rows', 10))

        s = request.GET.get('s', False)
        if s:
            q = q.filter(Q(yde_number__icontains=s) |
                           Q(tracking_number__icontains=s) |
                           Q(sender_name__icontains=s) |
                           Q(sender_company__icontains=s) |
                           Q(sender_city__icontains=s) |
                           Q(sender_postcode__icontains=s) |
                           Q(sender_tel__icontains=s) |
                           Q(sender_street__icontains=s)
                           )
        else:
            sender_name = request.GET.get('sender_name', False)
            sender_company = request.GET.get('sender_company', False)
            sender_city = request.GET.get('sender_city', False)
            sender_postcode = request.GET.get('sender_postcode', False)
            sender_tel = request.GET.get('sender_tel', False)
            sender_street = request.GET.get('sender_street', False)

            status = request.GET.get('status', False)
            number = request.GET.get('number', False)


            if sender_name:
                q = q.filter(sender_name__icontains=sender_name)
            if sender_company:
                q = q.filter(sender_company__icontains=sender_company)
            if sender_city:
                q = q.filter(sender_city__icontains=sender_city)
            if sender_postcode:
                q = q.filter(sender_postcode__icontains=sender_postcode)
            if sender_tel:
                q = q.filter(sender_tel__icontains=sender_tel)
            if sender_street:
                q = q.filter(sender_street__icontains=sender_street)

            if status:
                q = q.filter(status=status)
            if number:
                q = q.filter(Q(yde_number__icontains=number) |
                           Q(tracking_number__icontains=number))

        results = {}
        count = q.count()
        results['count'] = count or 0
        if count == 0:
            results['parcels'] = []
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
        tz = getattr(settings, 'TIME_ZONE', 'Asia/Shanghai')
        local = pytz.timezone(tz)
        results['parcels'] = []
        for parcel in q.order_by('-created_at')[start:end]:
            results['parcels'].append(get_retoure_info(parcel, local))

        return results

class RetourePdfView(PDFTemplateView):
    filename = "retoure-label.pdf"
    template_name = 'parcel/dhl_retoure.html'
    cmd_options = {
        'orientation': 'landscape',
        'no-outline':True,  # 不产生index
        # 'collate': True,
        # 'quiet': None,
    }
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RetourePdfView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(RetourePdfView, self).get_context_data(*args, **kwargs)
        if self.request.method == 'GET':
            yids = self.request.GET.get('yids', '')
            yids = yids.split('.')
            user_id = self.request.session.get('_auth_user_id')
            parcels = []
            for yid in yids:
                try:
                    parcel = DhlRetoureLabel.objects.get(yid=yid,
                                                       user_id=user_id,
                                                       is_deleted=False,
                                                       status__in=['confirmed', 'finished'])
                    parcels.append(parcel)
                    if not parcel.printed_at:
                        parcel.printed_at = datetime.now()
                        parcel.save()
                except DhlRetoureLabel.DoesNotExist:
                    pass
            if parcels:
                context.update({'parcels':parcels})
            else:
                raise Http404('No retoure label found!')

        return context

#############################################################################
# # part intl parcel
# #
#############################################################################

@json_response
@secure_required
@login_required
def json_parcel_types(request):
    logger.info('')
    u_id = request.session.get('_auth_user_id')
    if u_id:
        user = User.objects.get(id=u_id)
        default_level = Level.objects.get(code="default")

        try:
            level = user.userprofile.level
        except Level.DoesNotExist:
            level = default_level

        logger.info(level)

        currency_type = user.userprofile.deposit_currency_type or "eur"
        parcel_types = []

        if user.userprofile.trusted:
            q = ParcelType.objects.all()
        else:
            q = ParcelType.objects.filter(show_to_all=True)

        for parcel_type in q.order_by("name"):
            try:
                price_level = PriceLevel.objects.get(level=level,
                                                   currency_type=currency_type,
                                                   parcel_type=parcel_type)
            except PriceLevel.DoesNotExist:
                try:
                    price_level = PriceLevel.objects.get(level=default_level,
                                                   currency_type=currency_type,
                                                   parcel_type=parcel_type)
                except PriceLevel.DoesNotExist:
                    # TODO add logging
                    return {"error500":"true"}
            parcel_types.append({'name':parcel_type.name,
                                 'code':parcel_type.code,
                                 'currency_type':currency_type,
                                 'json_prices':price_level.json_prices,
                                 'description':parcel_type.description})

        return parcel_types

@json_response
@secure_required
@login_required
def json_post_intl_parcel(request):
    logger.info('')
    u_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=u_id)
    if request.method == 'POST':
        parcel_form = IntlParcelForm(request.POST, request.FILES)
        detail_forms = []
        is_valid = True
        detail_errors = []
        for i in range(0, int(request.POST.get('detail_num', 0))):
            detail = dict(
                description=request.POST.get('description-' + str(i)),
                cn_customs_tax_catalog_name=request.POST.get('cn_customs_tax_catalog_name-' + str(i)),
                cn_customs_tax_name=request.POST.get('cn_customs_tax_name-' + str(i)),
                qty=request.POST.get('qty-' + str(i)),
                item_net_weight_kg=request.POST.get('item_net_weight_kg-' + str(i)),
                item_price_eur=request.POST.get('item_price_eur-' + str(i)))
            detail_form = ParcelDetailForm(detail)
            if detail_form.is_valid():
                detail_forms.append(ParcelDetailForm(detail))
            else:
                is_valid = False
                detail_errors.append({
                    'key':request.POST.get('key-' + str(i)),
                    'errors':detail_form.errors
                })

        if not parcel_form.is_valid():
            is_valid = False
            parcel_errors = parcel_form.errors

        if is_valid:
            parcel_clean_data = parcel_form.clean()
            yid = request.POST.get('yid', False)
            if yid:
                # edit a parcel
                try:
                    parcel = IntlParcel.objects.get(user=user, yid=yid, is_deleted=False)
                    if parcel.status in ['draft']:
                        # update intel parcel
                        update_parcel_form = IntlParcelForm(request.POST, instance=parcel)
                        update_parcel_form.save()

                        type = ParcelType.objects.get(code=parcel_clean_data['type_code'])
                        parcel.type = type

                        # #get price level
                        default_level = Level.objects.get(code="default")
                        level = user.userprofile.level or default_level
                        try:
                            price_level = PriceLevel.objects.get(level=level,
                                                               currency_type=parcel.currency_type,
                                                               parcel_type=type)
                        except PriceLevel.DoesNotExist:
                            price_level = PriceLevel.objects.get(level=default_level,
                                                               currency_type=parcel.currency_type,
                                                               parcel_type=type)

                        parcel.json_prices = price_level.json_prices
                        parcel.save()
                        parcel.get_sfz_status()

                        # delete goods details and create new goods details
                        parcel.goodsdetails.all().delete()
                        for detail_form in detail_forms:
                            detail = detail_form.save(commit=False)
                            detail.intl_parcel = parcel
                            detail.save()

                        # create sender and receiver template if checked
                        if parcel_clean_data['save_sender'] == "true":
                            try:
                                template = SenderTemplate.objects.create(
                                    user=user,
                                    sender_name=parcel_clean_data['sender_name'],
                                    sender_name2=parcel_clean_data['sender_name2'],
                                    sender_company=parcel_clean_data['sender_company'],
                                    sender_city=parcel_clean_data['sender_city'],
                                    sender_postcode=parcel_clean_data['sender_postcode'],
                                    sender_street=parcel_clean_data['sender_street'],
                                    sender_add=parcel_clean_data['sender_add'],
                                    sender_hause_number=parcel_clean_data['sender_hause_number'],
                                    sender_tel=parcel_clean_data['sender_tel'],
                                    sender_email=parcel_clean_data['sender_email'],
                                    )
                                template.yid = hashlib.md5("sendertemplate%d" % template.id).hexdigest()
                                template.save()
                            except Exception as e:
                                logger.debug(e)
                        if parcel_clean_data['save_receiver'] == "true":
                            try:
                                template = ReceiverTemplate.objects.create(
                                    user=user,
                                    receiver_name=parcel_clean_data['receiver_name'],
                                    receiver_company=parcel_clean_data['receiver_company'],
                                    receiver_province=parcel_clean_data['receiver_province'],
                                    receiver_city=parcel_clean_data['receiver_city'],
                                    receiver_district=parcel_clean_data['receiver_district'],
                                    receiver_postcode=parcel_clean_data['receiver_postcode'],
                                    receiver_address=parcel_clean_data['receiver_address'],
                                    receiver_address2=parcel_clean_data['receiver_address2'],
                                    receiver_mobile=parcel_clean_data['receiver_mobile'],
                                    receiver_email=parcel_clean_data['receiver_email'],
                                    )
                                template.yid = hashlib.md5("receivertemplate%d" % template.id).hexdigest()
                                template.save()
                            except Exception as e:
                                logger.debug(e)

                        return dict(state="success",
                            yid=parcel.yid)

                    else:
                        return dict(state="error",
                            msg=u"邮单已提交，不能被修改")
                except IntlParcel.DoesNotExist:
                    return dict(state="error",
                            msg=u"邮单不存在或者已被删除")
            else:
                # create a new parcel

                parcel = parcel_form.save(commit=False)
                parcel.user = user
                currency_type = user.userprofile.deposit_currency_type
                parcel.currency_type = currency_type

                type = ParcelType.objects.get(code=parcel_clean_data['type_code'])
                parcel.type = type

                # #get price level
                default_level = Level.objects.get(code="default")
                level = user.userprofile.level or default_level
                try:
                    price_level = PriceLevel.objects.get(level=level,
                                                       currency_type=currency_type,
                                                       parcel_type=type)
                except PriceLevel.DoesNotExist:
                    price_level = PriceLevel.objects.get(level=default_level,
                                                       currency_type=currency_type,
                                                       parcel_type=type)

                parcel.json_prices = price_level.json_prices
                parcel.save()
                parcel.yid = hashlib.md5("intlparcel%d" % parcel.id).hexdigest()
                parcel.save()
                parcel.get_sfz_status()

                for detail_form in detail_forms:
                    detail = detail_form.save(commit=False)
                    detail.intl_parcel = parcel
                    detail.save()

                if parcel_clean_data['save_sender'] == "true":
                    try:
                        template = SenderTemplate.objects.create(
                            user=user,
                            sender_name=parcel_clean_data['sender_name'],
                            sender_name2=parcel_clean_data['sender_name2'],
                            sender_company=parcel_clean_data['sender_company'],
                            sender_city=parcel_clean_data['sender_city'],
                            sender_postcode=parcel_clean_data['sender_postcode'],
                            sender_street=parcel_clean_data['sender_street'],
                            sender_add=parcel_clean_data['sender_add'],
                            sender_hause_number=parcel_clean_data['sender_hause_number'],
                            sender_tel=parcel_clean_data['sender_tel'],
                            sender_email=parcel_clean_data['sender_email'],
                            )
                        template.yid = hashlib.md5("sendertemplate%d" % template.id).hexdigest()
                        template.save()
                    except Exception as e:
                        logger.debug(e)
                if parcel_clean_data['save_receiver'] == "true":
                    try:
                        template = ReceiverTemplate.objects.create(
                            user=user,
                            receiver_name=parcel_clean_data['receiver_name'],
                            receiver_company=parcel_clean_data['receiver_company'],
                            receiver_province=parcel_clean_data['receiver_province'],
                            receiver_city=parcel_clean_data['receiver_city'],
                            receiver_district=parcel_clean_data['receiver_district'],
                            receiver_postcode=parcel_clean_data['receiver_postcode'],
                            receiver_address=parcel_clean_data['receiver_address'],
                            receiver_address2=parcel_clean_data['receiver_address2'],
                            receiver_mobile=parcel_clean_data['receiver_mobile'],
                            receiver_email=parcel_clean_data['receiver_email'],
                            )
                        template.yid = hashlib.md5("receivertemplate%d" % template.id).hexdigest()
                        template.save()
                    except Exception as e:
                        logger.debug(e)
                return dict(state="success",
                            yid=parcel.yid)
        else:
            return dict(state='error',
                        parcel_errors=parcel_errors,
                        detail_errors=detail_errors)

            # user = form.save()
    else:
        return {'error':True}

def get_parcel_info(parcel, local=None):
    logger.info('')
    try:
        result = {}

        if not local:
            tz = getattr(settings, 'TIME_ZONE', 'Asia/Shanghai')
            local = pytz.timezone(tz)
        local_dt = parcel.created_at.astimezone(local)

        result['created_at'] = parcel.created_at.astimezone(local).strftime("%Y-%m-%d %H:%M")

        result['sender_name'] = parcel.sender_name
        result['sender_name2'] = parcel.sender_name2
        result['sender_company'] = parcel.sender_company
        result['sender_city'] = parcel.sender_city
        result['sender_postcode'] = parcel.sender_postcode
        result['sender_street'] = parcel.sender_street
        result['sender_add'] = parcel.sender_add
        result['sender_hause_number'] = parcel.sender_hause_number
        result['sender_tel'] = parcel.sender_tel
        result['sender_email'] = parcel.sender_email

        result['receiver_name'] = parcel.receiver_name
        result['receiver_company'] = parcel.receiver_company
        result['receiver_province'] = parcel.receiver_province
        result['receiver_city'] = parcel.receiver_city
        result['receiver_district'] = parcel.receiver_district
        result['receiver_postcode'] = parcel.receiver_postcode
        result['receiver_address'] = parcel.receiver_address
        result['receiver_address2'] = parcel.receiver_address2
        result['receiver_mobile'] = parcel.receiver_mobile
        result['receiver_email'] = parcel.receiver_email

        result['ref'] = parcel.ref
        result['weight_kg'] = parcel.weight_kg
        result['length_cm'] = parcel.length_cm
        result['width_cm'] = parcel.width_cm
        result['height_cm'] = parcel.height_cm
        result['currency_type'] = parcel.currency_type
        result['yde_number'] = parcel.yde_number or u"草稿,未生成订单号"
        result['yid'] = parcel.yid
        result['type_code'] = parcel.type.code
        result['type_code_name'] = parcel.type.name
        result['tracking_number'] = parcel.tracking_number
        result['retoure_tracking_number'] = parcel.retoure_tracking_number
        result['cn_customs_paid_by'] = parcel.cn_customs_paid_by
        result['exported_at'] = parcel.exported_at and parcel.exported_at.strftime("%Y-%m-%d %H:%M") or ""
        if parcel.cn_customs_paid_by == "sender":
            result['cn_customs_paid_by_name'] = "发件人"
        else:
            result['cn_customs_paid_by_name'] = "收件人"
        result['json_prices'] = parcel.json_prices
        result['status'] = parcel.status
        result['sfz_status'] = parcel.get_sfz_status()
        if  parcel.printed_at:
            result['printed'] = True
        else:
            result['printed'] = False
        return result
    except Exception as e:
        logger.error(e)
@json_response
@secure_required
@login_required
def json_get_intl_parcel(request, yid):
    logger.info('')
    u_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=u_id)

    if yid:
        try:
            tz = getattr(settings, 'TIME_ZONE', 'Asia/Shanghai')
            local = pytz.timezone(tz)

            parcel = IntlParcel.objects.get(yid=yid, user=user)
            result = get_parcel_info(parcel, local)
            details = []
            for detail in parcel.goodsdetails.all():
                details.append({
                    "description":detail.description,
                    "cn_customs_tax_catalog_name":detail.cn_customs_tax_catalog_name,
                    "cn_customs_tax_name":detail.cn_customs_tax_name,
                    "qty":detail.qty,
                    "item_net_weight_kg":detail.item_net_weight_kg,
                    "item_price_eur":detail.item_price_eur, })
            result['details'] = details

            histories = []
            for history in parcel.histories.filter(visible_to_customer=True).order_by('created_at'):
                histories.append({
                    "created_at":history.created_at.astimezone(local).strftime("%Y-%m-%d %H:%M"),
                    "description":history.description, })
            result['histories'] = histories

            return {"state":'success', "parcel":result}



        except IntlParcel.DoesNotExist:
            return dict(state="error", msg=u"未找到该国际包裹单")

@json_response
@secure_required
@login_required
def json_confirm_intl_parcel(request):
    logger.info('')
    results = []
    try:
        if request.method == 'POST':

            user_id = request.session.get('_auth_user_id')
            user = User.objects.get(id=user_id)
            yids = request.POST.get('yids', False)
            p = re.compile(u'^[a-zA-Z0-9\+]+$')
            if yids and p.match(yids):
                yids = yids.split('+')
                parcels = IntlParcel.objects.filter(yid__in=yids, user_id=user_id, status='draft', is_deleted=False)
                for parcel in parcels:
                    if not parcel.yde_number:
                        parcel.yde_number = get_seq_by_code('yde', True)
                        parcel.save()
                    fee = parcel.get_fee()
                    fee_to_book = fee - parcel.booked_fee
                    # ## deduct the fee
                    logger.info(fee)
                    logger.info(parcel.booked_fee)
                    logger.info(fee_to_book)
                    (success, msg) = user.userprofile.deposit_deduct(fee_to_book, parcel.yde_number, u"国际邮单。订单号：" + parcel.yde_number)
                    if success:
                        # 扣款成功
########################################################
                        parcel.booked_fee = fee
                        parcel.save()
########################################################
                        numbers = get_parcel_numbers(parcel)
                        logger.info(numbers)
                        if numbers['success']:
                            parcel.tracking_number = numbers['tracking_number']
                            parcel.tracking_number_created_at = datetime.now()
                            parcel.retoure_tracking_number = numbers['retoure_tracking_number']
                            parcel.retoure_tracking_number_created_at = datetime.now()
                            parcel.retoure_routing_code = numbers['retoure_routing_code']
                            parcel.pdf_info = numbers['pdf_info']
                            parcel.status = 'confirmed'
                            parcel.booked_fee = fee
                            History.objects.create(intl_parcel=parcel, created_at=datetime.now(), description=u"扣款成功。下一步：等待包裹到达处理中心")
                            results.append({
                                        'success':True,
                                        'yid':parcel.yid,
                                        'yde_number':parcel.yde_number,
                                        'tracking_number':numbers['tracking_number'],
                                        'retoure_tracking_number':numbers['retoure_tracking_number']
                                        })
                        else:
                            # 未正确生成相应单号，退回扣款
                            user.userprofile.deposit_increase(fee_to_book, parcel.yde_number, u"国际邮单。订单号：" + parcel.yde_number)
########################################################
                            parcel.booked_fee = fee-fee_to_book
                            parcel.save()
########################################################
                            results.append({
                                        'success':False,
                                        'yid':parcel.yid,
                                        'yde_number':parcel.yde_number,
                                        'msg':numbers['msg'],
                                        })


                    else:
                        # 扣款不成功
                        results.append({'success':False,
                                        'yid':parcel.yid,
                                        'yde_number':parcel.yde_number,
                                        'msg':"余额不足，请充值后再试"
                                        })
                    parcel.save()
                return results
    except Exception as e:
        logger.exception('')
        # logger.error(e)
        results.append({'success':False,
                        'yid':"",
                        'yde_number':"",
                        'msg':u"非常抱歉，我们遇到了系统错误,烦请联系客服"
                        })
        return results
@json_response
@secure_required
@login_required
def json_import_intl_parcel(request):
    logger.info('')
    if request.method == 'POST':
        type_code = request.POST.get('type_code', 'yd').strip()
        cn_customs_paid_by = request.POST.get('cn_customs_paid_by', 'receiver').strip()
        upload_file = request.FILES.get('file')
        parcel_infos, parcel_errors = get_parcel_infos_from_excel(upload_file.read())
        if parcel_errors:
            return {'success':False, 'parcel_errors':parcel_errors}
        if not parcel_infos:
            return {'success':False, 'parcel_errors':[{'row_no':'000', 'errors':{'file_error':['服务器未读取到任何数据：文件格式错误或者内容为空。']}}]}
        is_valid = True
        parcel_errors = []
        forms = []
        for key in parcel_infos.keys():
            parcel_info = parcel_infos[key]
            parcel_info['type_code'] = type_code
            parcel_info['cn_customs_paid_by'] = cn_customs_paid_by
            parcel_form = IntlParcelForm(parcel_info)
            if not parcel_form.is_valid():
                is_valid = False
                parcel_errors.append({'row_no':parcel_info['row_no'],
                                      'errors':parcel_form.errors
                                      })
            goodsdetail_forms = []
            for goodsdetail_info in parcel_info['goodsdetails']:
                gd_form = ParcelDetailForm(goodsdetail_info)
                if not gd_form.is_valid():
                    is_valid = False
                    parcel_errors.append({'row_no':goodsdetail_info['row_no'],
                                          'errors':gd_form.errors
                                      })
                goodsdetail_forms.append(gd_form)

            forms.append({
                          'parcel_form':parcel_form,
                          'goodsdetail_forms':goodsdetail_forms
                          })

        if is_valid:

            user_id = request.session.get('_auth_user_id')
            user = User.objects.get(id=user_id)
            currency_type = user.userprofile.deposit_currency_type
            type = ParcelType.objects.get(code=type_code)
            # #get price level
            default_level = Level.objects.get(code="default")
            level = user.userprofile.level or default_level
            try:
                price_level = PriceLevel.objects.get(level=level,
                                                   currency_type=currency_type,
                                                   parcel_type=type)
            except PriceLevel.DoesNotExist:
                price_level = PriceLevel.objects.get(level=default_level,
                                                   currency_type=currency_type,
                                                   parcel_type=type)
            json_prices = price_level.json_prices
            for parcel_form in forms:
                # create parcel
                parcel = parcel_form['parcel_form'].save(commit=False)
                parcel.user_id = user_id
                parcel.type = type
                parcel.currency_type = currency_type
                parcel.json_prices = json_prices
                parcel.save()
                parcel.yid = hashlib.md5("intlparcel%d" % parcel.id).hexdigest()
                parcel.save()
                parcel.get_sfz_status()

                for detail_form in parcel_form['goodsdetail_forms']:
                    detail = detail_form.save(commit=False)
                    detail.intl_parcel = parcel
                    detail.save()

            return {'success':True}
        else:
            return {'success':False, 'parcel_errors':parcel_errors}


    return parcel_infos


@json_response
@secure_required
@login_required
def json_remove_intl_parcel(request):
    logger.info('')
    if request.method == 'POST':
        results = []
        user_id = request.session.get('_auth_user_id')
        yids = request.POST.get('yids', False)
        p = re.compile(u'^[a-zA-Z0-9\+]+$')
        if yids and p.match(yids):
            yids = yids.split('+')
            for yid in yids:
                try:
                    parcel = IntlParcel.objects.get(yid=yid, user_id=user_id, status='draft')
                    parcel.is_deleted = True
                    parcel.save()
                    results.append({'yid':yid})
                except IntlParcel.DoesNotExist:
                    pass  # TODO make log
            return results
@json_response
@secure_required
@login_required
def json_search_intl_parcel(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')

    if request.method == 'GET':
        q = IntlParcel.objects.filter(user_id=user_id, is_deleted=False)
        page = int(request.GET.get('page', 1) or 1)
        rows = int(request.GET.get('rows', 10) or 10)
        if page < 1:
            page = 1
        if rows < 1:
            rows = 10
        s = request.GET.get('s', False)
        if s:
            q = q.filter(Q(yde_number__icontains=s) |
                           Q(tracking_number__icontains=s) |
                           Q(retoure_tracking_number__icontains=s) |
                           Q(sender_name__icontains=s) |
                           Q(sender_company__icontains=s) |
                           Q(sender_city__icontains=s) |
                           Q(sender_postcode__icontains=s) |
                           Q(sender_tel__icontains=s) |
                           Q(sender_street__icontains=s) |
                           Q(receiver_name__icontains=s) |
                           Q(receiver_company__icontains=s) |
                           Q(receiver_province__icontains=s) |
                           Q(receiver_city__icontains=s) |
                           Q(receiver_address__icontains=s) |
                           Q(receiver_mobile__icontains=s) |
                           Q(ref__icontains=s)
                           )
        else:
            sender_name = request.GET.get('sender_name', False)
            sender_company = request.GET.get('sender_company', False)
            sender_city = request.GET.get('sender_city', False)
            sender_postcode = request.GET.get('sender_postcode', False)
            sender_tel = request.GET.get('sender_tel', False)
            sender_street = request.GET.get('sender_street', False)

            receiver_name = request.GET.get('receiver_name', False)
            receiver_company = request.GET.get('receiver_company', False)
            receiver_province = request.GET.get('receiver_province', False)
            receiver_city = request.GET.get('receiver_city', False)
            receiver_address = request.GET.get('receiver_address', False)
            receiver_mobile = request.GET.get('receiver_mobile', False)

            ref = request.GET.get('ref', False)
            cn_customs_paid_by = request.GET.get('cn_customs_paid_by', False)
            type_code = request.GET.get('type_code', False)
            status = request.GET.get('status', False)
            number = request.GET.get('number', False)


            if sender_name:
                q = q.filter(sender_name__icontains=sender_name)
            if sender_company:
                q = q.filter(sender_company__icontains=sender_company)
            if sender_city:
                q = q.filter(sender_city__icontains=sender_city)
            if sender_postcode:
                q = q.filter(sender_postcode__icontains=sender_postcode)
            if sender_tel:
                q = q.filter(sender_tel__icontains=sender_tel)
            if sender_street:
                q = q.filter(sender_street__icontains=sender_street)
            if receiver_name:
                q = q.filter(receiver_name__icontains=receiver_name)
            if receiver_company:
                q = q.filter(receiver_company__icontains=receiver_company)
            if receiver_province:
                q = q.filter(receiver_province__icontains=receiver_province)
            if receiver_city:
                q = q.filter(receiver_city__icontains=receiver_city)
            if receiver_address:
                q = q.filter(receiver_address__icontains=receiver_address)
            if receiver_mobile:
                q = q.filter(receiver_mobile__icontains=receiver_mobile)
            if ref:
                q = q.filter(ref__icontains=ref)
            if cn_customs_paid_by:
                q = q.filter(cn_customs_paid_by=cn_customs_paid_by)
            if type_code:
                try:
                    type = ParcelType.objects.get(code=type_code)
                    q = q.filter(type_id=type.id)
                except ParcelType.DoesNotExist:
                    q = q.filter(type_id=0)
            if status:
                q = q.filter(status=status)
            if number:
                q = q.filter(Q(yde_number__icontains=number) |
                           Q(tracking_number__icontains=number) |
                           Q(retoure_tracking_number__icontains=number))

        results = {}
        count = q.count()
        results['count'] = count or 0
        if count == 0:
            results['parcels'] = []
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
        tz = getattr(settings, 'TIME_ZONE', 'Asia/Shanghai')
        local = pytz.timezone(tz)
        results['parcels'] = []
        for parcel in q.order_by('-created_at')[start:end]:
            results['parcels'].append(get_parcel_info(parcel, local))

        return results


class IntlParcelPdfView(PDFTemplateView):
    filename = "intl-parcel-label.pdf"
    template_name = 'parcel/intl_parcel_label.html'
    cmd_options = {
        'orientation': 'landscape',
        'checkbox-checked-svg': '/srv/django/checkbox2.svg',
        'checkbox-svg':'/srv/django/checkbox3.svg',
        'no-outline':True,  # 不产生index
        # 'collate': True,
 #       'quiet': False,
    }
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(IntlParcelPdfView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(IntlParcelPdfView, self).get_context_data(*args, **kwargs)
        if self.request.method == 'POST':
            yids = self.request.POST.get('yids', '')
        elif self.request.method == 'GET':
            yids = self.request.GET.get('yids', '')

        logger.info(self.request.method)
        logger.info(yids)

        if self.request.GET.get('wsm', ''):
            logger.info('GET ?')
            self.cmd_options = {
                #'orientation': 'landscape',
                'checkbox-checked-svg': '/srv/django/checkbox2.svg',
                'checkbox-svg':'/srv/django/checkbox3.svg',
                'no-outline':True,  # 不产生index
                'page-size':'A5',
                'margin-top':1,
                #'margin-right':1,
                'margin-bottom':1,
                #'margin-left':1,
                # 'collate': True,
                # 'quiet': None,
            }
            self.template_name = 'parcel/intl_parcel_label_no_shuoming.html'

        yids = yids.split('.')
        user_id = self.request.session.get('_auth_user_id')
        user = User.objects.get(id=user_id)
        parcels = IntlParcel.objects.filter(yid__in=yids,
                                    status__in=['confirmed',
                                               'proccessing_at_yde',
                                               'transit_to_destination_country',
                                               'custom_clearance_at_destination_country',
                                                'distributing_at_destination_country',
                                                'distributed_at_destination_country',
                                                'error',
                                               ],
                                    is_deleted=False,
                                    ).order_by("yde_number")
        if not user.is_staff:
            parcels = parcels.filter(user_id=user_id)
        logger.info(parcels)
        for parcel in parcels:
            logger.info(parcel.printed_at)
            if not parcel.printed_at:
                parcel.printed_at = datetime.now()
                parcel.save()

        if parcels.count() > 0:
            context.update({'parcels':parcels})
        else:
            raise Http404('No retoure label found!')

        view = context['view']
        view.show_content_in_browser = True
        context.update({'view': view})

        logger.info(dir(view))
        logger.info(view.show_content_in_browser)
        # logger.info(view.get_context_data())
        # logger.info(view.header_template)

        return context
    def post(self, request, *args, **kwargs):
        logger.info("function");
        return super(IntlParcelPdfView, self).get(request, *args, **kwargs)

class IntlParcelCustomsPdfView(PDFTemplateView):
    filename = "intl-parcel-customs-label.pdf"
    template_name = 'parcel/intl_parcel_customs_label.html'
    cmd_options = {
        'orientation': 'portrait',
        'no-outline':True,  # 不产生index
        # 'checkbox-checked-svg': '/home/lilee/Dropbox/Software_Project/yunda_web_app/parcel/templates/parcel/checkbox2.svg',
        # 'checkbox-svg':'/home/lilee/Dropbox/Software_Project/yunda_web_app/parcel/templates/parcel/checkbox3.svg',
        # 'collate': True,
        # 'quiet': None,
    }
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(IntlParcelCustomsPdfView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        try:
            context = super(IntlParcelCustomsPdfView, self).get_context_data(*args, **kwargs)
            if self.request.method == 'POST':
                yids = self.request.POST.get('yids', '')
            elif self.request.method == 'GET':
                yids = self.request.GET.get('yids', '')
            yids = yids.split('.')
            user_id = self.request.session.get('_auth_user_id')
            user = User.objects.get(id=user_id)
            parcels = IntlParcel.objects.filter(yid__in=yids,
                                        status__in=['confirmed',
                                                   'proccessing_at_yde',
                                                   'transit_to_destination_country',
                                                   'custom_clearance_at_destination_country',
                                                    'distributing_at_destination_country',
                                                    'distributed_at_destination_country',
                                                    'error',
                                                   ],
                                        is_deleted=False,
                                        ).order_by("yde_number")
            if not user.is_staff:
                parcels = parcels.filter(user_id=user_id)
    #             parcels = []
    #             for parcel in qs:
    #                 parcels.append(parcel)
    #                 if not parcel.printed_at:
    #                     parcel.printed_at = datetime.now()
    #                     parcel.save()
            # #
            #for parcel in parcels.filter(export_proof_created_at__isnull=True):
            #    parcel.export_proof_created_at = datetime.now()
            #    parcel.save()

            if parcels.count() > 0:
                context.update({'parcels':parcels})
            else:
                raise Http404('No parcel found!')

            view = context['view']
            logger.info(dir(view))
            # logger.info(view.get_context_data())
            logger.info(view.header_template)
            logger.info(view.footer_template)

            return context
        except Exception as e:
            logger.error(e)
    def post(self, request, *args, **kwargs):
        return super(IntlParcelCustomsPdfView, self).get(request, *args, **kwargs)

class IntlParcelAusfuhrbescheinigungPdfView(PDFTemplateView):
    filename = "Ausfuhrbescheinigung.pdf"
    template_name = 'parcel/intl_parcel_export_proof.html'
    header_template = 'parcel/header.html'
    footer_template = 'parcel/footer.html'
    cmd_options = {
        'orientation': 'portrait',
        'no-outline':True,  # 不产生index
        # 'checkbox-checked-svg': '/home/lilee/Dropbox/Software_Project/yunda_web_app/parcel/templates/parcel/checkbox2.svg',
        # 'checkbox-svg':'/home/lilee/Dropbox/Software_Project/yunda_web_app/parcel/templates/parcel/checkbox3.svg',
        # 'collate': True,
        # 'quiet': None,
    }
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(IntlParcelAusfuhrbescheinigungPdfView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(IntlParcelAusfuhrbescheinigungPdfView, self).get_context_data(*args, **kwargs)
        if self.request.method == 'POST':
            yids = self.request.POST.get('yids', '')
        elif self.request.method == 'GET':
            yids = self.request.GET.get('yids', '')
        yids = yids.split('.')
        user_id = self.request.session.get('_auth_user_id')
        user = User.objects.get(id=user_id)
        parcels = IntlParcel.objects.filter(yid__in=yids,
#                                     status__in=[
#                                                'transit_to_destination_country',
#                                                'custom_clearance_at_destination_country',
#                                                 'distributing_at_destination_country',
#                                                 'distributed_at_destination_country',
#                                                ],
                                    is_deleted=False,).exclude(mawb__isnull=True)
        logger.error("##############")
        logger.error(parcels.count())
        logger.error(user.is_staff)
        if not user.is_staff:
            parcels = parcels.filter(user_id=user_id)
#             parcels = []
#             for parcel in qs:
#                 parcels.append(parcel)
#                 if not parcel.printed_at:
#                     parcel.printed_at = datetime.now()
#                     parcel.save()

        if parcels.count() > 0:
            for parcel in parcels:
                if not parcel.export_proof_printed_at:
                    parcel.export_proof_printed_at=datetime.now()
                    parcel.save()
            context.update({'parcels':parcels})
        else:
            raise Http404('No parcel found!')

        return context
    def post(self, request, *args, **kwargs):
        return super(IntlParcelAusfuhrbescheinigungPdfView, self).get(request, *args, **kwargs)


@json_response
@secure_required
@staff_member_required
def admin_panel_json_after_scan_parcel_retoure(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')
    yde_number = request.GET.get('yde_number', False)
    oc_name = request.GET.get('oc_name', u"德国法兰克福处理中心")
    if not yde_number:
        return {'success':False, 'msg':'No yde number'}
    if not oc_name:
        return {'success':False, 'msg':'No operation center name'}
    try:
        parcel = IntlParcel.objects.get(yde_number=yde_number)
        parcel_infos = get_parcel_info(parcel)

        parcel_infos['real_weight_kg'] = parcel.real_weight_kg
        parcel_infos['real_length_cm'] = parcel.real_length_cm
        parcel_infos['real_width_cm'] = parcel.real_width_cm
        parcel_infos['real_height_cm'] = parcel.real_height_cm
        parcel_infos['cn_customs'] = parcel.get_cn_customs()

        parcel_infos['receiver_name_en'] = parcel.get_receiver_name_en()
        parcel_infos['receiver_company_en'] = parcel.get_receiver_company_en()
        parcel_infos['receiver_province_en'] = parcel.get_receiver_province_en()
        parcel_infos['receiver_city_en'] = parcel.get_receiver_city_en()
        parcel_infos['receiver_district_en'] = parcel.get_receiver_district_en()
        parcel_infos['receiver_address_en'] = parcel.get_receiver_address_en()
        parcel_infos['receiver_address2_en'] = parcel.get_receiver_address2_en()
        if "yd" in parcel.type.code:
            parcel_infos['pdf_info'] = parcel.pdf_info
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
        History.objects.create(
                               intl_parcel=parcel,
                               description=u"到达：%s 已扫描" % oc_name or u"欧洲公司",
                               visible_to_customer=True,
                               staff_id=user_id,
                               )
        return {'success':True,
                'is_parcel':True,
                'infos':parcel_infos
                }

    except IntlParcel.DoesNotExist:
        try:
            retoure = DhlRetoureLabel.objects.get(retoure_yde_number=yde_number)
            infos = get_retoure_info(retoure)
            RetoureHistory.objects.create(
                                   retoure=retoure,
                                   description=u"到达：%s 回邮包裹到达。下一步：内装包裹将会扫描并发送至目的国家" % oc_name or "欧洲公司",
                                   visible_to_customer=True,
                                   staff_id=user_id,
                                   )
            if retoure.status == "confirmed":
                retoure.status = "finished"
                retoure.save()
                return {'success':True,
                        'is_retoure':True,
                        'infos':infos,
                        'colors':{'success':True,
                            'color':COLORS['retoure_open'][COLORS['retoure_open'].keys()[0]],
                            'sign':COLORS['retoure_open'].keys()[0]}
                        }
            else:
                return {'success':True,
                        'is_retoure':True,
                        'infos':infos,
                        }

        except DhlRetoureLabel.DoesNotExist:
            return {'success':False, 'msg':'No intl. parcel or retoure label found'}
        except Exception as e:
            print e
            return {'success':False, 'msg':'System error, please inform webmaster'}

    except Exception as e:
        print e
        return {'success':False, 'msg':'System error, please inform webmaster'}

@json_response
@secure_required
@staff_member_required
def admin_panel_json_submit_retoure_second_time(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)
    oc_name = request.GET.get('oc_name', u"德国法兰克福处理中心")
    if request.method == "POST":
        waiting_return = {'success':True,
                            'color':COLORS['waiting'][COLORS['waiting'].keys()[0]],
                            'sign':COLORS['waiting'].keys()[0]}
        yid = request.POST.get('yid', False)
        if not yid:
            return {'success':False, 'msg':'No yid'}
        try:
            retoure = DhlRetoureLabel.objects.get(yid=yid)
            fee = retoure.price
            (success, msg) = retoure.user.userprofile.deposit_deduct(fee, retoure.retoure_yde_number, u"回邮单。订单号：" + retoure.retoure_yde_number)
            if not success:
                write_new_subject_to_customer(retoure.user.id,
                                                  u"包裹延迟，余额不足",
                                                  u"亲爱的客户，\n由于重复使用回邮单，且余额不足，回邮单%s内包裹暂时不能发往目的国。为保证包裹能尽快发往目的国，请尽快充值。" % (retoure.retoure_yde_number,
                                                                                                                                                    ),
                                                  user.get_full_name()
                                                )
                RetoureHistory.objects.create(retoure=retoure,
                                   description=u"重复使用回邮单。扣款不成功。",
                                   visible_to_customer=True,
                                   staff_id=user_id
                                   )
                return waiting_return
            else:
                RetoureHistory.objects.create(retoure=retoure,
                                   description=u"重复使用回邮单。扣款成功。",
                                   visible_to_customer=True,
                                   staff_id=user_id
                                   )
                return {'success':True,
                            'color':COLORS['retoure_open'][COLORS['retoure_open'].keys()[0]],
                            'sign':COLORS['retoure_open'].keys()[0]}
        except DhlRetoureLabel.DoesNotExist:
            return {'success':False, 'msg':'Retoure label does not exist'}


@json_response
@secure_required
@staff_member_required
def admin_panel_json_submit_parcel(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)
    oc_name = request.GET.get('oc_name', u"德国法兰克福处理中心")
    if request.method == "POST":
        p = re.compile(u'^[a-zA-Z0-9\-]{1,20}$')
        mawb_number = request.POST.get('mawb_number', False)
        if not p.match(mawb_number):
            return {'success':False, 'msg':'Mawb number not valid'}
        yid = request.POST.get('yid', False)
        if not yid:
            return {'success':False, 'msg':'No yid'}
        real_weight_kg = request.POST.get('real_weight_kg', 0)
        if real_weight_kg < 0.1:
            return {'success':False, 'msg':'Real weight <0.1'}
        real_length_cm = request.POST.get('real_length_cm', 0)
        real_width_cm = request.POST.get('real_width_cm', 0)
        real_height_cm = request.POST.get('real_height_cm', 0)

        waiting_return = {'success':True,
                            'color':COLORS['waiting'][COLORS['waiting'].keys()[0]],
                            'sign':COLORS['waiting'].keys()[0]}

        try:
            parcel = IntlParcel.objects.get(yid=yid)
            if parcel.status not in ['confirmed', 'error']:
                return {'success':False, 'msg':'Parcel duplicated or something wrong'}
            parcel.real_weight_kg = float(real_weight_kg)
            if real_length_cm:
                parcel.real_length_cm = float(real_length_cm)
            if real_width_cm:
                parcel.real_width_cm = float(real_width_cm)
            if real_height_cm:
                parcel.real_height_cm = float(real_height_cm)
            parcel.save()

            # 扣款
            fee = parcel.get_real_fee()
            fee_to_book = fee - parcel.booked_fee
            # ## deduct the fee
            if fee_to_book > 0:
                (success, msg) = parcel.user.userprofile.deposit_deduct(fee_to_book, parcel.yde_number, u"国际邮单。订单号：" + parcel.yde_number)

                if not success:
                    # TODO inform customer short in deposit
                    write_new_subject_to_customer(parcel.user.id,
                                                  u"包裹延迟，余额不足",
                                                  u"亲爱的客户，\n由于余额不足，包裹%s暂时不能发往目的国。为保证包裹能尽快发往目的国，请尽快充值。\n包裹实际重量：%.1f kg, 体积： %.1f x %.1f x %.1fcm" % (parcel.yde_number,
                                                                                                                                                    parcel.real_weight_kg,
                                                                                                                                                    parcel.real_length_cm,
                                                                                                                                                    parcel.real_width_cm,
                                                                                                                                                    parcel.real_height_cm),
                                                  user.get_full_name()
                                                )
                    parcel.status = "error"
                    parcel.save()
                    History.objects.create(intl_parcel=parcel,
                                       description=u"到达：%s 包裹延迟，延迟原因已通知发件人，等待发件人回复" % oc_name,
                                       visible_to_customer=True,
                                       staff_id=user_id
                                       )
                    return waiting_return
                parcel.booked_fee = fee
                parcel.save()

            if parcel.get_sfz_status() == "2":
                # TODO inform customer no sfz
                write_new_subject_to_customer(parcel.user.id,
                                                  u"包裹延迟，未上传身份证图片",
                                                  u"亲爱的客户，\n根据中国海关规定，韵达自营小包裹需要收件人身份证图片，包裹%s暂时不能发往目的国。为保证包裹能尽快发往目的国，请尽快上传身份证图片。\n\n<a target='_blank' href='http://yunda-express.eu/shenfenzheng/?name=%s&mobile=%s'><u>++点击这里直接上传身份证++</u></a>" \
                                                  % (parcel.yde_number, parcel.receiver_name, parcel.receiver_mobile),
                                                  user.get_full_name()
                                                )
                # TODO inform receiver no sfz
                parcel.status = "error"
                parcel.save()
                History.objects.create(intl_parcel=parcel,
                                       description=u"到达：%s 包裹延迟，等待上传身份证" % oc_name,
                                       visible_to_customer=True,
                                       staff_id=user_id
                                       )
                return waiting_return

            color, sign = add_to_mawb(mawb_number, yid,
                                    parcel.receiver_name + parcel.receiver_mobile,
                                    parcel.sender_name + parcel.sender_tel,
                                    parcel.get_total_value())
            if color:
                if parcel.status in ["confirmed"]:
                    if "yd" in parcel.type.code:
                        description = u"到达：%s 下一步，出口清关" % oc_name
                    else:
                        description = u"包裹到达韵达欧洲处理中心。下一步：包裹运往韵达合作伙伴处理中心"
                elif parcel.status in ['error']:
                    if "yd" in parcel.type.code:
                        description = u"到达：%s 包裹状态正常。下一步，出口清关" % oc_name
                    else:
                        description = u"包裹状态正常。下一步：包裹运往韵达合作伙伴处理中心"
                History.objects.create(intl_parcel=parcel,
                                       description=description,
                                       visible_to_customer=True,
                                       staff_id=user_id
                                       )
                parcel.status = "proccessing_at_yde"
                parcel.save()
                return {'success':True, 'color':color, 'sign':sign}
            else:
                parcel.status = "error"
                parcel.save()
                History.objects.create(intl_parcel=parcel,
                                       description=u"到达：%s 出口清关延迟" % oc_name,
                                       visible_to_customer=True,
                                       staff_id=user_id
                                       )
                return waiting_return

        except IntlParcel.DoesNotExist:
            return {'success':False, 'msg':'Intl. parcel does not exist'}

def get_mawb_info(mawb):
    logger.info('')
    mawb_info = {
               'mawb_number':mawb.mawb_number,
               'cn_customs':mawb.cn_customs,
               'need_receiver_name_mobiles':mawb.need_receiver_name_mobiles,
               'need_total_value_per_sender':mawb.need_total_value_per_sender,
               'status':mawb.status,
               'status_display':mawb.get_status_display(),
               'id':mawb.id,
               'batches':[],
               }
    for batch in mawb.batches.all():
        batch_info = {
                    'order_number':batch.order_number,
                    'sign':batch.sign,
                    'color':batch.color,
                    'max_value':batch.max_value
                    }
        mawb_info['batches'].append(batch_info)
    return mawb_info

COLORS = {
                "dhl":{'car':'#FF9900',  # orange
                       },
                'postnl':{'tree':'#008000',  # green
                          },
                "ctu":{ 'star':'#00FFFF',  # aqua-
                        'flash':'#808080',  # gray-
                        'key':'#800000',  # maroon-
                        'apple':'#808000',  # olive-
                        },
                "default":{'envelope':'#0000FF',  # blue-
                           'umbrella':'#000080',  # navy-
                           'camera':'#FF00FF',  # magenta-
                           'glass':'#800080',  # purple-
                           },
                'waiting':{'plane':'#000000',  # black-
                           },
                'error':{'times':'#FF0000',  # red
                         },
                'retoure_open':{'unlock':'#EE0000',  #
                         },
                }
@json_response
@secure_required
@staff_member_required
def admin_panel_available_mawbs(request):
    logger.info('')
    #cn_customses = ['dhl', 'postnl', 'ctu', 'default']
    cn_customses = ['dhl',  'ctu', 'default']

    mawb_infos = {}
    for cn_customs in cn_customses:
        mawbs = Mawb.objects.filter(status="warehouse_open", cn_customs=cn_customs)
        infos = []
        for mawb in mawbs:
            infos.append(get_mawb_info(mawb))
        mawb_infos[cn_customs] = infos

    return {'mawbs':mawb_infos,
            'colors':COLORS,
            }

@json_response
@secure_required
@staff_member_required
def admin_panel_get_colors(request):
    logger.info('')
    return COLORS

@json_response
@secure_required
@staff_member_required
def admin_panel_post_mawbs(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')
    if request.method == "POST":
        p = re.compile(u'^[a-zA-Z0-9\-]{1,20}$')
        mawb_number = request.POST.get('mawb_number', False)
        if not p.match(mawb_number):
            return {'success':False, 'msg':'Mawb number not valid'}
        cn_customs = request.POST.get('cn_customs', False)
        if not p.match(cn_customs):
            return {'success':False, 'msg':'CN customs code not valid'}


        msg = []
        mawb_form = MawbForm(request.POST)
        is_valid = True
        batch_forms = []
        if not mawb_form.is_valid():
            is_valid = False
            msg.append(mawb_form.errors)

        for i in range(0, int(request.POST.get('batch_num', 0))):
            dict = {
                  'order_number':request.POST.get('order_number-' + str(i), ''),
                  'sign':request.POST.get('sign-' + str(i), ''),
                  'color':request.POST.get('color-' + str(i), ''),
                  'max_value':request.POST.get('max_value-' + str(i), 0),
                  }
            batch_form = BatchForm(dict)
            if batch_form.is_valid():
                batch_forms.append(batch_form)
            else:
                is_valid = False
                msg.append(batch_form.errors)
        if is_valid:
            mawb = mawb_form.save()
            # mawb.status = "warehouse_open"
            mawb.receiver_name_mobiles = []
            mawb.save()
            for batch_form in batch_forms:
                batch = batch_form.save(commit=False)
                batch.mawb = mawb
                batch.total_value_per_sender = {}
                batch.yids = []
                batch.save()
            return {'success':True,
                    'mawb':get_mawb_info(mawb),
                    }
        else:
            return {'success':False, 'msg':msg}

@json_response
@secure_required
@staff_member_required
def admin_panel_search_mawbs(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')

    if request.method == 'GET':
        q = Mawb.objects
        page = int(request.GET.get('page', 1))
        rows = int(request.GET.get('rows', 10))

        s = request.GET.get('s', False)
        if s:
            s = s.strip()
            q = q.filter(Q(mawb_number__icontains=s) | Q(number__icontains=s))
        cn_customs = request.GET.get('cn_customs', False)
        if cn_customs:
            q = q.filter(cn_customs__icontains=cn_customs)
        status = request.GET.get('status', False)
        if status:
            q = q.filter(status__icontains=status)

        results = {}
        count = q.count()
        results['count'] = count or 0
        results['mawbs'] = []
        results['colors'] = COLORS
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
        tz = getattr(settings, 'TIME_ZONE', 'Europe/Berlin')
        local = pytz.timezone(tz)
        for mawb in q.order_by('-created_at')[start:end]:
            results['mawbs'].append({
                                        'mawb_number':mawb.mawb_number,
                                        'cn_customs':mawb.cn_customs,
                                        'need_receiver_name_mobiles':mawb.need_receiver_name_mobiles,
                                        'need_total_value_per_sender':mawb.need_total_value_per_sender,
                                        'created_at':mawb.created_at.astimezone(local).strftime("%Y-%m-%d %H:%M"),
                                        'status':mawb.status,
                                        'status_display':mawb.get_status_display(),
                                        'id':mawb.id,
                                    })

        return results

@json_response
@secure_required
@staff_member_required
def json_get_mawb(request, id):
    logger.info('')
    user_id = request.session.get('_auth_user_id')

    if id:
        try:
            mawb = Mawb.objects.get(id=id)
            tz = getattr(settings, 'TIME_ZONE', 'Europe/Berlin')
            local = pytz.timezone(tz)
            result = {
                        'mawb_number':mawb.mawb_number,
                        'cn_customs':mawb.cn_customs,
                        'need_receiver_name_mobiles':mawb.need_receiver_name_mobiles,
                        'need_total_value_per_sender':mawb.need_total_value_per_sender,
                        'created_at':mawb.created_at.astimezone(local).strftime("%Y-%m-%d %H:%M"),
                        'status':mawb.status,
                        'status_display':mawb.get_status_display(),
                        'id':mawb.id,
                        'histories':mawb.histories,
                        'number':mawb.number or "",
                    }


            batches = []
            for batch in mawb.batches.order_by('order_number').all():
                batches.append({
                                'order_number':batch.order_number,
                                'sign':batch.sign,
                                'color':batch.color,
                                'total_value_per_sender':batch.total_value_per_sender,
                                'max_value':batch.max_value,
                                'yids':batch.yids,
                                'status':batch.status,
                                'status_display':batch.get_status_display(),
                                'id':batch.id,
                                })
            result['batches'] = batches

            return {"state":'success', "mawb":result}



        except Mawb.DoesNotExist:
            return dict(state="error", msg=u"Mawb does not exist")

_excel_column = {
    'xuhao':0,
    'fendanhao':1,
    'shxingming':2,
    'shdizhi':3,
    'shdianhua':4,
    'shzhengjianhao':5,
    'wupingmingcheng':9,
    'shuliang':10,
    'danjia':11,
    'shuihao':12,
    'shuilv':13,
    'jianshu':14,
    'zhongliang':15
        }
@secure_required
@staff_member_required
def get_mawb_haiguan_excel(request, id):
    logger.info('')
    user_id = request.session.get('_auth_user_id')
    batch_id = request.GET.get('batch_id', '').strip()
    if id:
        try:
            mawb = Mawb.objects.get(id=id, cn_customs__in=['ctu', 'default'])
            if mawb.cn_customs in ["default","ctu","can-wtd"]:
                return _haiguan_excel_can_wtd(mawb, batch_id)
            else:
                return ""



        except Mawb.DoesNotExist:
            return HttpResponse(u"MAWB does not exist")
        except Exception as e:
            logger.error(e)
            return HttpResponse(u"%s" % e)

@secure_required
@staff_member_required
def get_mawb_dhl_lieferschein(request, id):
    logger.info('')
    user_id = request.session.get('_auth_user_id')

    if id:
        try:
            mawb = Mawb.objects.get(id=id, cn_customs__icontains="dhl")
            parcels = IntlParcel.objects.filter(yid__in=mawb.yids)
            for parcel in parcels:
                pass


        except Mawb.DoesNotExist:
            return dict(state="error", msg=u"Mawb does not exist")

@secure_required
@staff_member_required
def get_mawb_dhl_3d_file(request, id):
    logger.info('')
    user_id = request.session.get('_auth_user_id')

    if id:
        try:
            mawb = Mawb.objects.get(id=id, cn_customs__icontains="dhl")
            parcels = IntlParcel.objects.filter(yid__in=mawb.yids)
            for parcel in parcels:
                pass


        except Mawb.DoesNotExist:
            return dict(state="error", msg=u"Mawb does not exist")


@secure_required
@staff_member_required
def get_batch_manifest_excel(request, id):
    logger.info('')
    user_id = request.session.get('_auth_user_id')
    if id:
        try:
            batch = Batch.objects.get(id=id)
            parcels = IntlParcel.objects.filter(yid__in=batch.yids).order_by("yde_number")
            book = Workbook(encoding='utf8')
            sheet1 = book.add_sheet('Sheet 1')

            batch_total_weight = 0
            current_row = 11
            for shipment in parcels:
                detail_text = u""
                for detail in shipment.goodsdetails.all():
                    detail_text += u"%s %d X %.3fkg /%.2fEUR\n" % ((detail.description or u""),
                                                                 (detail.qty or 0),
                                                                 (detail.item_net_weight_kg or 0.1),
                                                                 ((detail.qty or 1) * (detail.item_price_eur or 1)))
                sender_add = u"%s\n%s %s\n%s %s, Germany\nTel.: %s" % (shipment.sender_name or u"",
                                                           shipment.sender_street or u"",
                                                           shipment.sender_hause_number or u"",
                                                           shipment.sender_postcode or u"",
                                                           shipment.sender_city or u"",
                                                           shipment.sender_tel or u"",
                                                           )
                sheet1.write_merge(current_row, current_row + 1, 1, 1, shipment.yde_number + "\nTracking#" + (shipment.tracking_number or u''))
                sheet1.write_merge(current_row, current_row + 1, 2, 2, u'1')
                sheet1.write_merge(current_row, current_row + 1, 3, 3, u'%.3f' % shipment.real_weight_kg)
                sheet1.write_merge(current_row, current_row + 1, 4, 4, shipment.sender_city + u",DE/" + \
                                   (shipment.get_receiver_province_en() or u'') + u" " + \
                                   (shipment.get_receiver_city_en() or u'') + ",CN")
                sheet1.write_merge(current_row, current_row + 1, 5, 5, u'PPD')
                sheet1.write(current_row, 6 , u"Shipper")
                sheet1.write(current_row + 1, 6 , u"Consignee")
                sheet1.write_merge(current_row, current_row, 7, 8 , sender_add)
                sheet1.write_merge(current_row + 1, current_row + 1, 7, 8 , (shipment.get_receiver_name_en() or u"") + u"\n" + \
                                   (shipment.get_receiver_district_en() or u"") + u" " + (shipment.get_receiver_address_en() or u"")
                                   + u"\nTel.: "
                                   + (shipment.receiver_mobile or u""))
                sheet1.write_merge(current_row, current_row + 1, 9, 9, detail_text)
                current_row += 2

            # write the head
            sheet1.write(1, 1, u'Consolidation Manifest')
            sheet1.write_merge(1, 1, 7, 8, batch.mawb.mawb_number + str(batch.order_number) or u"")
            sheet1.write(2, 1, batch.mawb.created_at.strftime("%d.%m.%Y"))
            sheet1.write(3, 1, u"Carrier")
            sheet1.write(3, 2, u"")
            sheet1.write(4, 1, u"Shipper")
            sheet1.write_merge(4, 4, 2, 6, u"")
            sheet1.write(5, 1, u"Origin")
            sheet1.write(5, 2, u"")
            sheet1.write(6, 1, u"Destination")
            sheet1.write(6, 2, u"")
            sheet1.write(7, 1, u"Flight")
            sheet1.write(7, 2, u"")
            sheet1.write(8, 1, u"HAWBs")
            sheet1.write(8, 2, len(batch.yids) or 0)

            sheet1.write(4, 7, u"Consignee")
            sheet1.write_merge(4, 4, 8, 9, u"")
            sheet1.write(5, 7, u"MAWB")
            sheet1.write(5, 8, batch.mawb.mawb_number or u"")
            sheet1.write(6, 7, u"Pieces")
            sheet1.write(6, 8, len(batch.yids) or 0)
            sheet1.write(7, 7, u"Weight")
            sheet1.write(7, 8, u"%.3fK" % (batch_total_weight or 0))

            sheet1.write(10, 1, u"HAWB")
            sheet1.write(10, 2, u"Pieces")
            sheet1.write(10, 3, u"Weight")
            sheet1.write(10, 4, u"Orig/Dest")
            sheet1.write(10, 5, u"PPD/COLL")
            sheet1.write(10, 9, u"Details")

            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=%s.xls' % (batch.mawb.mawb_number + str(batch.order_number))
            book.save(response)
            return response


        except Mawb.DoesNotExist:
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=empty.xls'
            return response

@json_response
@secure_required
@staff_member_required
def json_remove_mawb(request):
    logger.info('')
    if request.method == 'POST':
        results = []
        ids = request.POST.get('ids', False)
        p = re.compile(u'^[0-9\+]+$')
        if ids and p.match(ids):
            ids = ids.split('+')
            for id in ids:
                try:
                    mawb = Mawb.objects.get(id=id, status='draft')
                    mawb.delete()
                    results.append({'id':id})
                except Mawb.DoesNotExist:
                    pass  # TODO make log
            return results


@json_response
@secure_required
@staff_member_required
def json_mawb_change_status(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)
    user_name = user.get_full_name()
    oc_name = request.GET.get('oc_name', u"德国法兰克福处理中心")

    if request.method == 'POST':
        status = request.POST.get('status', False)
        year = request.POST.get('year', False)
        month = request.POST.get('month', False)
        day = request.POST.get('day', False)
        hour = request.POST.get('hour', False)
        minute = request.POST.get('minute', False)
        second = request.POST.get('second', False)
        if (not year) or (not month) or (not day) or (not hour) or (not minute) or (not second) or status in ["warehouse_open","warehouse_closed"]:
            changed_at = datetime.now()
        else:
            changed_at = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
            if changed_at > datetime.now():
                return {'success':False}


        id = request.POST.get('id', False)
        p = re.compile(u'^[0-9]+$')
        if id and p.match(id) and status:
            if status == "warehouse_open":
                try:
                    mawb = Mawb.objects.get(id=id, status='draft')
                    mawb.status = status
                    histories = mawb.histories
                    histories.append({"status":status,
                                      "status_display":mawb.get_status_display(),
                                      "datetime":changed_at.isoformat(),
                                      'staff':user_name})
                    mawb.histories = histories
                    mawb.save()
                    return {'success':True, 'status':status, 'status_display':mawb.get_status_display()}
                except Mawb.DoesNotExist:
                    # TODO make log
                    return {'success':False}
            elif status == "warehouse_closed":
                try:
                    mawb = Mawb.objects.get(id=id, status='warehouse_open')
                    mawb.status = status
                    histories = mawb.histories
                    histories.append({"status":status,
                                      "status_display":mawb.get_status_display(),
                                      "datetime":changed_at.isoformat(),
                                      'staff':user_name})
                    mawb.histories = histories
                    mawb.save()
                    return {'success':True, 'status':status, 'status_display':mawb.get_status_display()}
                except Mawb.DoesNotExist:
                    # TODO make log
                    return {'success':False}
            elif status == "transfered_to_partner":
                try:
                    mawb = Mawb.objects.get(id=id, status='warehouse_closed', cn_customs__in=['dhl', 'postnl'])
                    mawb.status = status
                    histories = mawb.histories
                    histories.append({"status":status,
                                      "status_display":mawb.get_status_display(),
                                      "datetime":changed_at.isoformat(),
                                      'staff':user_name})
                    mawb.histories = histories
                    mawb.save()
                    yids = []
                    for batch in mawb.batches.all():
                        yids += batch.yids
                    for parcel in IntlParcel.objects.filter(yid__in=yids):
                        History.objects.create(intl_parcel=parcel,
                                               description=u"包裹运送至合作公司处理中心途中",
                                               visible_to_customer=True,
                                               staff_id=user_id,
                                               )
                    return {'success':True, 'status':status, 'status_display':mawb.get_status_display()}
                except Mawb.DoesNotExist:
                    # TODO make log
                    return {'success':False}
            elif status == "flied_to_dest":
                try:
                    mawb = Mawb.objects.get(id=id, status='warehouse_closed', cn_customs__in=['ctu', 'default'])
                    mawb.status = status
                    histories = mawb.histories
                    histories.append({"status":status,
                                      "status_display":mawb.get_status_display(),
                                      "datetime":changed_at.isoformat(),
                                      'staff':user_name})
                    mawb.histories = histories
                    mawb.save()
                    yids = []
                    for batch in mawb.batches.all():
                        yids += batch.yids
                    for parcel in IntlParcel.objects.filter(yid__in=yids):
                        History.objects.create(intl_parcel=parcel,
                                               description=u"到达：%s 包裹飞往目的国家" % oc_name,
                                                visible_to_customer=True,
                                                staff_id=user_id,
                                                created_at=changed_at,
                                               )
                        parcel.exported_at = changed_at
                        parcel.save()
                    return {'success':True, 'status':status, 'status_display':mawb.get_status_display()}
                except Mawb.DoesNotExist:
                    # TODO make log
                    return {'success':False}
            elif status == "landed_at_dest":
                try:
                    mawb = Mawb.objects.get(id=id, status='flied_to_dest', cn_customs__in=['ctu', 'default'])
                    mawb.status = status
                    histories = mawb.histories
                    histories.append({"status":status,
                                      "status_display":mawb.get_status_display(),
                                      "datetime":changed_at.isoformat(),
                                      'staff':user_name})
                    mawb.histories = histories
                    mawb.save()
                    yids = []
                    for batch in mawb.batches.all():
                        yids += batch.yids
                    for parcel in IntlParcel.objects.filter(yid__in=yids):
                        History.objects.create(intl_parcel=parcel,
                                               description=u"到达：国际部 抵达目的国，下一步：目的国进口清关",
                                                visible_to_customer=True,
                                                staff_id=user_id,
                                                created_at=changed_at,
                                               )
                    return {'success':True, 'status':status, 'status_display':mawb.get_status_display()}
                except Mawb.DoesNotExist:
                    # TODO make log
                    return {'success':False}
            elif status == "customs_cleared":
                try:
                    mawb = Mawb.objects.get(id=id, status='landed_at_dest', cn_customs__in=['ctu', 'default'])
                    mawb.status = status
                    histories = mawb.histories
                    histories.append({"status":status,
                                      "status_display":mawb.get_status_display(),
                                      "datetime":changed_at.isoformat(),
                                      'staff':user_name})
                    mawb.histories = histories
                    mawb.save()
                    yids = []
                    for batch in mawb.batches.all():
                        yids += batch.yids
                    for parcel in IntlParcel.objects.filter(yid__in=yids):
                        History.objects.create(intl_parcel=parcel,
                                               description=u"到达：国际部 目的国进口清关完成。下一步：进入派送流程",
                                                visible_to_customer=True,
                                                staff_id=user_id,
                                                created_at=changed_at,
                                               )
                    return {'success':True, 'status':status, 'status_display':mawb.get_status_display()}
                except Mawb.DoesNotExist:
                    # TODO make log
                    return {'success':False}

@json_response
@secure_required
@staff_member_required
def json_batch_change_status(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)
    user_name = user.get_full_name()
    oc_name = request.GET.get('oc_name', u"德国法兰克福处理中心")
    if request.method == 'POST':
        status = request.POST.get('status', False)
        year = request.POST.get('year', False)
        month = request.POST.get('month', False)
        day = request.POST.get('day', False)
        hour = request.POST.get('hour', False)
        minute = request.POST.get('minute', False)
        second = request.POST.get('second', False)
        if (not year) or (not month) or (not day) or (not hour) or (not minute) or (not second) or status in ["warehouse_closed"]:
            changed_at = datetime.now()
        else:
            changed_at = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
            if changed_at > datetime.now():
                return {'success':False}
        id = request.POST.get('id', False)
        p = re.compile(u'^[0-9]+$')
        if id and p.match(id) and status:
            if status == "warehouse_closed":
                try:
                    batch = Batch.objects.get(id=id, status='warehouse_open')
                    batch.status = status
                    histories = batch.histories
                    histories.append({"status":status,
                                      "status_display":batch.get_status_display(),
                                      "datetime":changed_at.isoformat(),
                                      'staff':user_name})
                    batch.histories = histories
                    batch.save()
                    return {'success':True, 'status':status, 'status_display':batch.get_status_display()}
                except Batch.DoesNotExist:
                    # TODO make log
                    return {'success':False}
            elif status == "export_customs_cleared":
                try:
                    batch = Batch.objects.get(id=id, status='warehouse_closed', mawb__cn_customs__in=['ctu', 'default'])
                    batch.status = status
                    histories = batch.histories
                    histories.append({"status":status,
                                      "status_display":batch.get_status_display(),
                                      "datetime":changed_at.isoformat(),
                                      'staff':user_name})
                    batch.histories = histories
                    batch.save()
                    yids = batch.yids
                    for parcel in IntlParcel.objects.filter(yid__in=yids):
                        History.objects.create(intl_parcel=parcel,
                                               description=u"到达：%s 出口清关完成,下一步：包裹运送至目的国家" % oc_name,
                                                visible_to_customer=True,
                                                staff_id=user_id,
                                                created_at=changed_at,
                                               )
                    return {'success':True, 'status':status, 'status_display':batch.get_status_display()}
                except Batch.DoesNotExist:
                    # TODO make log
                    return {'success':False}

@json_response
@secure_required
@staff_member_required
def admin_json_search_intl_parcel(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')

    if request.method == 'GET':
        q = IntlParcel.objects.filter(is_deleted=False)
        page = int(request.GET.get('page', 1) or 1)
        rows = int(request.GET.get('rows', 10) or 10)
        if page < 1:
            page = 1
        if rows < 1:
            rows = 10
        s = request.GET.get('s', False)
        if s:
            q = q.filter(Q(yde_number__icontains=s) |
                           Q(tracking_number__icontains=s) |
                           Q(retoure_tracking_number__icontains=s) |
                           Q(sender_name__icontains=s) |
                           Q(sender_company__icontains=s) |
                           Q(sender_city__icontains=s) |
                           Q(sender_postcode__icontains=s) |
                           Q(sender_tel__icontains=s) |
                           Q(sender_street__icontains=s) |
                           Q(receiver_name__icontains=s) |
                           Q(receiver_company__icontains=s) |
                           Q(receiver_province__icontains=s) |
                           Q(receiver_city__icontains=s) |
                           Q(receiver_address__icontains=s) |
                           Q(receiver_mobile__icontains=s) |
                           Q(ref__icontains=s)
                           )

        cn_customs_paid_by = request.GET.get('cn_customs_paid_by', False)
        type_code = request.GET.get('type_code', False)
        status = request.GET.get('status', False)
        customer_number = request.GET.get('customer_number', False)
        customer_number = customer_number and customer_number.strip()
        sfz_status = request.GET.get('sfz_status', False)
        mawb_number = request.GET.get('mawb_number', False)

        if mawb_number:
            q=q.filter(Q(mawb__mawb_number__icontains=mawb_number) |
                       Q(mawb__number__icontains=mawb_number))

        if cn_customs_paid_by:
            q = q.filter(cn_customs_paid_by=cn_customs_paid_by)
        if type_code:
            try:
                parcel_type = ParcelType.objects.get(code=type_code)
                q = q.filter(type_id=parcel_type.id)
            except ParcelType.DoesNotExist:
                q = q.filter(type_id=0)
        if status:
            q = q.filter(status=status)

        if customer_number:
            try:
                customer = UserProfile.objects.get(customer_number=customer_number)
                q = q.filter(user_id=customer.user_id)
            except UserProfile.DoesNotExist:
                q = q.filter(user_id=0)
        if sfz_status:
            tmp_parcels = IntlParcel.objects.exclude(status="draft").filter(sfz_status="2")
            for tmp_parcel in tmp_parcels:
                tmp_parcel.get_sfz_status()
            q = q.filter(sfz_status=sfz_status)

        results = {}
        count = q.count()
        results['count'] = count or 0
        if count == 0:
            results['parcels'] = []
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
        tz = getattr(settings, 'TIME_ZONE', 'Europe/Berlin')
        local = pytz.timezone(tz)
        results['parcels'] = []
        for parcel in q.order_by('-created_at')[start:end]:
            parcel_info = get_parcel_info(parcel, local)
            if parcel_info['yde_number'] == u"草稿,未生成订单号":
                parcel_info['yde_number'] = "Draft"
            parcel_info['customer_number'] = parcel.user.userprofile.customer_number
            parcel_info['real_weight_kg'] = parcel.real_weight_kg
            parcel_info['real_length_cm'] = parcel.real_length_cm
            parcel_info['real_width_cm'] = parcel.real_width_cm
            parcel_info['real_height_cm'] = parcel.real_height_cm
            parcel_info['customs_code_forced'] = parcel.customs_code_forced
            parcel_info['mawb_name'] = parcel.mawb and parcel.mawb.mawb_number or ""
            parcel_info['histories'] = []
            parcel_info['goodsdetails'] = []
            for history in parcel.histories.filter(visible_to_customer=True).order_by('created_at'):
                parcel_info['histories'].append({
                    "created_at":history.created_at.astimezone(local).strftime("%Y-%m-%d %H:%M"),
                    "description":history.description, })
            for detail in parcel.goodsdetails.all():
                parcel_info['goodsdetails'].append({
                    "description":detail.description,
                    "cn_customs_tax_catalog_name":detail.cn_customs_tax_catalog_name,
                    "cn_customs_tax_name":detail.cn_customs_tax_name,
                    "qty":detail.qty,
                    "item_net_weight_kg":detail.item_net_weight_kg,
                    "item_price_eur":detail.item_price_eur, })
            results['parcels'].append(parcel_info)

        return results

_gss_moban_column = {
    'fendanbiaoshi':0,
    'miandanhao':1,
    'hezuoshang':3,
    'receiver_name1':5,
    'lianxiren':6,
    'yde_number':7,
    'receiver_country_code':8,
    'receiver_city':9,
    'receiver_postcode':10,
    'receiver_street':11,
    'receiver_mobilephone':13,
    'receiver_email':14,
    'sender_name1':16,
    'sender_country_code':17,
    'sender_city':18,
    'sender_postcode':19,
    'sender_street':21,
    'sender_telephone':23,
    'sender_email':24,
    'shifoubaoxian':27,
    'insurance':28,
    'cn_name':34,
    'cn_customnumber':35,
    'total_weight':44,
    'ref1':48,
            }
@secure_required
@staff_member_required
def admin_get_gss_excel(request):
    logger.info('')
    if request.method == "GET":
        yids = request.GET.get("yids", False)
        yids = yids and yids.strip()
        if yids:
            yids = yids.split('.')
            book = Workbook()
            sheet_ctu = book.add_sheet('CTU')
            sheet_default = book.add_sheet('Default')

            shipments = IntlParcel.objects.exclude(is_deleted=True)\
                    .filter(yid__in=yids)\
                    .filter(type__code__icontains="yd")\
                    .exclude(status="draft")\
                    .filter(Q(tracking_number__isnull=True) |
                            Q(tracking_number=""))
            shipments_ctu = []
            shipments_default = []
            for shipment in shipments:
                if shipment.get_cn_customs() == 'ctu':
                    shipments_ctu.append(shipment)
                else:
                    shipments_default.append(shipment)
            # # create ctu
            current_row = 1
            fendanbiaoshi = 1
            sheet1 = sheet_ctu
            for shipment in shipments_ctu:
                sheet1.write(current_row, _gss_moban_column['miandanhao'], shipment.tracking_number or "")
                sheet1.write(current_row, _gss_moban_column['hezuoshang'], u'xxxxxxxxxx')
                if shipment.receiver_company:
                    sheet1.write(current_row, _gss_moban_column['receiver_name1'], shipment.receiver_company)
                    sheet1.write(current_row, _gss_moban_column['lianxiren'], shipment.receiver_name)
                else:
                    sheet1.write(current_row, _gss_moban_column['receiver_name1'], shipment.receiver_name)
                    sheet1.write(current_row, _gss_moban_column['lianxiren'], shipment.receiver_name)

                sheet1.write(current_row, _gss_moban_column['yde_number'], shipment.yde_number)
                sheet1.write(current_row, _gss_moban_column['receiver_country_code'], u'中国大陆')
                sheet1.write(current_row, _gss_moban_column['receiver_city'], (shipment.receiver_province or '') + (shipment.receiver_city or '') + (shipment.receiver_district or ''))
                sheet1.write(current_row, _gss_moban_column['receiver_postcode'], shipment.receiver_postcode or u'123456')
                sheet1.write(current_row, _gss_moban_column['receiver_street'], (shipment.receiver_province or '') + (shipment.receiver_city or '') + (shipment.receiver_district or '') + (shipment.receiver_address or '') + (shipment.receiver_address2 or ''))
                sheet1.write(current_row, _gss_moban_column['receiver_mobilephone'], shipment.receiver_mobile)
                sheet1.write(current_row, _gss_moban_column['sender_name1'], shipment.sender_name)
                sheet1.write(current_row, _gss_moban_column['sender_country_code'], u'德国')
                sheet1.write(current_row, _gss_moban_column['sender_city'], shipment.sender_city or u'Moerfelden-Walldorf')
                sheet1.write(current_row, _gss_moban_column['sender_postcode'], shipment.sender_postcode or u'64546')
                sheet1.write(current_row, _gss_moban_column['sender_street'], (shipment.sender_street or '') + (shipment.sender_hause_number or ''))
                sheet1.write(current_row, _gss_moban_column['sender_telephone'], u'198168')  # 发件人电话填198168
                sheet1.write(current_row, _gss_moban_column['shifoubaoxian'], u'否')
                sheet1.write(current_row, _gss_moban_column['insurance'], 0)
                sheet1.write(current_row, _gss_moban_column['total_weight'], 1)
                sheet1.write(current_row, _gss_moban_column['ref1'], shipment.ref or '')
                for detail in shipment.goodsdetails.all():
                    sheet1.write(current_row, _gss_moban_column['fendanbiaoshi'], str(fendanbiaoshi))
                    sheet1.write(current_row, _gss_moban_column['cn_name'], detail.cn_customs_tax_name)
                    sheet1.write(current_row, _gss_moban_column['cn_customnumber'], '11111111')
                    current_row += 1
                fendanbiaoshi += 1
            # #create default
            current_row = 1
            fendanbiaoshi = 1
            sheet1 = sheet_default
            for shipment in shipments_default:
                sheet1.write(current_row, _gss_moban_column['miandanhao'], shipment.tracking_number or "")
                sheet1.write(current_row, _gss_moban_column['hezuoshang'], u'xxxxxxxxxx')
                if shipment.receiver_company:
                    sheet1.write(current_row, _gss_moban_column['receiver_name1'], shipment.receiver_company)
                    sheet1.write(current_row, _gss_moban_column['lianxiren'], shipment.receiver_name)
                else:
                    sheet1.write(current_row, _gss_moban_column['receiver_name1'], shipment.receiver_name)
                    sheet1.write(current_row, _gss_moban_column['lianxiren'], shipment.receiver_name)

                sheet1.write(current_row, _gss_moban_column['yde_number'], shipment.yde_number)
                sheet1.write(current_row, _gss_moban_column['receiver_country_code'], u'中国大陆')
                sheet1.write(current_row, _gss_moban_column['receiver_city'], (shipment.receiver_province or '') + (shipment.receiver_city or '') + (shipment.receiver_district or ''))
                sheet1.write(current_row, _gss_moban_column['receiver_postcode'], shipment.receiver_postcode or u'123456')
                sheet1.write(current_row, _gss_moban_column['receiver_street'], (shipment.receiver_province or '') + (shipment.receiver_city or '') + (shipment.receiver_district or '') + (shipment.receiver_address or '') + (shipment.receiver_address2 or ''))
                sheet1.write(current_row, _gss_moban_column['receiver_mobilephone'], shipment.receiver_mobile)
                sheet1.write(current_row, _gss_moban_column['sender_name1'], shipment.sender_name)
                sheet1.write(current_row, _gss_moban_column['sender_country_code'], u'德国')
                sheet1.write(current_row, _gss_moban_column['sender_city'], shipment.sender_city or u'Moerfelden-Walldorf')
                sheet1.write(current_row, _gss_moban_column['sender_postcode'], shipment.sender_postcode or u'64546')
                sheet1.write(current_row, _gss_moban_column['sender_street'], (shipment.sender_street or '') + (shipment.sender_hause_number or ''))
                sheet1.write(current_row, _gss_moban_column['sender_telephone'], u'198168')  # 发件人电话填198168
                sheet1.write(current_row, _gss_moban_column['shifoubaoxian'], u'否')
                sheet1.write(current_row, _gss_moban_column['insurance'], 0)
                sheet1.write(current_row, _gss_moban_column['total_weight'], 1)
                sheet1.write(current_row, _gss_moban_column['ref1'], shipment.ref or '')
                for detail in shipment.goodsdetails.all():
                    sheet1.write(current_row, _gss_moban_column['fendanbiaoshi'], str(fendanbiaoshi))
                    sheet1.write(current_row, _gss_moban_column['cn_name'], detail.cn_customs_tax_name)
                    sheet1.write(current_row, _gss_moban_column['cn_customnumber'], '11111111')
                    current_row += 1
                fendanbiaoshi += 1

            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=gss-%s.xls' % datetime.now().isoformat()
            book.save(response)
        else:
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=empty.xls'
        return response

@json_response
@secure_required
@staff_member_required
def admin_upload_gss_excel(request):
    logger.info('')
    if request.method == 'POST':
        upload_file = request.FILES.get('file')
        # parcel_infos, parcel_errors = get_parcel_infos_from_excel(upload_file.read())
        results = '+++++++++++++++++++<br>'
        try:
            excel = open_workbook(file_contents=upload_file.read())
            asheet = excel.sheet_by_index(0)
            import_info2update = {}
            for current_row in range(1, asheet.nrows):
                tracking_number = asheet.cell(current_row, 1).value
                if type(tracking_number) is types.FloatType:
                    tracking_number = str(int(tracking_number))

                yde_number = asheet.cell(current_row, 7).value
                if tracking_number and yde_number:
                    import_info2update[yde_number] = tracking_number
                else:
                    break

            for yde_number in import_info2update.keys():
                try:
                    parcel = IntlParcel.objects.get(yde_number=yde_number)
                    if parcel.tracking_number:
                        results += "%s: %s not updated. alreay has tracking no. %s<br>" % (yde_number, import_info2update[yde_number], parcel.tracking_number)
                    else:
                        parcel.tracking_number = import_info2update[yde_number]
                        parcel.tracking_number_created_at = datetime.now()
                        parcel.save()
                        results += "%s: %s updated<br>" % (yde_number, import_info2update[yde_number])
                except IntlParcel.DoesNotExist:
                    results += "%s: %s not updated. can't find parcel<br>" % (yde_number, import_info2update[yde_number])
            return {'success':True, 'results':"All updated<br>" + results}
        except:
            return {'success':False, 'results':"Not all updated<br>" + results}

class AdminIntlParcelPdf4ZollamtView(PDFTemplateView):
    filename = "intl-parcel-label.pdf"
    template_name = 'parcel/intl_parcel_label4zollamt.html'
    cmd_options = {
        'orientation': 'landscape',
        'checkbox-checked-svg': '/opt/django_sites/checkbox2.svg',
        'checkbox-svg':'/opt/django_sites/checkbox3.svg',
        'no-outline':True,  # 不产生index
        # 'collate': True,
        # 'quiet': None,
    }
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(AdminIntlParcelPdf4ZollamtView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(AdminIntlParcelPdf4ZollamtView, self).get_context_data(*args, **kwargs)
        yids = ""
        if self.request.method == 'POST':
            yids = self.request.POST.get('yids', '')
        elif self.request.method == 'GET':
            yids = self.request.GET.get('yids', '')
        yids = yids.split('.')
        # user_id = self.request.session.get('_auth_user_id')
        # user = User.objects.get(id=user_id)
        parcels = IntlParcel.objects.filter(yid__in=yids,
                                    status__in=['confirmed',
                                               'proccessing_at_yde',
                                               'transit_to_destination_country',
                                               'custom_clearance_at_destination_country',
                                               'distributing_at_destination_country',
                                               'distributed_at_destination_country',
                                               'error',
                                               ],
                                    is_deleted=False,
                                    ).order_by("yde_number")

        if parcels.count() > 0:
            context.update({'parcels':parcels})
        else:
            raise Http404('No retoure label found!')

        return context
    def post(self, request, *args, **kwargs):
        return super(AdminIntlParcelPdf4ZollamtView, self).get(request, *args, **kwargs)

@json_response
@csrf_exempt
def json_parcel_trackingv_simple(request):
    logger.info('')
    try:
        s = False
        if request.method == 'GET':
            s = request.GET.get('s', False)
        if request.method == 'POST':
            s = request.POST.get('s', False)

        s = s and s.strip()
        if s:
            results = {}
            result = []
            try:
                parcel = IntlParcel.objects.get(Q(yde_number=s) | Q(tracking_number=s))
                results['tracking_number'] = parcel.tracking_number
                results['yde_number'] = parcel.yde_number
                result.append({"created_at":parcel.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                               "description":u"包裹信息已收到并生成追踪号。下一步,包裹到达韵达德国处理中心"})
            except:
                results['tracking_number'] = s
                results['yde_number'] = ""
            res = tracking_fetch([{'mail_no':results['tracking_number']}])
            for info in res[0]['scan_infos']:
                if info["remark"] in [u"无对应数据"]:
                    continue
                result.append({"created_at":info["time"],
                               "description":info["remark"]})
            results['histories'] = sorted(result, key=lambda info: info['created_at'])

            return [results]
        return  []
    except Exception as e:
        logger.error(e)

@json_response
@csrf_exempt
def json_parcel_tracking(request):
    logger.info('')
    s = False
    if request.method == 'GET':
        s = request.GET.get('s', False)
    if request.method == 'POST':
        s = request.POST.get('s', False)

    s = s and s.strip()
    if s:
        try:
            parcels = IntlParcel.objects.filter(Q(yde_number=s) |
                                    Q(tracking_number=s) |
                                    Q(receiver_mobile=s) |
                                    Q(retoure_tracking_number=s)
                                    )
            tz = getattr(settings, 'TIME_ZONE', 'Europe/Berlin')
            local = pytz.timezone(tz)
            results = []
            for parcel in parcels:
                result = []
                for history in parcel.histories.filter(visible_to_customer=True).order_by('created_at'):
                    result.append({
                        "created_at":history.created_at.astimezone(local).strftime("%Y-%m-%d %H:%M"),
                        "description":history.description, })
                results.append({'tracking_number':parcel.tracking_number,
                                'yde_number':parcel.yde_number,
                                'histories':result
                                })
            if results:
                return results
            else:
                retoures = DhlRetoureLabel.objects.filter(
                                    Q(retoure_yde_number=s) |
                                    Q(tracking_number=s)
                                    )
                for parcel in retoures:
                    result = []
                    for history in parcel.histories.filter(visible_to_customer=True).order_by('created_at'):
                        result.append({
                            "created_at":history.created_at.astimezone(local).strftime("%Y-%m-%d %H:%M"),
                            "description":history.description, })
                    results.append({'tracking_number':parcel.tracking_number,
                                    'yde_number':parcel.retoure_yde_number,
                                    'histories':result
                                    })
                if results:
                    return results
                else:
                    res = tracking_fetch([{'mail_no':s}])
                    # logger.debug(res)
                    result = []
                    for info in res[0]['scan_infos']:
                        result.append({"created_at":info["time"],
                                       "description":info["remark"]})
                    # logger.debug(result)
                    s_result = sorted(result, key=lambda info: info['created_at'])
                    # logger.debug(s_result)
                    return [{'tracking_number':s,
                            'yde_number':"",
                            'histories':s_result,
                            }]
        except Exception as e:
            logger.error(e)
            return []
    return  []

##############
# sender template
##############
@json_response
@secure_required
@login_required
def json_search_sender_template(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')

    if request.method == 'GET':
        q = SenderTemplate.objects.filter(user_id=user_id)
        page = int(request.GET.get('page', 1) or 1)
        rows = int(request.GET.get('rows', 10) or 10)
        if page < 1:
            page = 1
        if rows < 1:
            rows = 10
        s = request.GET.get('s', False)
        if s:
            q = q.filter(
                           Q(sender_name__icontains=s) |
                           Q(sender_name2__icontains=s) |
                           Q(sender_company__icontains=s) |
                           Q(sender_city__icontains=s) |
                           Q(sender_postcode__icontains=s) |
                           Q(sender_tel__icontains=s) |
                           Q(sender_street__icontains=s) |
                           Q(sender_email__icontains=s) |
                           Q(sender_add__icontains=s)
                           )

        results = {}
        count = q.count()
        results['count'] = count or 0
        results['templates'] = []
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
        for obj in q.order_by('-sender_name')[start:end]:
            results['templates'].append(
                {
                    'yid':obj.yid,
                    'sender_name':obj.sender_name,
                    'sender_name2':obj.sender_name2,
                    'sender_company':obj.sender_company,
                    'sender_state':obj.sender_state,
                    'sender_city':obj.sender_city,
                    'sender_postcode':obj.sender_postcode,
                    'sender_street':obj.sender_street,
                    'sender_add':obj.sender_add,
                    'sender_hause_number':obj.sender_hause_number,
                    'sender_tel':obj.sender_tel,
                    'sender_email':obj.sender_email,
                 }
            )

        return results

@json_response
@secure_required
@login_required
def json_remove_sender_template(request):
    logger.info('')
    if request.method == 'POST':
        results = []
        user_id = request.session.get('_auth_user_id')
        yids = request.POST.get('yids', False)
        p = re.compile(u'^[a-zA-Z0-9\+]+$')
        if yids and p.match(yids):
            yids = yids.split('+')
            try:
                templates = SenderTemplate.objects.filter(yid__in=yids, user_id=user_id)
                templates.delete()
                results = yids
            except Exception as e:
                logger.error(e)
        return results

@json_response
@secure_required
@login_required
def json_post_sender_template(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')
    if request.method == 'POST':
        template_form = SenderTemplateForm(request.POST, request.FILES)
        is_valid = True
        if not template_form.is_valid():
            is_valid = False
            errors = template_form.errors

        if is_valid:
            yid = request.POST.get('yid', False)
            if yid:
                # edit a parcel
                try:
                    template = SenderTemplate.objects.get(user_id=user_id, yid=yid)

                    update_form = SenderTemplateForm(request.POST, instance=template)
                    update_form.save()
                    return dict(state="success",
                            yid=yid)

                except SenderTemplate.DoesNotExist:
                    return dict(state="error",
                            msg=u"发件人地址不存在或者已被删除",
                            errors={})
                except Exception as e:
                    logger.error(e)
            else:
                # create a new parcel

                template = template_form.save(commit=False)
                template.user_id = user_id
                template.save()
                template.yid = hashlib.md5("sendertemplate%d" % template.id).hexdigest()
                template.save()

                return dict(state="success",
                            yid=template.yid)
        else:
            return dict(state='error',
                        errors=errors,
                        msg=u"提交数据有误，请修改")

            # user = form.save()
    else:
        return {'state':'error',
                'msg':"",
                'errors':{}}

##############
# receiver template
##############
@json_response
@secure_required
@login_required
def json_search_receiver_template(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')

    if request.method == 'GET':
        q = ReceiverTemplate.objects.filter(user_id=user_id)
        page = int(request.GET.get('page', 1) or 1)
        rows = int(request.GET.get('rows', 10) or 10)
        if page < 1:
            page = 1
        if rows < 1:
            rows = 10
        s = request.GET.get('s', False)
        if s:
            q = q.filter(
                           Q(receiver_name__icontains=s) |
                           Q(receiver_company__icontains=s) |
                           Q(receiver_province__icontains=s) |
                           Q(receiver_city__icontains=s) |
                           Q(receiver_district__icontains=s) |
                           Q(receiver_address__icontains=s) |
                           Q(receiver_address2__icontains=s) |
                           Q(receiver_postcode__icontains=s) |
                           Q(receiver_email__icontains=s) |
                           Q(receiver_mobile__icontains=s)
                           )

        results = {}
        count = q.count()
        results['count'] = count or 0
        results['templates'] = []
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
        for obj in q.order_by('-receiver_name')[start:end]:
            results['templates'].append(
                {
                    'yid':obj.yid,
                    'receiver_name':obj.receiver_name,
                    'receiver_company':obj.receiver_company,
                    'receiver_province':obj.receiver_province,
                    'receiver_city':obj.receiver_city,
                    'receiver_district':obj.receiver_district,
                    'receiver_postcode':obj.receiver_postcode,
                    'receiver_address':obj.receiver_address,
                    'receiver_address2':obj.receiver_address2,
                    'receiver_mobile':obj.receiver_mobile,
                    'receiver_email':obj.receiver_email,
                 }
            )

        return results

@json_response
@secure_required
@login_required
def json_remove_receiver_template(request):
    logger.info('')
    if request.method == 'POST':
        results = []
        user_id = request.session.get('_auth_user_id')
        yids = request.POST.get('yids', False)
        p = re.compile(u'^[a-zA-Z0-9\+]+$')
        if yids and p.match(yids):
            yids = yids.split('+')
            try:
                templates = ReceiverTemplate.objects.filter(yid__in=yids, user_id=user_id)
                templates.delete()
                results = yids
            except Exception as e:
                logger.error(e)
        return results

@json_response
@secure_required
@login_required
def json_post_receiver_template(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')
    if request.method == 'POST':
        template_form = ReceiverTemplateForm(request.POST, request.FILES)
        is_valid = True
        if not template_form.is_valid():
            is_valid = False
            errors = template_form.errors

        if is_valid:
            yid = request.POST.get('yid', False)
            if yid:
                # edit a parcel
                try:
                    template = ReceiverTemplate.objects.get(user_id=user_id, yid=yid)

                    update_form = ReceiverTemplateForm(request.POST, instance=template)
                    update_form.save()
                    return dict(state="success",
                            yid=yid)

                except ReceiverTemplate.DoesNotExist:
                    return dict(state="error",
                            msg=u" 收件人地址不存在或者已被删除",
                            errors={})
                except Exception as e:
                    logger.error(e)
            else:
                # create a new parcel

                template = template_form.save(commit=False)
                template.user_id = user_id
                template.save()
                template.yid = hashlib.md5("receivertemplate%d" % template.id).hexdigest()
                template.save()

                return dict(state="success",
                            yid=template.yid)
        else:
            return dict(state='error',
                        msg=u"提交信息有误，请修改",
                        errors=errors)

            # user = form.save()
    else:
        return {'state':'error',
                'msg':"",
                'errors':{}}
# # end receiver template

@json_response
@secure_required
@staff_member_required
def tracking_push_to_gss(request):
    logger.info('')
    tz = getattr(settings, 'TIME_ZONE', 'Asia/Shanghai')
    local = pytz.timezone(tz)
    results = []
    for history in History.objects.filter(intl_parcel__type__code__icontains="yd", tracking_pushed=False).\
    exclude(description__icontains=u"扣款成功。下一步：等待包裹到达处理中心")[:50]:
        if u"扣款成功。下一步：等待包裹到达处理中心" in history.description:
            continue
        if history.intl_parcel.tracking_number:
            description = history.description
            if u'等待上传身份证' in description:
                description += u"。上传网址：http://yunda-express.eu/shenfenzheng/ (请复制粘贴至浏览器地址栏，此网址也可以直接手机访问上传)"  # % (history.intl_parcel.receiver_name, history.intl_parcel.receiver_mobile)
            scan_infos = [{
                         'mail_no':history.intl_parcel.tracking_number,
                         'mail_oth_no':history.intl_parcel.yde_number,
                         'time':history.created_at.astimezone(local).strftime("%Y/%m/%d %H:%M:%S"),  # 2015/07/13 19:37:45
                         'remark':description
                         }]
            result = tracking_push(scan_infos)
            if result:
                results += result
                history.tracking_pushed = True
                history.tracking_pushed_at = datetime.now()
                history.save()
            else:
                results.append({
                                'tracking_number':history.intl_parcel.tracking_number,
                                'description':description,
                                'fail':True
                                })
    return results

@json_response
@secure_required
@staff_member_required
def get_yd_print_data(request):  # not need any more, need to be deleted
    logger.info('')
    if request.method == 'GET':
        yid = request.GET.get('yid', False)
        if yid:
            try:
                parcel = IntlParcel.objects.get(yid=yid)
                if parcel.pdf_info:
                    return {'success':True, 'yd_print_data':parcel.pdf_info}
                else:
                    result = query_parcel([{'hawbno':parcel.yde_number, 'mail_no':parcel.tracking_number}])
                    # result=query_parcel(parcel.tracking_number,'default')
                    if result:
                        parcel.pdf_info = result[0]['pdf_info']
                        parcel.save()
                        return {'success':True, 'yd_print_data':result[0]['pdf_info']}
                    else:
                        return {'success':False, 'msg':u"No data found at GOS"}
            except IntlParcel.DoesNotExist:
                logger.error("YID %s duplicated!" % yid)
                return {'success':False, 'msg':u"YID %s duplicated!" % yid}
            except Exception as e:
                logger.error(e)
                return {'success':False, 'msg':u"Server error, inform the IT, please"}
        else:
            return {'success':False, 'msg':u"No yid submitted"}
    return {'success':False, 'msg':u"Network error"}



@json_response
@secure_required
@csrf_exempt
def json_get_tracking_from_gss(request):
    logger.info('')
    if request.method == 'GET':
        s = request.GET.get('s', False)
    if request.method == 'POST':
        s = request.POST.get('s', False)

    result = tracking_fetch([{'mail_no':s}])
    return result

################################
# mawb statistics
_stat_sheet_cols = {
      'pos':0,
      'mawb':1,
      'cn_customs_name':2,
      'parcel_qty':3,
      'total_weight_kg':4,  # total weight of all parcels
      'total_volumn_cmb':5,  # total volumn of all parcels
      'total_incomming_fee_eur':6,
      'total_incomming_fee_cny':7,
      'mawb_wegiht_kg':8,  # mawb weight to airlines
      'mawb_vweight_kg':9,  # mawb volumn weight to airlines
      'cost_yde_to_dest_airport_eur':10,
      'cost_customs_clearance_cny':11,  # cost of customs clearance in china
      'sh_yunda_to_pay_cny':12,  # cost to shanghai hq
      'local_yunda_to_pay_cny':13,  # cost to local yunda
      'remarks':14,  # remarks
      }

_parcels_sheet_cols = {
    'pos':0,
    'mawb':1,
    'customer_number':2,
    'yde_number':3,
    'tracking_number':4,
    'parcel_type':5,
    'customer_input_weight':6,
    'customer_input_length':7,
    'customer_input_width':8,
    'customer_input_height':9,
    'real_weight':10,
    'real_length':11,
    'real_width':12,
    'real_height':13,
    'charged_fee_eur':14,
    'charged_fee_cny':15,
    'dest_country':16,
    'dest_city':17,
    'dest_postcode':18,
    'dest_name_en':19,
    'dest_city_en':20,
    'sender_name':21,
    'sender_company':22,
    'sender_street':23,
    'sender_city':24,
    'sender_postcode':25,
    'invoice_name':26,
    'invoice_company':27,
    'invoice_street':28,
    'invoice_city':29,
    'invoice_postcode':30,
    }
def _write_to_parcels_sheet(parcel, sheet, row, mawb):
    logger.info('')
    sheet.write(row, _parcels_sheet_cols['pos'], row)
    sheet.write(row, _parcels_sheet_cols['mawb'], mawb)
    sheet.write(row, _parcels_sheet_cols['customer_number'], parcel.user.userprofile.customer_number)
    sheet.write(row, _parcels_sheet_cols['yde_number'], parcel.yde_number)
    sheet.write(row, _parcels_sheet_cols['tracking_number'], parcel.tracking_number)
    sheet.write(row, _parcels_sheet_cols['parcel_type'], parcel.type.code)
    sheet.write(row, _parcels_sheet_cols['customer_input_weight'], parcel.weight_kg)
    sheet.write(row, _parcels_sheet_cols['customer_input_length'], parcel.length_cm)
    sheet.write(row, _parcels_sheet_cols['customer_input_width'], parcel.width_cm)
    sheet.write(row, _parcels_sheet_cols['customer_input_height'], parcel.height_cm)
    sheet.write(row, _parcels_sheet_cols['real_weight'], parcel.real_weight_kg)
    sheet.write(row, _parcels_sheet_cols['real_length'], parcel.real_length_cm)
    sheet.write(row, _parcels_sheet_cols['real_width'], parcel.real_width_cm)
    sheet.write(row, _parcels_sheet_cols['real_height'], parcel.real_height_cm)
    if parcel.currency_type == 'eur':
        sheet.write(row, _parcels_sheet_cols['charged_fee_eur'], parcel.booked_fee)
    else:
        sheet.write(row, _parcels_sheet_cols['charged_fee_cny'], parcel.booked_fee)
    sheet.write(row, _parcels_sheet_cols['dest_country'], parcel.receiver_country)
    sheet.write(row, _parcels_sheet_cols['dest_city'], u"%s%s%s" % (parcel.receiver_province, parcel.receiver_city or u"", parcel.receiver_district or u''))
    sheet.write(row, _parcels_sheet_cols['dest_postcode'], parcel.receiver_postcode)

    receiver_name_en = parcel.get_receiver_name_en()
    receiver_company_en = parcel.get_receiver_company_en()
    if receiver_company_en:
        receiver_name_en += "\n" + receiver_company_en
    sheet.write(row, _parcels_sheet_cols['dest_name_en'], receiver_name_en)
    sheet.write(row, _parcels_sheet_cols['dest_city_en'], u"%s %s %s" % (parcel.get_receiver_province_en(), parcel.get_receiver_city_en() or u"", parcel.get_receiver_district_en() or u''))
    sheet.write(row, _parcels_sheet_cols['sender_name'], parcel.sender_name)
    sheet.write(row, _parcels_sheet_cols['sender_company'], parcel.sender_company)
    sheet.write(row, _parcels_sheet_cols['sender_street'], u"%s %s" % (parcel.sender_street, parcel.sender_hause_number))
    sheet.write(row, _parcels_sheet_cols['sender_city'], parcel.sender_city)
    sheet.write(row, _parcels_sheet_cols['sender_postcode'], parcel.sender_postcode)
    sheet.write(row, _parcels_sheet_cols['invoice_name'], parcel.user.get_full_name())
    sheet.write(row, _parcels_sheet_cols['invoice_company'], parcel.user.userprofile.company)
    sheet.write(row, _parcels_sheet_cols['invoice_street'], parcel.user.userprofile.street)
    sheet.write(row, _parcels_sheet_cols['invoice_city'], parcel.user.userprofile.city)
    sheet.write(row, _parcels_sheet_cols['invoice_postcode'], parcel.user.userprofile.postcode)

@json_response
@secure_required
@staff_member_required
def mail_mawb_report(request):
    logger.info('')
    if request.method == 'GET':
        ids = request.GET.get('ids', False)
    if request.method == 'POST':
        ids = request.POST.get('ids', False)
    if ids:
        ids = ids.split('.')
        book = Workbook()
        stat_sheet = book.add_sheet('Statistcs')
        parcels_sheet = book.add_sheet('Parcels info')
        stat_sheet_row = 0
        parcels_sheet_row = 0
        email_body = "MAWB statistics:\n"
        if ids:
            for key in _stat_sheet_cols.keys():
                stat_sheet.write(stat_sheet_row, _stat_sheet_cols[key], key)
            stat_sheet_row += 1
            for key in _parcels_sheet_cols.keys():
                parcels_sheet.write(parcels_sheet_row, _parcels_sheet_cols[key], key)

            parcels_sheet_row += 1
            try:
                for mawb in Mawb.objects.filter(id__in=ids):
                    email_body += "%s\n" % mawb.mawb_number
                    remarks = ""
                    stat_sheet.write(stat_sheet_row, _stat_sheet_cols['pos'], stat_sheet_row)
                    stat_sheet.write(stat_sheet_row, _stat_sheet_cols['mawb'], mawb.mawb_number)
                    stat_sheet.write(stat_sheet_row, _stat_sheet_cols['cn_customs_name'], mawb.cn_customs)
                    yids = []
                    for batch in mawb.batches.all():
                        yids += batch.yids
                    stat_sheet.write(stat_sheet_row, _stat_sheet_cols['parcel_qty'], len(yids))
                    parcels = IntlParcel.objects.filter(yid__in=yids)
                    if len(yids) != parcels.count():
                        remarks += "qty not match: qty in all batches  %d, found %d" % (len(yids), parcels.count())
                    total_weight = 0
                    total_volumn = 0
                    total_incomming_fee_eur = 0
                    total_incomming_fee_cny = 0
                    for parcel in parcels:
                        _write_to_parcels_sheet(parcel, parcels_sheet, parcels_sheet_row, mawb.mawb_number)
                        total_weight += parcel.weight_kg
                        total_volumn += parcel.length_cm * parcel.width_cm * parcel.height_cm / 1000000
                        if parcel.currency_type == "eur":
                            total_incomming_fee_eur += parcel.booked_fee
                        else:
                            total_incomming_fee_cny += parcel.booked_fee
                        parcels_sheet_row += 1
                    stat_sheet.write(stat_sheet_row, _stat_sheet_cols['total_weight_kg'], total_weight)
                    stat_sheet.write(stat_sheet_row, _stat_sheet_cols['total_volumn_cmb'], total_volumn)
                    stat_sheet.write(stat_sheet_row, _stat_sheet_cols['total_incomming_fee_eur'], total_incomming_fee_eur)
                    stat_sheet.write(stat_sheet_row, _stat_sheet_cols['total_incomming_fee_cny'], total_incomming_fee_cny)

                    stat_sheet_row += 1

                # SEND EMAIL
                email = EmailMessage('YUNDA parcel statistics', email_body,
                                   to=getattr(settings, 'STATISTICS_SEND_TO_EMAILS', ['cmiao.yunda@gmail.com'])
                                   )
                attch_file = MIMEBase('application', 'vnd.ms-excel')
                file_io = StringIO()
                book.save(file_io)
                email.attach('mawb_statistics.xls', file_io.getvalue(), 'application/vnd.ms-excel')
                email.send(True)

                return True

#  response = HttpResponse(content_type='application/vnd.ms-excel')
#             response['Content-Disposition'] = 'attachment; filename=gss-%s.xls' % datetime.now().isoformat()
#             book.save(response)
#         else:
#             response = HttpResponse(content_type='application/vnd.ms-excel')
#             response['Content-Disposition'] = 'attachment; filename=empty.xls'

            except Exception as e:
                logger.error(e)
                return e
        else:
            return "No ids"
    return False

############
# # 20151214
@json_response
@secure_required
@staff_member_required
def edit_product_main_category(request):
    logger.info('')
    if request.method == 'POST':
        cn_name = request.POST.get('cn_name', "")
        en_name = request.POST.get('en_name', "")
        pk = request.GET.get("pk", "")
        cn_name = cn_name.strip()
        en_name = en_name.strip()
        if (not cn_name) or (not en_name):
            return {"state":"error", "msg":"Cn name and En name should not be blank"}
        pk = pk.strip()
        if pk:
            try:
                pk = int(pk)
                pmc = ProductMainCategory.objects.get(pk=pk)
                pmc.en_name = en_name
                pmc.cn_name = cn_name
                pmc.save()
                return {"state":"success", "product_main_category":{"pk":pk, "en_name":en_name, "cn_name":cn_name}}

            except Exception as e:
                logger.error(e)
                return {"state":"error", "msg":"%s" % e}
        else:
            try:
                pmc = ProductMainCategory.objects.create(cn_name=cn_name, en_name=en_name)
                return {"state":"success", "product_main_category":{"pk":pmc.id, "en_name":en_name, "cn_name":cn_name}}
            except Exception as e:
                logger.error(e)
                return {"state":"error", "msg":"%s" % e}

@json_response
@secure_required
@staff_member_required
def edit_product_category(request):
    logger.info('')
    if request.method == 'POST':
        cn_name = request.POST.get('cn_name', "").strip()
        en_name = request.POST.get('en_name', "").strip()
        product_main_category = request.POST.get('product_main_category', "").strip()
        pk = request.GET.get("pk", "")
        if (not cn_name) or (not en_name) or (not product_main_category):
            return {"state":"error", "msg":"Cn name, En name and product main category should not be blank"}

        try:
            pmc = ProductMainCategory.objects.get(pk=int(product_main_category))
        except Exception as e:
            logger.error(e)
            return {"state":"error", "msg":"%s" % e}

        pk = pk.strip()
        if pk:
            try:
                pk = int(pk)
                pc = ProductCategory.objects.get(pk=pk)
                pc.en_name = en_name
                pc.cn_name = cn_name
                pc.product_main_category = pmc
                pc.save()
                return {"state":"success", "pk":pk, "en_name":en_name, "cn_name":cn_name, "product_main_categories":pmc.id}

            except Exception as e:
                logger.error(e)
                return {"state":"error", "msg":"%s" % e}
        else:
            try:
                pc = ProductCategory.objects.create(cn_name=cn_name, en_name=en_name, product_main_category=pmc)
                return {"state":"success", "pk":pc.id, "en_name":en_name, "cn_name":cn_name, "product_main_category":pmc.id}
            except Exception as e:
                logger.error(e)
                return {"state":"error", "msg":"%s" % e}

@json_response
@secure_required
@staff_member_required
def edit_product_brand(request):
    logger.info('')
    if request.method == 'POST':
        cn_name = request.POST.get('cn_name', "")
        en_name = request.POST.get('en_name', "")
        pk = request.GET.get("pk", "")
        cn_name = cn_name.strip()
        en_name = en_name.strip()
        if (not cn_name) or (not en_name):
            return {"state":"error", "msg":"Cn name and En name should not be blank"}
        pk = pk.strip()
        if pk:
            try:
                pk = int(pk)
                pb = ProductBrand.objects.get(pk=pk)
                pb.en_name = en_name
                pb.cn_name = cn_name
                pb.save()
                return {"state":"success", "product_brand":{ "pk":pk, "en_name":en_name, "cn_name":cn_name}}

            except Exception as e:
                logger.error(e)
                return {"state":"error", "msg":"%s" % e}
        else:
            try:
                pb = ProductBrand.objects.create(cn_name=cn_name, en_name=en_name)
                return {"state":"success", "product_brand":{"pk":pb.id, "en_name":en_name, "cn_name":cn_name}}

            except Exception as e:
                logger.error(e)
                return {"state":"error", "msg":"%s" % e}

def image_resize(img, size=(1000, 500)):
    try:
        if img.mode not in ('L', 'RGB'):
            img = img.convert('RGB')
        img = img.resize(size)
    except Exception, e:
        pass
    return img

def image_resize_with_max_width(img, max_width, max_height):
    try:
        # if img.mode not in ('L', 'RGB'):
        #    img = img.convert('RGB')
        width, height = img.size
        w_ratio = float(width) / max_width
        h_ratio = float(height) / max_height

        ratio = (w_ratio >= h_ratio) and w_ratio or h_ratio
        if ratio >= 1:
            img = img.resize((int(width / ratio), int(height / ratio)), Image.ANTIALIAS)
    except Exception, e:
        pass
    return img

def image_merge(images, output_dir='output', output_name='merge.jpg', restriction_max_width=None, restriction_max_height=None):
    '''垂直合并多张图片
    images - 要合并的图片路径列表
    ouput_dir - 输出路径
    output_name - 输出文件名
    restriction_max_width - 限制合并后的图片最大宽度，如果超过将等比缩小
    restriction_max_height - 限制合并后的图片最大高度，如果超过将等比缩小
    '''
    max_width = 0
    total_height = 0
    # 计算合成后图片的宽度（以最宽的为准）和高度
    for img in images:
        width, height = img.size
        if width > max_width:
            max_width = width
        total_height += height

    # 产生一张空白图
    new_img = Image.new('RGB', (max_width, total_height), (255, 255, 255))
    # 合并
    x = y = 0
    for img in images:
        width, height = img.size
        new_img.paste(img, (x, y))
        y += height

    if restriction_max_width and max_width >= restriction_max_width:
        # 如果宽带超过限制
        # 等比例缩小
        ratio = restriction_max_height / float(max_width)
        max_width = restriction_max_width
        total_height = int(total_height * ratio)
        new_img = image_resize(new_img, size=(max_width, total_height))

    if restriction_max_height and total_height >= restriction_max_height:
        # 如果高度超过限制
        # 等比例缩小
        ratio = restriction_max_height / float(total_height)
        max_width = int(max_width * ratio)
        total_height = restriction_max_height
        new_img = image_resize(new_img, size=(max_width, total_height))

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    save_path = '%s%s' % (output_dir, output_name)

    new_img.save(save_path, 'JPEG')
    return save_path
@json_response
@secure_required
@staff_member_required
def edit_product(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')
    if request.method == 'POST':
        cn_name = request.POST.get('cn_name', "").strip()
        en_name = request.POST.get('en_name', "").strip()
        description = request.POST.get('description', "").strip()
        cn_tax_name = request.POST.get('cn_tax_name', "").strip()
        cn_tax_number = request.POST.get('cn_tax_number', "").strip()
        cn_tax_standard_price_cny = request.POST.get('cn_tax_standard_price_cny', "").strip()
        cn_tax_rate = request.POST.get('cn_tax_rate', "").strip()
        cn_tax_unit = request.POST.get('cn_tax_unit', "").strip()
        cn_real_unit_tax_cny = request.POST.get('cn_real_unit_tax_cny', "").strip()
        price_eur = request.POST.get('price_eur', "").strip()
        unit = request.POST.get('unit', "").strip()
        unit_net_weight_volumn = request.POST.get('unit_net_weight_volumn', "").strip()
        net_weight_volumn_unit = request.POST.get('net_weight_volumn_unit', "").strip()
        sku = request.POST.get('sku', "").strip()
        url = request.POST.get('url', "").strip()
        product_categories = request.POST.get('product_categories', "").strip()
        product_brand = request.POST.get('product_brand', "").strip()
        small_pic = request.POST.get('small_pic', "").strip()
        price_pic = request.POST.get('price_pic', "").strip()
        pk = request.GET.get("pk", "").strip()
        if (not cn_name) or (not en_name) or (not description) or\
            (not cn_tax_name) or (not cn_tax_number) or (not cn_tax_standard_price_cny) or\
            (not cn_tax_rate) or (not cn_tax_unit) or\
            (not price_eur) or (not unit) or (not unit_net_weight_volumn) or\
            (not net_weight_volumn_unit) or (not sku) or (not url) or\
            (not product_categories) or (not product_brand) or\
            (not small_pic) or (not price_pic):
            return {"state":"error", "msg":"Cn name and En name should not be blank"}
        try:
            pb = ProductBrand.objects.get(id=int(product_brand))

            pc_ids = product_categories.split('.')
            for pc_id in pc_ids:
                if pc_id:
                    pc = ProductCategory.objects.get(id=int(pc_id))

            crutc = {}
            for utax in cn_real_unit_tax_cny.split("\n"):
                if utax:
                    tax = utax.split(":")
                    crutc[tax[0]] = float(tax[1].replace(",", "."))


            small_pic_imgage = Image.open(StringIO(small_pic.decode("base64")))
            small_pic_imgage = image_resize_with_max_width(small_pic_imgage, 800, 800)
            price_pic_imgage = Image.open(StringIO(price_pic.decode("base64")))
            price_pic_imgage = image_resize_with_max_width(price_pic_imgage, 800, 800)
        except Exception as e:
            logger.error(e)
            return {"state":"error", "msg":"%s" % e}
        if pk:
            try:
                user=User.objects.get(id=user_id)
                pk = int(pk)
                pd = Product.objects.get(pk=pk)
                pd.en_name = en_name
                pd.cn_name = cn_name
                pd.description = description
                pd.cn_tax_name = cn_tax_name
                pd.cn_tax_number = cn_tax_number
                pd.cn_tax_standard_price_cny = float(cn_tax_standard_price_cny)
                pd.cn_tax_rate = float(cn_tax_rate)
                pd.cn_tax_unit = cn_tax_unit
                pd.cn_real_unit_tax_cny = crutc
                pd.price_eur = float(price_eur)
                pd.unit = unit
                pd.unit_net_weight_volumn = float(unit_net_weight_volumn)
                pd.net_weight_volumn_unit = net_weight_volumn_unit
                pd.sku = sku
                pd.url = url
                pd.product_brand = pb.id
                pd.product_categories.clear()
                for pc_id in pc_ids:
                    pd.product_categories.add(int(pc_id))
                pd.save()
                product_small_image_root = settings.PRODUCT_SMALL_IMAGE_ROOT
                product_price_image_root = settings.PRODUCT_PRICE_IMAGE_ROOT
                small_image_dir = "%s/%s/%s/%s/" % (product_small_image_root,
                                                          pd.yid[5:6],
                                                          pd.yid[8:9],
                                                          pd.yid[11:12])
                if not os.path.exists(small_image_dir):
                    os.makedirs(small_image_dir)

                price_image_dir = "%s/%s/%s/%s/" % (product_price_image_root,
                                                          pd.yid[5:6],
                                                          pd.yid[8:9],
                                                          pd.yid[11:12])
                if not os.path.exists(price_image_dir):
                    os.makedirs(price_image_dir)

                small_pic_imgage.save("%s%s.jpg" % (small_image_dir, pd.yid), "JPEG", quality=95)
                price_pic_imgage.save("%s%s.jpg" % (price_image_dir, pd.yid), "JPEG", quality=95)
                pd.small_pic_url = "%s/%s/%s/%s.jpg" % (pd.yid[5:6],
                                                          pd.yid[8:9],
                                                          pd.yid[11:12],
                                                     pd.yid)
                pd.price_pic_url = "%s/%s/%s/%s.jpg" % (pd.yid[5:6],
                                                          pd.yid[8:9],
                                                          pd.yid[11:12],
                                                     pd.yid)
                histories=pd.histories or []
                histories.append({
                              "datetime":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                              "staff":user.get_full_name(),
                              "description":"Standard product edited"
                              })
                pd.histories=histories
                pd.save()

                result = _get_product(pd)
                result["state"] = "success"
                return result

            except Exception as e:
                logger.error(e)
                return {"state":"error", "msg":"%s" % e}
        else:
            try:
                user=User.objects.get(id=user_id)
                pd = Product.objects.create(
                    cn_name=cn_name,
                    en_name=en_name,
                    description=description,
                    cn_tax_name=cn_tax_name,
                    cn_tax_number=cn_tax_number,
                    cn_tax_standard_price_cny=float(cn_tax_standard_price_cny),
                    cn_tax_rate=float(cn_tax_rate),
                    cn_tax_unit=cn_tax_unit,
                    cn_real_unit_tax_cny=crutc,
                    price_eur=float(price_eur),
                    unit=unit,
                    unit_net_weight_volumn=float(unit_net_weight_volumn),
                    net_weight_volumn_unit=net_weight_volumn_unit,
                    sku=sku,
                    url=url,
                    product_brand=pb
                    )
                pd.yid = hashlib.md5("product%d" % pd.id).hexdigest()
                for pc_id in pc_ids:
                    if pc_id:
                        pd.product_categories.add(int(pc_id))
                pd.save()
                product_small_image_root = settings.PRODUCT_SMALL_IMAGE_ROOT
                product_price_image_root = settings.PRODUCT_PRICE_IMAGE_ROOT
                small_image_dir = "%s/%s/%s/%s/" % (product_small_image_root,
                                                          pd.yid[5:6],
                                                          pd.yid[8:9],
                                                          pd.yid[11:12])
                if not os.path.exists(small_image_dir):
                    os.makedirs(small_image_dir)

                price_image_dir = "%s/%s/%s/%s/" % (product_price_image_root,
                                                          pd.yid[5:6],
                                                          pd.yid[8:9],
                                                          pd.yid[11:12])
                if not os.path.exists(price_image_dir):
                    os.makedirs(price_image_dir)

                small_pic_imgage.save("%s%s.jpg" % (small_image_dir, pd.yid), "JPEG", quality=95)
                price_pic_imgage.save("%s%s.jpg" % (price_image_dir, pd.yid), "JPEG", quality=95)
                pd.small_pic_url = "%s/%s/%s/%s.jpg" % (pd.yid[5:6],
                                                          pd.yid[8:9],
                                                          pd.yid[11:12],
                                                     pd.yid)
                pd.price_pic_url = "%s/%s/%s/%s.jpg" % (pd.yid[5:6],
                                                          pd.yid[8:9],
                                                          pd.yid[11:12],
                                                     pd.yid)
                histories=[]
                histories.append({
                              "datetime":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                              "staff":user.get_full_name(),
                              "description":"Standard product created"
                              })
                pd.histories=histories
                pd.save()
                result = _get_product(pd)
                result["state"] = "success"
                return result
            except Exception as e:
                logger.error(e)
                return {"state":"error", "msg":"%s" % e}


def _get_product(product, cn_tax_to_eur_rate=None):
    logger.info('')
    if not cn_tax_to_eur_rate:
        cn_tax_to_eur_rate = YundaCommenSettings.objects.get(code="default").cn_tax_to_eur_rate
    cn_real_unit_tax_cny = product.cn_real_unit_tax_cny
    real_price_cny = product.price_eur * cn_tax_to_eur_rate
    if product.cn_tax_unit in [u"千克",u"kg",u"KG",u"Kg",u"公斤"]:
        real_price_cny_kg = real_price_cny / product.unit_net_weight_volumn * 1000
        if real_price_cny_kg >= product.cn_tax_standard_price_cny / 2 and real_price_cny_kg <= product.cn_tax_standard_price_cny * 2:
            cn_real_unit_tax_cny['default'] = product.cn_tax_standard_price_cny * product.cn_tax_rate * product.unit_net_weight_volumn / 1000
        else:
            cn_real_unit_tax_cny['default'] = real_price_cny * product.cn_tax_rate
    else:
        if real_price_cny >= product.cn_tax_standard_price_cny / 2 and real_price_cny <= product.cn_tax_standard_price_cny * 2:
            cn_real_unit_tax_cny['default'] = product.cn_tax_standard_price_cny * product.cn_tax_rate
        else:
            cn_real_unit_tax_cny['default'] = real_price_cny * product.cn_tax_rate
    categories = []
    for category in product.product_categories.all():
        categories.append({"main_category_pk":category.product_main_category.id,
                           "category_pk":category.id
                           })
    return {
            "pk":product.id,
            "en_name":product.en_name,
            "cn_name":product.cn_name,

            "description":product.description,
            "cn_tax_name":product.cn_tax_name,
            "cn_tax_number":product.cn_tax_number,
            "cn_tax_standard_price_cny":product.cn_tax_standard_price_cny,
            "cn_tax_rate":product.cn_tax_rate,
            "cn_tax_unit":product.cn_tax_unit,
            "cn_real_unit_tax_cny":cn_real_unit_tax_cny,

            "price_eur":product.price_eur,
            "unit":product.unit,
            "unit_net_weight_volumn":product.unit_net_weight_volumn,
            "net_weight_volumn_unit":product.net_weight_volumn_unit,

            "sku":product.sku,
            "yid":product.yid,
            "url":product.url,

            "product_categories":categories,
            "product_brand":product.product_brand.id
            }

@json_response
@secure_required
@staff_member_required
def get_product(request):
    logger.info('')
    pk = request.GET.get('pk', "").strip()
    if pk:
        try:
            pd = Product.objects.get(id=int(pk))
            result = _get_product(pd)
            result['state'] = "success"
            return result
        except Exception as e:
            logger.error(e)
            return {"state":"error", "msg":"%s" % e}
    else:
        return {"state":"error", "msg":"no pk"}

@json_response
@secure_required
@staff_member_required
def get_product_by_category(request):
    logger.info('')
    pk = request.GET.get('pk', "").strip()
    if pk:
        try:
            cn_tax_to_eur_rate = YundaCommenSettings.objects.get(code="default").cn_tax_to_eur_rate
            pc = ProductCategory.objects.get(id=int(pk))
            result = []
            for product in pc.product_set.all():
                result.append(_get_product(product, cn_tax_to_eur_rate=cn_tax_to_eur_rate))
            return {"state":"success", "products":result}
        except Exception as e:
            logger.error(e)
            return {"state":"error", "msg":"%s" % e}
    else:
        return {"state":"error", "msg":"no pk"}

@json_response
@secure_required
@staff_member_required
def get_product_by_brand(request):
    logger.info('')
    pk = request.GET.get('pk', "").strip()
    if pk:
        try:
            cn_tax_to_eur_rate = YundaCommenSettings.objects.get(code="default").cn_tax_to_eur_rate
            pb = ProductBrand.objects.get(id=int(pk))
            result = []
            for product in pb.product_set.all():
                result.append(_get_product(product, cn_tax_to_eur_rate=cn_tax_to_eur_rate))
            return {"state":"success", "products":result}
        except Exception as e:
            logger.error(e)
            return {"state":"error", "msg":"%s" % e}
    else:
        return {"state":"error", "msg":"no pk"}

@json_response
@secure_required
@staff_member_required
def admin_get_intl_parcel(request):
    logger.info('')
    yid = request.GET.get("yid", "").strip()
    if yid:
        try:
            tz = getattr(settings, 'TIME_ZONE', 'Asia/Shanghai')
            local = pytz.timezone(tz)

            parcel = IntlParcel.objects.get(yid=yid)
            result = get_parcel_info(parcel, local)
            details = []
            for detail in parcel.goodsdetails.all():
                if detail.product:
                    product = _get_product(detail.product)
                else:
                    product = False
                details.append({
                    "pk":detail.id,
                    "description":detail.description,
                    "cn_customs_tax_catalog_name":detail.cn_customs_tax_catalog_name,
                    "cn_customs_tax_name":detail.cn_customs_tax_name,
                    "qty":detail.qty,
                    "item_net_weight_kg":detail.item_net_weight_kg,
                    "item_price_eur":detail.item_price_eur,
                    "product":product})
            result['details'] = details

            histories = []
            for history in parcel.histories.filter(visible_to_customer=True).order_by('created_at'):
                histories.append({
                    "created_at":history.created_at.astimezone(local).strftime("%Y-%m-%d %H:%M"),
                    "description":history.description, })
            result['histories'] = histories

            result["cn_tax_to_pay_cny"] = parcel.cn_tax_to_pay_cny
            result["cn_tax_paid_cny"] = parcel.cn_tax_paid_cny
            result["internal_histories"] = parcel.internal_histories
            result["processing_msg"] = parcel.processing_msg
            result["customs_code_forced"] = parcel.customs_code_forced

            result['real_weight_kg'] = parcel.real_weight_kg
            result['real_length_cm'] = parcel.real_length_cm
            result['real_width_cm'] = parcel.real_width_cm
            result['real_height_cm'] = parcel.real_height_cm
            result['booked_fee'] = parcel.booked_fee

            cn_tax_to_eur_rate = YundaCommenSettings.objects.get(code="default").cn_tax_to_eur_rate
            return {"state":'success', "parcel":result, "cn_tax_to_eur_rate":cn_tax_to_eur_rate}



        except IntlParcel.DoesNotExist:
            return dict(state="error", msg=u"No intl parcel found")
        except Exception as e:
            logger.error(e)
            return {"state":"error", "msg":"%s" % e}
    else:
        return {"state":"error", "msg":"no yid"}

@json_response
@secure_required
@staff_member_required
def admin_edit_detail(request):
    logger.info('')
    if request.method == "POST":
        description = request.POST.get("description", "").strip()
        cn_customs_tax_catalog_name = request.POST.get("cn_customs_tax_catalog_name", "").strip()
        cn_customs_tax_name = request.POST.get("cn_customs_tax_name", "").strip()
        qty = request.POST.get("qty", "").strip()
        item_net_weight_kg = request.POST.get("item_net_weight_kg", "").strip()
        item_price_eur = request.POST.get("item_price_eur", "").strip()
        product = request.POST.get("product", "").strip()
        pk = request.POST.get("pk", "").strip()
        if pk:
            try:
                detail = GoodsDetail.objects.get(pk=int(pk))
                if description:
                    detail.description = description
                if cn_customs_tax_catalog_name:
                    detail.cn_customs_tax_catalog_name = cn_customs_tax_catalog_name
                if cn_customs_tax_name:
                    detail.cn_customs_tax_name = cn_customs_tax_name
                if qty:
                    detail.qty = float(qty)
                if item_net_weight_kg:
                    detail.item_net_weight_kg = float(item_net_weight_kg)
                if item_price_eur:
                    detail.item_price_eur = float(item_price_eur)
                if product:
                    product = Product.objects.get(id=int(product))
                    detail.product = product
                detail.save()
                return {"state":"success", "detail":{
                    "pk":detail.id,
                    "description":detail.description,
                    "cn_customs_tax_catalog_name":detail.cn_customs_tax_catalog_name,
                    "cn_customs_tax_name":detail.cn_customs_tax_name,
                    "qty":detail.qty,
                    "item_net_weight_kg":detail.item_net_weight_kg,
                    "item_price_eur":detail.item_price_eur,
                    "product":_get_product(detail.product)}}
            except Exception as e:
                return {"state":"error", "msg":"%s" % e}
    return  {"state":"error", "msg":"Not post method, or pk not posted"}


@json_response
@secure_required
@staff_member_required
def admin_get_brands(request):
    logger.info('')
    results = []
    for brand in ProductBrand.objects.order_by("en_name"):
        results.append({"pk":brand.id, "cn_name":brand.cn_name, "en_name":brand.en_name})
    return {"state":"success", "product_brands":results}
@json_response
@secure_required
@staff_member_required
def admin_get_main_categories(request):
    logger.info('')
    results = []
    for pmc in ProductMainCategory.objects.order_by("en_name"):
        results.append({"pk":pmc.id, "cn_name":pmc.cn_name, "en_name":pmc.en_name})
    return {"state":"success", "product_main_categories":results}

@json_response
@secure_required
@staff_member_required
def admin_get_categories_by_main_category(request):
    logger.info('')
    pk = request.GET.get("pk", "").strip()
    results = []
    if pk:
        try:
            pmc = ProductMainCategory.objects.get(id=int(pk))
            for pc in pmc.productcategory_set.order_by("en_name"):
                results.append({"pk":pc.id, "cn_name":pc.cn_name, "en_name":pc.en_name})
            return {"state":"success", "product_categories":results}
        except ProductMainCategory.DoesNotExist:
            return {"state":"error", "msg":"no product main category found"}
        except Exception as e:
            logger.error(e)
            return {"state":"error", "msg":"%s" % e}

    else:
        return {"state":"error", "msg":"no pk"}

@json_response
@secure_required
@staff_member_required
def admin_get_cn_customs(request):
    logger.info('')
    get_all = request.GET.get("get_all", "no").strip()
    try:
        if get_all == "yes":
            objs = CnCustoms.objects.all()
        else:
            objs = CnCustoms.objects.filter(is_active=True)
        results = []
        for cn_customs in objs:
            results.append({
                            "code":cn_customs.code,
                            "name":cn_customs.name,
                            "is_active":cn_customs.is_active,
                            "settings":cn_customs.settings,
                            })
        return {"state":"success", "cn_customses":results}
    except Exception as e:
        logger.error(e)
        return {"state":"error", "msg":"%s" % e}

@json_response
@secure_required
@staff_member_required
def admin_set_parcel_cn_customs(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')
    if request.method=="POST":
        user=User.objects.get(id=user_id)
        yid = request.POST.get("yid", "").strip()
        cn_tax_to_pay_cny = request.POST.get("cn_tax_to_pay_cny", "").strip()
        customs_code_forced = request.POST.get("customs_code_forced", "").strip()
        try:
            parcel=IntlParcel.objects.get(yid=yid)
            parcel.customs_code_forced=customs_code_forced
            parcel.cn_tax_to_pay_cny=float(cn_tax_to_pay_cny)
            histories=parcel.internal_histories or []
            histories.append({
                              "datetime":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                              "staff":user.get_full_name(),
                              "description":"CN customs checked"
                              })
            parcel.internal_histories=histories
            parcel.save()
            return {"state":"success",
                    }
        except Exception as e:
            return {"state":"error", "msg":"%s" % e}
    return {"state":"error", "msg":"No data posted"}

@json_response
@secure_required
@staff_member_required
def admin_edit_parcel_processing_msg(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')
    if request.method=="POST":
        user=User.objects.get(id=user_id)
        yid = request.POST.get("yid", "").strip()
        processing_msg = request.POST.get("processing_msg", "").strip()
        try:

            parcel=IntlParcel.objects.get(yid=yid)
            parcel.processing_msg=processing_msg
            histories=parcel.internal_histories or []
            histories.append({
                              "datetime":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                              "staff":user.get_full_name(),
                              "description":"Processing msg changed to: %s" % processing_msg
                              })
            parcel.internal_histories=histories
            parcel.save()
            return {"state":"success",
                    }
        except Exception as e:
            return {"state":"error", "msg":"%s" % e}
    return {"state":"error", "msg":"No data posted"}

@json_response
@secure_required
@staff_member_required
def admin_add_new_msg_to_customer(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')
    if request.method=="POST":
        try:
            user=User.objects.get(id=user_id)
            yid = request.POST.get("yid", "").strip()
            content = request.POST.get("content", "").strip()
            parcel=IntlParcel.objects.get(yid=yid)

            write_new_subject_to_customer(parcel.user.id, u"问题件：追踪号%s，订单号:%s" % (parcel.tracking_number, parcel.yde_number), content, user.get_full_name())
            return {"state":"success"}
        except Exception as e:
            return {"state":"error", "msg":"%s" % e}
    return {"state":"error", "msg":"No data posted"}

# 20121225
def _haiguan_excel_can_wtd(mawb, batch_id):
    logger.info('')
    book = Workbook(encoding='utf8')
    sheet = book.add_sheet('importDateTemplate')
    try:
        row = 0
        sheet.write(row, 0, u"No")
        sheet.write(row, 1, u"报关单号")
        sheet.write(row, 2, u"总运单号")
        sheet.write(row, 3, u"袋号")
        sheet.write(row, 4, u"快件单号")
        sheet.write(row, 5, u"发件人")
        sheet.write(row, 6, u"发件人地址")
        sheet.write(row, 7, u"发件人电话")
        sheet.write(row, 8, u"收件人")
        sheet.write(row, 9, u"收件人电话")
        sheet.write(row, 10, u"城市")
        sheet.write(row, 11, u"邮编")
        sheet.write(row, 12, u"收件人地址")
        sheet.write(row, 13, u"内件名称")
        sheet.write(row, 14, u"数量")
        sheet.write(row, 15, u"总价")
        sheet.write(row, 16, u"重量(KG)")
        sheet.write(row, 17, u"税号")
        sheet.write(row, 18, u"物品名称")
        sheet.write(row, 19, u"品牌")
        sheet.write(row, 20, u"规格型号")
        sheet.write(row, 21, u"数量")
        sheet.write(row, 22, u"单位")
        sheet.write(row, 23, u"单价")
        sheet.write(row, 24, u"币别")
        sheet.write(row, 25, u"身份证件号码")
        sheet.write(row, 26, u"运输工具")
        sheet.write(row, 27, u"客户编号")
        sheet.write(row, 28, u"购物小票号码")
        sheet.write(row, 29, u"价格网址")
        sheet.write(row, 30, u"发货人国别")

        cn_tax_to_eur_rate = YundaCommenSettings.objects.get(code="default").cn_tax_to_eur_rate
        row += 1
        xuhao = 1
        yids = []

        style = xlwt.XFStyle()
        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = xlwt.Style.colour_map['red']
        style.pattern = pattern

        if batch_id:
            batch=Batch.objects.get(id=batch_id)
            yids=batch.yids
            file_name='MAWB%s-Batch-%s-huilv%.2f.xls' % (mawb.number or mawb.mawb_number,batch.sign, cn_tax_to_eur_rate)
        else:
            for batch in mawb.batches.all():
                yids += batch.yids
            file_name='MAWB%s-all-batch-huilv%.2f.xls' % (mawb.number or mawb.mawb_number,cn_tax_to_eur_rate)

        for parcel in IntlParcel.objects.filter(yid__in=yids):
            neijianmingchen = []
            shuliang = 0
            zhongjia = 0
            for detail in parcel.goodsdetails.all():
                if detail.product:
                    if detail.product.description not in neijianmingchen:
                        neijianmingchen.append(detail.product.description)
                    zhongjia += detail.product.price_eur * detail.qty * cn_tax_to_eur_rate
                shuliang += detail.qty
            sheet.write(row, 13, u",".join(neijianmingchen))
            sheet.write(row, 14, u"%.0f" % shuliang)
            sheet.write(row, 15, u"%.2f" % zhongjia)
            sheet.write(row, 16, u"%.2f" % parcel.real_weight_kg)
            for detail in parcel.goodsdetails.all():
                sheet.write(row, 0, u"%d" % xuhao)
                # sheet.write(row,1,u"报关单号")
                sheet.write(row, 2, mawb.number or mawb.mawb_number or "")
                # sheet.write(row,3,u"袋号")
                sheet.write(row, 4, parcel.tracking_number)
                sheet.write(row, 5, u"Yunda express")
                sheet.write(row, 6, u"Starkenburgstr. 11, 64546 Moerfelden-Walldorf, Germany")
                sheet.write(row, 7, u"0049-61057178772")
                sheet.write(row, 8, parcel.receiver_name)
                sheet.write(row, 9, parcel.receiver_mobile)
                sheet.write(row, 10, u"%s%s%s" % (parcel.receiver_province, parcel.receiver_city or "", parcel.receiver_district or ""))
                sheet.write(row, 11, parcel.receiver_postcode or "")
                sheet.write(row, 12, u"%s, %s" % (parcel.receiver_address, parcel.receiver_address2 or ""))

                if detail.product:
                    sheet.write(row, 17, detail.product.cn_tax_number)
                    sheet.write(row, 18, detail.product.cn_name or detail.description)
                    sheet.write(row, 19, detail.product.product_brand.cn_name)
                    sheet.write(row, 20, u"%.0f%s" % (detail.product.unit_net_weight_volumn, detail.product.net_weight_volumn_unit))
                    if detail.product.cn_tax_unit in [u"kg", u"千克", u"Kg", u"KG", u"公斤"]:
                        sheet.write(row, 21, u"%.2f" % (detail.product.unit_net_weight_volumn * detail.qty/1000))
                        sheet.write(row, 22, u"千克")
                        sheet.write(row, 23, u"%.2f" % (detail.product.price_eur * cn_tax_to_eur_rate / detail.product.unit_net_weight_volumn * 1000))
                    else:
                        sheet.write(row, 21, detail.qty)
                        sheet.write(row, 22, detail.product.unit or u"件")
                        sheet.write(row, 23, u"%.2f" % (detail.product.price_eur * cn_tax_to_eur_rate))
                    sheet.write(row, 24, u"CNY")
                    sheet.write(row, 25, parcel.get_sfz_number())
                    # sheet.write(row, 26, u"运输工具")
                    sheet.write(row, 27, parcel.yde_number)
                    # sheet.write(row, 28, u"购物小票号码")
                    sheet.write(row, 29, detail.product.url)
                else:
                    sheet.write(row, 17, "", style)
                    sheet.write(row, 18, detail.description, style)
                    sheet.write(row, 19, "", style)
                    sheet.write(row, 20, "", style)
                    sheet.write(row, 21, "", style)
                    sheet.write(row, 22, "", style)
                    sheet.write(row, 23, "", style)

                    sheet.write(row, 24, u"CNY")
                    sheet.write(row, 25, parcel.get_sfz_number())
                    # sheet.write(row, 26, u"运输工具")
                    sheet.write(row, 27, parcel.yde_number)
                    # sheet.write(row, 28, u"购物小票号码")
                    sheet.write(row, 29, "", style)
                # sheet.write(row, 30, u"发货人国别")
                row += 1
            xuhao += 1
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=%s' % file_name
        book.save(response)
        return response



    except Exception as e:
        logger.error(e)
        return HttpResponse("%s" % e)


@secure_required
@staff_member_required
def admin_get_price_images(request):
    logger.info('')
    try:
        if request.method == "POST":
            yids = request.POST.get('yids', "").strip()
            file_name = request.POST.get('file_name', 'mawb').strip()
            cn_customs = request.POST.get('cn_customs', '').strip()
        if request.method == "GET":
            yids = request.GET.get('yids', "").strip()
            file_name = request.GET.get('file_name', 'mawb').strip()
            cn_customs = request.GET.get('cn_customs', '').strip()
        if yids:
            yids = yids.split('+')
            parcels = IntlParcel.objects.filter(yid__in=yids)
            #if cn_customs in ["ctu","can-wtd"]:
            #    return _get_price_images_can_wtd(parcels, file_name)
            return _get_price_images_can_wtd(parcels, file_name)
    except Exception as e:
        logger.error(e)
        return HttpResponse("%s" % e)

def _image_merge(images, restriction_max_width=None, restriction_max_height=None):
    logger.info('')
    """垂直合并多张图片
    images - 要合并的图片
    restriction_max_width - 限制合并后的图片最大宽度，如果超过将等比缩小
    restriction_max_height - 限制合并后的图片最大高度，如果超过将等比缩小
    """
    max_width = 0
    total_height = 0
    # 计算合成后图片的宽度（以最宽的为准）和高度
    for img in images:
        width, height = img.size
        if width > max_width:
            max_width = width
        total_height += height

    # 产生一张空白图
    new_img = Image.new('RGB', (max_width, total_height), (255, 255, 255))
    # 合并
    x = y = 0
    for img in images:
        width, height = img.size
        new_img.paste(img, (x, y))
        y += height

    if restriction_max_width and max_width >= restriction_max_width:
        # 如果宽带超过限制
        # 等比例缩小
        ratio = restriction_max_width / float(max_width)
        max_width = restriction_max_width
        total_height = int(total_height * ratio)
        new_img = image_resize(new_img, size=(max_width, total_height))

    if restriction_max_height and total_height >= restriction_max_height:
        # 如果高度超过限制
        # 等比例缩小
        logger.error("#############aaa")
        ratio = restriction_max_height / float(total_height)
        max_width = int(max_width * ratio)
        total_height = restriction_max_height
        new_img = image_resize(new_img, size=(max_width, total_height))
        logger.error("2222222222222222222")
    return new_img
def _get_price_images_can_wtd(parcels, file_name):
    logger.info('')
    try:
        product_price_image_root = settings.PRODUCT_PRICE_IMAGE_ROOT
        complete_sign=""
        with closing(StringIO()) as buff:
            zf = zipfile.ZipFile(buff, mode="w")
            for parcel in parcels:
                images = []
                for detail in parcel.goodsdetails.all():
                    if detail.product:
                        images.append(Image.open("%s/%s" % (product_price_image_root, detail.product.price_pic_url)))
                    else:
                        complete_sign = u"_NOT_COMPLETE"
                new_img = _image_merge(images, restriction_max_width=800)
                img_buffer = StringIO()
                new_img.save(img_buffer, format="JPEG")
                if parcel.other_infos.has_key('third_party_tracking_number'):
                    jpg_file_name=parcel.other_infos['third_party_tracking_number']
                else:
                    jpg_file_name= parcel.tracking_number

                zf.writestr("20_%s.jpg" % jpg_file_name,
                                img_buffer.getvalue()  # base64.b64decode(image_file)
                                # compress_type=compression
                                )
            zf.close()
            ff = buff.getvalue()
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=%s%s.zip' % (file_name, complete_sign)
        response.write(ff)
        return response
    except Exception as e:
        logger.error(e)
        return HttpResponse(u"%s" % e)

@secure_required
@staff_member_required
def get_sfz_images(request):
    logger.info('')
    if request.method == "POST":
        yids = request.POST.get('yids', False)
        file_name = request.POST.get('file_name', 'mawb')
        cn_customs = request.POST.get('cn_customs', '').strip()
    if request.method == "GET":
        yids = request.GET.get('yids', False)
        file_name = request.GET.get('file_name', 'mawb')
        cn_customs = request.GET.get('cn_customs', '').strip()
    if yids:
        yids = yids.split('+')
        parcels=IntlParcel.objects.filter(yid__in=yids)
        if cn_customs in ["ctu","can-wtd"]:
            return _get_sfz_images_can_wtd(parcels, file_name)
        else:
            return _get_sfz_images_default(parcels, file_name)


    # return empty
    return HttpResponse(u"No yids")

def _get_sfz_images_can_wtd(parcels, file_name):
    logger.info('')
    try:
        complete_sign = ""  # ""表示完整
        with closing(StringIO()) as buff:
            zf = zipfile.ZipFile(buff, mode="w")
            for parcel in parcels:
                (number, image_file) = parcel.get_sfz_image()
                if number:
                    try:
                        if parcel.other_infos.has_key('third_party_tracking_number'):
                            zf.writestr("10_%s.jpg" % parcel.other_infos['third_party_tracking_number'],
                                    base64.b64decode(image_file)
                                    # compress_type=compression
                                    )
                        else:
                            zf.writestr("10_%s.jpg" % parcel.tracking_number,
                                    base64.b64decode(image_file)
                                    # compress_type=compression
                                    )
                    except Exception as e:
                        complete_sign = u"_NOT_COMPLETE"
                        zf.writestr("error_%s.jpg" % parcel.yde_number,
                            ""
                            # compress_type=compression
                            )
                else:
                    zf.writestr("not_found_%s.jpg" % parcel.yde_number,
                            ""
                            # compress_type=compression
                            )
                    complete_sign = u"_NOT_COMPLETE"
            zf.close()
            ff = buff.getvalue()
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=sfz-%s%s.zip' % (file_name, complete_sign)
        response.write(ff)
        return response
    except Exception as e:
        logger.error(e)
        return HttpResponse(u"%s" % e)

def _get_sfz_images_default(parcels, file_name):
    logger.info('')
    try:
        complete_sign = ""  # ""表示完整
        with closing(StringIO()) as buff:
            zf = zipfile.ZipFile(buff, mode="w")
            for parcel in parcels:
                (number, image_file) = parcel.get_sfz_image()
                if number:
                    zf.writestr("%s.jpg" % number,
                                base64.b64decode(image_file)
                                # compress_type=compression
                                )
                else:
                    complete_sign = u"_NOT_COMPLETE"
            zf.close()
            ff = buff.getvalue()
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=%s%s.zip' % (file_name, complete_sign)
        response.write(ff)
        return response
    except Exception as e:
        logger.error(e)
        return HttpResponse(u"%s" % e)

#######################################
# 20160201
@secure_required
@staff_member_required
def admin_get_label_image(request):
    logger.info('')
    if request.method == "GET":
        yids = request.GET.get('yids', False)
        file_name = request.GET.get('file_name', 'mawb')
        cn_customs = request.GET.get('cn_customs', '').strip()
    if request.method == "POST":
        yids = request.POST.get('yids', "").strip()
        file_name = request.POST.get('file_name', 'mawb').strip()
        cn_customs = request.POST.get('cn_customs', '').strip()
    if yids:
        tpl = loader.get_template("parcel/intl_parcel_label_qingguangongsi.html")
        yids = yids.split('+')
        parcels = IntlParcel.objects.filter(yid__in=yids)
        try:
            with closing(StringIO()) as buff:
                zf = zipfile.ZipFile(buff, mode="w")
                for parcel in parcels:
                    html_str = tpl.render(Context({"parcels":[parcel], "cn_customs":cn_customs}))
                    b = imagekit.from_string(html_str, False,options={"width":"550"})
                    zf.writestr("30_%s.jpg" % parcel.tracking_number, b)

                zf.close()
                ff = buff.getvalue()
            response = HttpResponse(content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename=label_image-%s.zip' % file_name
            response.write(ff)
            return response
        except Exception as e:
            logger.error(e)
            return HttpResponse(u"%s" % e)

    # TODO
    return HttpResponse("No yids")

##################################
# 20160222
##################################

@json_response
@secure_required
@staff_member_required
def admin_delete_from_mawb(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)
    if request.method == "POST":
        mawb_id = request.POST.get('mawb_id', '').strip()
        parcel_yde_number = request.POST.get('parcel_yde_number', '').strip()
        if mawb_id and parcel_yde_number:
            try:
                mawb = Mawb.objects.get(id=mawb_id)
                parcel = IntlParcel.objects.get(yde_number=parcel_yde_number)

                for batch in mawb.batches.all():
                    if parcel.yid in batch.yids:
                        batch.yids.remove(parcel.yid)
                        batch.total_value_per_sender[parcel.sender_name + parcel.sender_tel] -= parcel.get_total_value()
                        try:
                            mawb.receiver_name_mobiles.remove(parcel.receiver_name + parcel.receiver_mobile)
                        except ValueError:
                            logger.error('Receiver_name_mobiles not in list, when remove %s from %s' % (parcel_yde_number, mawb.mawb_number))
                        parcel.status = "confirmed"
                        parcel.mawb = None
                        parcel.exported_at = None

                        batch.histories.append({
                            "status":"Intl parcel %s removed" % parcel_yde_number,
                            "status_display":"Intl parcel %s removed" % parcel_yde_number,
                            "datetime":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "staff":user.get_full_name()
                          })
                        parcel.save()
                        batch.save()
                        mawb.save()
                        return {'state':'success', 'msg':'Done','deleted_yid':parcel.yid, 'batch_id':batch.id}

                return {'state':'error', 'msg':'Parcel does not exist in any batch here'}

            except Mawb.DoesNotExist:
                return {'state':'error', 'msg':'MAWB does not exist'}
            except Mawb.MultipleObjectsReturned:
                return {'state':'error', 'msg':'MAWB duplicated'}
            except IntlParcel.DoesNotExist:
                return {'state':'error', 'msg':'Intl parcel %s does not exist' % parcel_yde_number}
            except IntlParcel.MultipleObjectsReturned:
                return {'state':'error', 'msg':'Intl parcel %s duplicated' % parcel_yde_number}
            except Exception as e:
                logger.error(e)
                return {'state':'error', 'msg':'%s' % e}
        else:
            return {'state':'error', 'msg':'No mawb id or parcel yde number submitted'}

######################################
# 20160225
######################################
@json_response
@secure_required
@staff_member_required
def admin_upload_third_party_tracking_number_excel(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        upload_file = request.FILES.get('file')
        # parcel_infos, parcel_errors = get_parcel_infos_from_excel(upload_file.read())
        results = '+++++++++++++++++++<br>'
        try:
            excel = open_workbook(file_contents=upload_file.read())
            asheet = excel.sheet_by_index(0)
            third_party_tracking_number2update = {}
            third_party_name2update = {}
            for current_row in range(1, asheet.nrows):
                tracking_number = asheet.cell(current_row, 1).value
                if type(tracking_number) is types.FloatType:
                    tracking_number = str(int(tracking_number))

                third_party_tracking_number = asheet.cell(current_row, 2).value
                if type(third_party_tracking_number) is types.FloatType:
                    third_party_tracking_number = str(int(third_party_tracking_number))

                third_party_name = asheet.cell(current_row, 3).value
                if tracking_number and third_party_tracking_number:
                    third_party_tracking_number2update[tracking_number] = third_party_tracking_number
                    third_party_name2update[tracking_number] = third_party_name
                else:
                    break

            for tracking_number in third_party_tracking_number2update.keys():
                try:
                    parcel = IntlParcel.objects.get(tracking_number=tracking_number)
                    if not parcel.other_infos:
                        parcel.other_infos = {}

                    if not parcel.internal_histories:
                        parcel.internal_histories = []

                    if parcel.other_infos.has_key('third_party_tracking_number'):
                        old_tptn=parcel.other_infos['third_party_tracking_number']
                    else:
                        old_tptn="null"

                    if parcel.other_infos.has_key('third_party_name'):
                        old_tpn=parcel.other_infos['third_party_name']
                    else:
                        old_tpn="null"


                    parcel.internal_histories.append({
                        "datetime":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "staff":user.get_full_name(),
                        "description":"Third party tracking number changed: %s -> %s, third party name: %s -> %s" %
                            (old_tptn,
                             third_party_tracking_number2update[tracking_number],
                             old_tpn,
                             third_party_name2update[tracking_number]
                             )
                        })
                    parcel.other_infos['third_party_tracking_number'] = third_party_tracking_number2update[tracking_number]
                    parcel.other_infos['third_party_name'] = third_party_name2update[tracking_number]

                    parcel.save()
                    results += "%s: %s/%s updated<br>" % (tracking_number, third_party_tracking_number2update[tracking_number],third_party_name2update[tracking_number])
                except IntlParcel.DoesNotExist:
                    results += "%s: %s/%s not updated. can't find parcel<br>" % (tracking_number, third_party_tracking_number2update[tracking_number],third_party_name2update[tracking_number])
                except IntlParcel.MultipleObjectsReturned:
                    results += "%s: %s/%s not updated. duplicated parcel<br>" % (tracking_number, third_party_tracking_number2update[tracking_number],third_party_name2update[tracking_number])
                except Exception as e:
                    logger.error(e)
                    results += "%s: %s/%s not updated. ERROR: %s<br>" % (tracking_number, third_party_tracking_number2update[tracking_number],third_party_name2update[tracking_number],e)
            return {'success':True, 'results':"All updated<br>" + results}
        except Exception as e:
            logger.error(e)
            return {'success':False, 'results':"Not all updated<br>" + results}

##########################
# upload bank excel get cunstomer address for invoice
@secure_required
@staff_member_required
@csrf_exempt
def admin_customer_number_excel(request):
    logger.info('')
    if request.method == 'POST':
        upload_file = request.FILES.get('file')
        # parcel_infos, parcel_errors = get_parcel_infos_from_excel(upload_file.read())
        style = xlwt.XFStyle()
        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = xlwt.Style.colour_map['red']
        style.pattern = pattern
        p = re.compile(u'^K[0-9]{6}$')
        try:
            excel = open_workbook(file_contents=upload_file.read())
            asheet = excel.sheet_by_index(0)

            new_excel=Workbook()
            new_sheet=new_excel.add_sheet('out')
            for current_row in range(0, asheet.nrows):
                customer_number=asheet.cell(current_row, 5).value

                c_name=""
                c_street=""
                c_city=""
                c_postcode=""

                if p.match(customer_number):
                    try:
                        userprofile=UserProfile.objects.get(customer_number=customer_number)
                        if userprofile.user.last_name and userprofile.street and userprofile.postcode:
                            c_name=userprofile.user.get_full_name()
                            c_street="%s %s" % (userprofile.street,userprofile.hause_number or "")
                            if userprofile.company:
                                c_street="%s\n%s" %(userprofile.company,c_street)
                            c_city=userprofile.city or ""
                            c_postcode=userprofile.postcode or ""
                        else:
                            parcels=IntlParcel.objects.filter(user=userprofile.user)
                            if parcels.count()>0:
                                parcel=parcels[0]
                                c_name=parcel.sender_name
                                c_street="%s %s" % (parcel.sender_street,parcel.sender_hause_number or "")
                                if parcel.sender_company:
                                    c_street="%s\n%s" %(parcel.sender_company,c_street)
                                c_city=parcel.sender_city or ""
                                c_postcode=parcel.sender_postcode or ""


                    except:
                        pass

                for current_line in range(0,12):
                    new_sheet.write(current_row, current_line, asheet.cell(current_row, current_line).value or "")

                if c_name:
                    new_sheet.write(current_row, 13, c_name)
                else:
                    new_sheet.write(current_row, 13, "",style)

                if c_street:
                    new_sheet.write(current_row, 14, c_street)
                else:
                    new_sheet.write(current_row, 14, "",style)

                if c_postcode:
                    new_sheet.write(current_row, 15, c_postcode)
                else:
                    new_sheet.write(current_row, 15, "",style)

                if c_city:
                    new_sheet.write(current_row, 16, c_city)
                else:
                    new_sheet.write(current_row, 16, "",style)
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=out.xls'
            new_excel.save(response)
            return response
        except Exception as e:
            return HttpResponse(e)

##############################
# create excel DuiZhangDan
def get_duizhangdan(customer_number, start_date=None, end_date=None, for_check=False):
    logger.info('')
    if customer_number:
        try:
            userprofile = UserProfile.objects.get(customer_number=customer_number)
        except UserProfile.DoesNotExist:
            logger.error("get_duizhangdan: %s does not exist" % customer_number)
            return False
        except UserProfile.MultipleObjectsReturned:
            logger.error("get_duizhangdan: %s duplicated" % customer_number)
            return False
        except Exception as e:
            logger.error("get_duizhangdan: %s" % e)
            return False
        try:
            if start_date and end_date:
                start_date = datetime.strptime(start_date, "%y-%m-%d")
                end_date = datetime.strptime(end_date, "%y-%m-%d")
                intl_parcels = IntlParcel.objects.filter(user=userprofile.user).exclude(status='draft').filter(created_at__get=start_date).filter(created_at__let=end_date).order_by("-created_at")
                retoures = DhlRetoureLabel.objects.filter(user=userprofile.user).exclude(status='draft').filter(created_at__get=start_date).filter(created_at__let=end_date).order_by("-created_at")
                transfers = DepositTransferNew.objects.filter(user=userprofile.user).filter(created_at__get=start_date).filter(created_at__let=end_date).order_by("-created_at")
            else:
                intl_parcels = IntlParcel.objects.filter(user=userprofile.user).exclude(status='draft').order_by("-created_at")
                retoures = DhlRetoureLabel.objects.filter(user=userprofile.user).exclude(status='draft').order_by("-created_at")
                transfers = DepositTransferNew.objects.filter(user=userprofile.user).order_by("-created_at")
            if intl_parcels.count() > 0 or retoures.count() > 0 or transfers.count() > 0:
                new_excel = Workbook()
                if for_check:
                    style_red = xlwt.XFStyle()
                    pattern_red = xlwt.Pattern()
                    pattern_red.pattern = xlwt.Pattern.SOLID_PATTERN
                    pattern_red.pattern_fore_colour = xlwt.Style.colour_map['red']
                    style_red.pattern = pattern_red

                    style_yellow = xlwt.XFStyle()
                    pattern_yellow = xlwt.Pattern()
                    pattern_yellow.pattern = xlwt.Pattern.SOLID_PATTERN
                    pattern_yellow.pattern_fore_colour = xlwt.Style.colour_map['yellow']
                    style_yellow.pattern = pattern_yellow

                else:
                    sheet_shuoming = new_excel.add_sheet("Read_me")
                    style_red = xlwt.XFStyle()
                    style_yellow = xlwt.XFStyle()


                sheet_deposit_transfers = new_excel.add_sheet('Deposit_transfers')
                sheet_deposit_transfers.write(0, 0, 'Date time')
                sheet_deposit_transfers.write(0, 1, 'Amount %s' % userprofile.deposit_currency_type)
                sheet_deposit_transfers.write(0, 2, 'Origin')
                sheet_deposit_transfers.write(0, 3, 'Description')


                sheet_intl_parcels = new_excel.add_sheet('Intl_parcels')
                sheet_intl_parcels.write(0, 0, 'Date time')
                sheet_intl_parcels.write(0, 1, 'Order number')
                sheet_intl_parcels.write(0, 2, 'Tracking number')
                sheet_intl_parcels.write(0, 3, 'Chargeable weight')
                sheet_intl_parcels.write(0, 4, 'Booked fee %s' % userprofile.deposit_currency_type)
                sheet_intl_parcels.write(0, 5, 'Fee to charge %s' % userprofile.deposit_currency_type)
                sheet_intl_parcels.write(0, 6, 'Is deleted')
                sheet_intl_parcels.write(0, 7, 'Parcel type')

                sheet_retoures = new_excel.add_sheet('Retoures')
                sheet_retoures.write(0, 0, 'Date time')
                sheet_retoures.write(0, 1, 'Order number')
                sheet_retoures.write(0, 2, 'Tracking number')
                sheet_retoures.write(0, 3, 'Booked fee %s' % userprofile.deposit_currency_type)
                sheet_retoures.write(0, 4, 'Is deleted')

                parcel_total_fee = 0
                retoure_total_fee = 0
                transfers_total = 0

                crow = 1
                for parcel in intl_parcels:
                    vweight = parcel.length_cm * parcel.width_cm * parcel.height_cm / 6000
                    real_vweight = parcel.real_length_cm * parcel.real_width_cm * parcel.real_height_cm / 6000
                    real_weight = (parcel.weight_kg > parcel.real_weight_kg) and parcel.weight_kg or parcel.real_weight_kg
                    real_vweight = (vweight > real_vweight) and vweight or real_vweight
                    cweight = (real_weight > real_vweight) and real_weight or real_vweight
                    sheet_intl_parcels.write(crow, 0, parcel.created_at.strftime("%y-%m-%d %H:%M"))
                    sheet_intl_parcels.write(crow, 1, parcel.yde_number)
                    sheet_intl_parcels.write(crow, 2, parcel.tracking_number)

                    sheet_intl_parcels.write(crow, 3, round(Decimal(cweight), 3))
                    sheet_intl_parcels.write(crow, 4, round(Decimal(parcel.booked_fee or 0), 2))

                    if parcel.is_deleted:
                        sheet_intl_parcels.write(crow, 6, 'YES')
                    else:
                        fee = parcel.get_fee()
                        try:
                            real_fee = parcel.get_real_fee()
                            real_fee = (fee > real_fee) and fee or real_fee
                            sheet_intl_parcels.write(crow, 5, round(Decimal(real_fee), 2))
                            parcel_total_fee += real_fee
                        except Exception as e:
                            sheet_intl_parcels.write(crow, 5, round(Decimal(fee), 2), style_yellow)
                            parcel_total_fee += fee

                    sheet_intl_parcels.write(crow, 7, parcel.type and parcel.type.name or "")
                    crow += 1

                crow = 1
                for retoure in retoures:
                    sheet_retoures.write(crow, 0, retoure.created_at.strftime("%y-%m-%d %H:%M"))
                    sheet_retoures.write(crow, 1, retoure.retoure_yde_number)
                    sheet_retoures.write(crow, 2, retoure.tracking_number)
                    sheet_retoures.write(crow, 3, round(Decimal(retoure.price or 0), 2))
                    sheet_retoures.write(crow, 4, retoure.is_deleted and 'yes' or "")
                    retoure_total_fee += retoure.price
                    crow += 1

                crow = 1
                for transfer in transfers:
                    try:
                        intlparcel = IntlParcel.objects.get(yde_number=transfer.origin)
                        sheet_deposit_transfers.write(crow, 0, transfer.created_at.strftime("%y-%m-%d %H:%M"))
                        sheet_deposit_transfers.write(crow, 1, round(Decimal(transfer.amount or 0), 2))
                        sheet_deposit_transfers.write(crow, 2, transfer.origin)
                        sheet_deposit_transfers.write(crow, 3, transfer.ref)

                    except IntlParcel.DoesNotExist:
                        try:
                            ret = DhlRetoureLabel.objects.get(retoure_yde_number=transfer.origin)
                            sheet_deposit_transfers.write(crow, 0, transfer.created_at.strftime("%y-%m-%d %H:%M"))
                            sheet_deposit_transfers.write(crow, 1, round(Decimal(transfer.amount or 0), 2))
                            sheet_deposit_transfers.write(crow, 2, transfer.origin)
                            sheet_deposit_transfers.write(crow, 3, transfer.ref)
                        except DhlRetoureLabel.DoesNotExist:
                            sheet_deposit_transfers.write(crow, 0, transfer.created_at.strftime("%y-%m-%d %H:%M"), style_red)
                            sheet_deposit_transfers.write(crow, 1, round(Decimal(transfer.amount or 0), 2), style_red)
                            sheet_deposit_transfers.write(crow, 2, transfer.origin, style_red)
                            sheet_deposit_transfers.write(crow, 3, transfer.ref, style_red)
                        except DhlRetoureLabel.MultipleObjectsReturned:
                            sheet_deposit_transfers.write(crow, 0, transfer.created_at.strftime("%y-%m-%d %H:%M"), style_yellow)
                            sheet_deposit_transfers.write(crow, 1, round(Decimal(transfer.amount or 0), 2), style_yellow)
                            sheet_deposit_transfers.write(crow, 2, transfer.origin, style_yellow)
                            sheet_deposit_transfers.write(crow, 3, transfer.ref, style_yellow)

                        except Exception as e:
                            logger.error("get_duizhangdan write to excel %s" % e)

                    except IntlParcel.MultipleObjectsReturned:
                        sheet_deposit_transfers.write(crow, 0, transfer.created_at.strftime("%y-%m-%d %H:%M"), style_yellow)
                        sheet_deposit_transfers.write(crow, 1, round(Decimal(transfer.amount or 0), 2), style_yellow)
                        sheet_deposit_transfers.write(crow, 2, transfer.origin, style_yellow)
                        sheet_deposit_transfers.write(crow, 3, transfer.ref, style_yellow)

                    except Exception as e:
                        logger.error("get_duizhangdan write to excel %s" % e)

                    transfers_total += transfer.amount
                    crow += 1

                if for_check:
                    sheet_deposit_transfers.write(0, 5, u'账户实际余额：')
                    sheet_deposit_transfers.write(0, 6, round(Decimal(userprofile.current_deposit or 0), 2))

                    sheet_deposit_transfers.write(1, 5, u'扣款记录求和：')
                    sheet_deposit_transfers.write(1, 6, round(Decimal(transfers_total), 2))

                    sheet_deposit_transfers.write(2, 5, u'国际邮单应扣费：')
                    sheet_deposit_transfers.write(2, 6, round(Decimal(parcel_total_fee), 2))

                    sheet_deposit_transfers.write(3, 5, u'回邮单应扣费：')
                    sheet_deposit_transfers.write(3, 6, round(Decimal(retoure_total_fee), 2))

                else:

                    sheet_shuoming.write(1, 0, u'账户实际余额：')
                    sheet_shuoming.write(2, 0, round(Decimal(userprofile.current_deposit or 0), 2))

                    sheet_shuoming.write(1, 1, u'扣款记录求和：')
                    sheet_shuoming.write(2, 1, round(Decimal(transfers_total), 2))

                    sheet_shuoming.write(1, 2, u'国际邮单应扣费：')
                    sheet_shuoming.write(2, 2, round(Decimal(parcel_total_fee), 2))

                    sheet_shuoming.write(1, 3, u'回邮单应扣费：')
                    sheet_shuoming.write(2, 3, round(Decimal(retoure_total_fee), 2))

                    sheet_shuoming.write(4, 0, u"表格说明：")
                    sheet_shuoming.write(5, 0, u"所有包裹均采用航空运输，计费时需计算其体积重量。根据国际航协IATA的规定，体积重量计算公式为：长cm*宽cm*高cm/6000。")
                    sheet_shuoming.write(6, 0, u"最终计费重量按体积重量和实际重量较大者计算。")
                return new_excel

            else:
                return False
        except Exception as e:
            logger.error("get_duizhangdan: %s" % e)

    else:
        return False


@secure_required
@login_required
def get_duizhangdan_excel(request):
    logger.info('')
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)

    if user.is_staff:
        customer_number = request.GET.get('customer_number', "").strip()
        if customer_number:
            excel = get_duizhangdan(customer_number,for_check=True)
            if excel:
                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename=%s-DuiZhangDan.xls' % customer_number
                excel.save(response)
                return response
            else:
                return HttpResponse(u"无对帐单生成")
        else:
            with closing(StringIO()) as buff:
                zf = zipfile.ZipFile(buff, mode="w")
                for userprofile in UserProfile.objects.all():
                    excel=get_duizhangdan(userprofile.customer_number,for_check=True)
                    if excel:
                        buff2=StringIO()
                        excel.save(buff2)
                        zf.writestr("%s-DuiZhangDan.xls" % userprofile.customer_number,buff2.getvalue())

                zf.close()
                ff = buff.getvalue()
            response = HttpResponse(content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename=DuiZhangDan.zip'
            response.write(ff)
            return response
    else:
        excel = get_duizhangdan(user.userprofile.customer_number,for_check=False)
        if excel:
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=%s-DuiZhangDan.xls' % user.userprofile.customer_number
            excel.save(response)
            return response
    return HttpResponse(u"无对帐单生成")

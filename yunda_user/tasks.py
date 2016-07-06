# -*- coding: utf-8 -*-
#from celery import task
from django.shortcuts import  get_object_or_404
import logging
from parcel.models import Level, IntlParcel
from userena.models import UserProfile
logger = logging.getLogger('yunda.django.async')
from django.conf import settings
import xmlrpclib
import pytz
from datetime import datetime
from yunda_user import models as accounts_models
from userena import signals as userena_signals
from django.contrib.auth.models import User
from userena import settings as userena_settings
from yunda_commen.commen_utils import get_seq_by_code


#@task
def user_info_sync_to_erp(user):

    user.userprofile.sync_status = 'waiting_to_sync'
    user.userprofile.save()

    # TODO sync
    url = getattr(settings, 'ODOO_URL', 'localhost:8069')
    username = getattr(settings, 'ODOO_USERNAME', '')
    password = getattr(settings, 'ODOO_PASSWORD', '')
    db = getattr(settings, 'ODOO_DB', '')
    common = xmlrpclib.ServerProxy('%s/xmlrpc/2/common' % url)
    uid = common.authenticate(db, username, password, {})
    models = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % url)
    try:
        id = models.execute_kw(db, uid, password, 'res.partner', 'create_or_update', [[{
            'name': user.get_full_name() or user.email,
            'email':user.email,
            'customer':True,
            'street':u"%s %s %s" % (user.userprofile.street or '', user.userprofile.hause_number or '', user.userprofile.street_add or ''),
            'street2':user.userprofile.company or '',
            'zip':user.userprofile.postcode or '',
            'city':(u"%s %s" % (user.userprofile.state or '', user.userprofile.city or '')).strip(),
            'phone':user.userprofile.tel or '',
            'fax':user.userprofile.fax or '',
            'vat':user.userprofile.vat_id or '',
            'yunda_internal_customer_number':user.userprofile.customer_number,

            'active':True,
            'type':'default',
            'currency_type':user.userprofile.deposit_currency_type,
            }]])

        logger.debug('customer synced to erp')
        user.userprofile.sync_status = 'synced'
        user.userprofile.save()
    except Exception as e:
        logger.error(e)
        user.userprofile.sync_status = 'error'
        user.userprofile.save()

    return u'%s synced to erp' % user.userprofile.customer_number

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
    company_code = getattr(settings, 'ODOO_COMPANY_CODE', '')

    common = xmlrpclib.ServerProxy('%s/xmlrpc/2/common' % url)
    uid = common.authenticate(db, username, password, {})
    models = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % url)


    try:
        histories = models.execute_kw(db, uid, password,
                                 'yunda2.accounting.deposit.record',
                                 'get_records4zhuanyun',
                                 [],
                                 {'company_code':company_code})
        print histories;
        ids = []
        for history in histories:
            userprofile = get_object_or_404(UserProfile, customer_number__iexact=history['customer_number'])
            dt = datetime.strptime(history['created_at'], "%Y-%m-%d %H:%M:%S")
            utc_dt = pytz.utc.localize(dt, is_dst=None)

            obj = accounts_models.DepositTransferNew(user_id=userprofile.user_id,
                                    created_at=utc_dt.astimezone(local),
                                    amount=history['amount'],
                                    origin=history['origin'],
                                    ref=history['ref'],
                                    )
            obj.save()
            ids.append(history['id'])

            logger.debug('Deposit transfer synced from erp')
        models.execute_kw(db, uid, password,
                                 'yunda2.accounting.deposit.record',
                                 'write',
                                 [ids, {'state_sync':'synced'}])
    except Exception as e:
        logger.error(e)

def get_my_deposit(customer_number):
    url = getattr(settings, 'ODOO_URL', 'localhost:8069')
    username = getattr(settings, 'ODOO_USERNAME', '')
    password = getattr(settings, 'ODOO_PASSWORD', '')
    db = getattr(settings, 'ODOO_DB', '')
    common = xmlrpclib.ServerProxy('%s/xmlrpc/2/common' % url)
    uid = common.authenticate(db, username, password, {})
    models = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % url)

    result = models.execute_kw(db, uid, password,
        'res.partner', 'search_read',
        [[['yunda_internal_customer_number', '=', customer_number]]],
        {'fields': ['deposit', 'deposit_in_security'], 'limit': 1})
    return result and result[0]


# create customer number then sync to erp
def sync_to_erp(sender, user, **kwargs):
    if not user.userprofile.customer_number:
        if user.userprofile.deposit_currency_type == 'eur':
            user.userprofile.customer_number = userena_settings.USERENA_CUSTOMER_NUMBER_PREFIX + get_seq_by_code(userena_settings.USERENA_CUSTOMER_NUMBER_SEQ_CODE, True)
        elif user.userprofile.deposit_currency_type == 'cny':
            user.userprofile.customer_number = userena_settings.USERENA_KEHU_NUMBER_PREFIX + get_seq_by_code(userena_settings.USERENA_KEHU_NUMBER_SEQ_CODE, True)
    if not user.userprofile.level:
        try:
            level=Level.objects.get(code="default")
            user.userprofile.level=level
        except Level.DoesNotExist:
            pass
    user.userprofile.sync_status = 'need_to_sync'
    user.userprofile.save()
    #user_info_sync_to_erp(user)
    # tasks.user_info_sync_to_erp.delay(user)
# connect the signal to handler

userena_signals.signup_complete.connect(sync_to_erp)
userena_signals.activation_complete.connect(sync_to_erp)
userena_signals.confirmation_complete.connect(sync_to_erp)
userena_signals.profile_change.connect(sync_to_erp)

def all_user_info_sync_to_erp():

    all_users = User.objects.filter(is_active=True, is_staff=False, is_superuser=False).all()

    # TODO sync
    url = getattr(settings, 'ODOO_URL', 'localhost:8069')
    username = getattr(settings, 'ODOO_USERNAME', '')
    password = getattr(settings, 'ODOO_PASSWORD', '')
    db = getattr(settings, 'ODOO_DB', '')
    common = xmlrpclib.ServerProxy('%s/xmlrpc/2/common' % url)
    uid = common.authenticate(db, username, password, {})
    models = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % url)
    vals = []
    for user in all_users:
        if user.username ==u"AnonymousUser": continue
        vals.append({
            'name': user.get_full_name() or user.email,
            'email':user.email,
            'customer':True,
            'street':u"%s %s %s" % (user.userprofile.street or '', user.userprofile.hause_number or '', user.userprofile.street_add or ''),
            'street2':user.userprofile.company or '',
            'zip':user.userprofile.postcode or '',
            'city':(u"%s %s" % (user.userprofile.state or '', user.userprofile.city or '')).strip(),
            'phone':user.userprofile.tel or '',
            'fax':user.userprofile.fax or '',
            'vat':user.userprofile.vat_id or '',
            'yunda_internal_customer_number':user.userprofile.customer_number or '',

            'active':True,
            'type':'default',
            'currency_type':'cny',
            })
    try:
        id = models.execute_kw(db, uid, password, 'res.partner', 'create_or_update', [vals])

        logger.debug('customer synced to erp')
        user.userprofile.sync_status = 'synced'
        user.userprofile.save()
    except Exception as e:
        logger.error(e)
        user.userprofile.sync_status = 'error'
        user.userprofile.save()

    return u'synced to all user'

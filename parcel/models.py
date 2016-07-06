# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.models import User
from datetime import datetime
from jsonfield import JSONField
from django.core import validators as field_validators
from django.core.exceptions import ValidationError
import re
import hashlib
from django.conf import settings
import xmlrpclib
from pypinyin import lazy_pinyin, NORMAL
import base64
import requests
import xml.etree.ElementTree as ET
from django.core.mail import send_mail
import math
import json
import logging
logger = logging.getLogger('django')

# Create your models here.
def _zh2py(hz):
        if not hz: return u''
        hz = hz.replace(u'，', ',')
        hz = hz.replace(u'。', '.')
        hz = hz.replace(u'；', ';')
        hz = hz.replace(u'：', ':')
        hz = hz.replace(u'（', '(')
        hz = hz.replace(u'）', ')')
        hz = hz.replace(u'《', '<')
        hz = hz.replace(u'》', '>')
        hz = hz.replace(u'！', '!')
        hz = hz.replace(u'？', '?')
        hz = hz.replace(u'“', '"')
        hz = hz.replace(u'”', '"')
        hz = hz.replace(u'、', ',')
        hans = lazy_pinyin(hz, NORMAL)
        # TODO algorithmus zu verbessern
        all = u""
        for hanz in hans:
            all += hanz[0:1].upper()
            if len(hanz) > 1:
                all += hanz[1:]
        return all
def field_validator_only_alphabeta_num(value):
    p = re.compile(u'^[a-zA-Z0-9\s\-,\+\.\(\)äÄöÖüÜ]+$')
    if not p.match(value):
        raise ValidationError(_('Only german/english alphabeta, numbers, and ",.-()" allowed: %(value)s'), params={'value': value},)

def field_validator_only_chinese(value):
    p = re.compile(u'^[\s\u4e00-\u9fa5]+$')
    if not p.match(value):
        raise ValidationError(_('Only chinese allowed: %(value)s'), params={'value': value},)

def field_validator_chinese_and_alphabeta(value):
    p = re.compile(u'^[a-zA-Z0-9\s\-,\.\(\)\u4e00-\u9fa5]+$')
    if not p.match(value):
        raise ValidationError(_('Only chinese, alphabeta, number and "-,.()" allowed: %(value)s'), params={'value': value},)

def field_validator_chinese_mobile_phone(value):
    p = re.compile(u'1[1-9][0-9]{9}')
    if not p.match(value):
        raise ValidationError(_('Chinese mobile number wrong.pls without 0086 or +86: %(value)s'), params={'value': value},)

def field_validator_chinese_postcode(value):
    p = re.compile(u'[0-9]{6}')
    if not p.match(value):
        raise ValidationError(_('Chinese postcode should be 6 digits, not with 0 start: %(value)s'), params={'value': value},)

def field_validator_german_postcode(value):
    p = re.compile(u'[0-9]{5}')
    if not p.match(value):
        raise ValidationError(_('German postcode should be 5 digits: %(value)s'), params={'value': value},)


class ParcelType(models.Model):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=30)
    description = models.TextField(default="Parcel description")
    show_to_all = models.NullBooleanField(default=False)
    
    def __unicode__(self):
        return u"%s(%s)" % (self.name, self.code)
    

class IntlParcel(models.Model): 
    yid = models.CharField(_("YID"), max_length="40", blank=True)
    
    sender_name = models.CharField(_('Sender name'), max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_name2 = models.CharField(_('Sender name2'), blank=True, max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_company = models.CharField(_('Sender company'), blank=True, max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_state = models.CharField(_('Sender state'), blank=True, max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_city = models.CharField(_('Sender city'), max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_postcode = models.CharField(_('Sender postcode'), max_length=5,)
    sender_street = models.CharField(_('Sender street'), max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_add = models.CharField(_('Sender street addition'), blank=True, max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_hause_number = models.CharField(_('Sender hause number'), max_length=10, validators=[field_validator_only_alphabeta_num])
    sender_tel = models.CharField(_('Sender telephone'), max_length=15)
    sender_email = models.EmailField(_('Sender email'), blank=True, validators=[field_validators.EmailValidator])
    sender_country = models.CharField(_('Sender country'), max_length=2, default="DE")
    
    receiver_name = models.CharField(_('Receiver name'), max_length=50, validators=[field_validator_only_chinese])
    receiver_company = models.CharField(_('Receiver company'), blank=True, max_length=50, validators=[field_validator_chinese_and_alphabeta])
    receiver_province = models.CharField(_('Receiver province'), max_length=20, validators=[field_validator_only_chinese])
    receiver_city = models.CharField(_('Receiver city'), blank=True, max_length=20, validators=[field_validator_only_chinese])
    receiver_district = models.CharField(_('Receiver district'), blank=True, max_length=20, validators=[field_validator_only_chinese])
    receiver_postcode = models.CharField(_('Receiver postcode'), blank=True, max_length=6, validators=[field_validator_chinese_postcode])
    receiver_address = models.CharField(_('Receiver address'), max_length=50, validators=[field_validator_chinese_and_alphabeta])
    receiver_address2 = models.CharField(_('Receiver address2'), blank=True, max_length=50, validators=[field_validator_chinese_and_alphabeta])
    receiver_mobile = models.CharField(_('Receiver mobilephone'), max_length=11, validators=[field_validator_chinese_mobile_phone])
    receiver_email = models.EmailField(_('Receiver email'), blank=True, validators=[field_validators.EmailValidator])
    receiver_country = models.CharField(_('Receiver country'), max_length=2, default="CN")
    
    ref = models.CharField(_('Ref number'), max_length=50, blank=True)
    
    weight_kg = models.FloatField(_('Weight (kg)'), default=0.1, validators=[field_validators.MinValueValidator(0.01)])
    length_cm = models.FloatField(_('Length (cm)'), default=0.1, validators=[field_validators.MinValueValidator(0.01)])
    width_cm = models.FloatField(_('Width (cm)'), default=0.1, validators=[field_validators.MinValueValidator(0.01)])
    height_cm = models.FloatField(_('Height (cm)'), default=0.1, validators=[field_validators.MinValueValidator(0.01)])
    real_weight_kg = models.FloatField(default=0.1, validators=[field_validators.MinValueValidator(0.01)])
    real_length_cm = models.FloatField(default=0.1, validators=[field_validators.MinValueValidator(0.01)])
    real_width_cm = models.FloatField(default=0.1, validators=[field_validators.MinValueValidator(0.01)])
    real_height_cm = models.FloatField(default=0.1, validators=[field_validators.MinValueValidator(0.01)])
    booked_fee = models.FloatField(default=0)     
    user = models.ForeignKey(User)
    currency_type = models.CharField(max_length=3)
    # prices_json = models.TextField()
    json_prices = JSONField(default={})
    
    created_at = models.DateTimeField(default=datetime.now)
    printed_at = models.DateTimeField(_('Printed at'), null=True, blank=True) 
    yde_number = models.CharField(_("Order number"), max_length="20", blank=True)
    SFZ_STATUSES = (("0", u"不需身份证"), ("1", u"已上传"), ("2", u"未上传"))
    sfz_status = models.CharField(default="2", max_length=1, choices=SFZ_STATUSES, blank=True)
    
    type = models.ForeignKey(ParcelType, related_name="intlparcels")
    # 与type有关的属性
    
    # # yd/yd_retoure
    CN_CUSTOMS_PAY_BYS = (("sender", u"发件人"), ("receiver", u"收件人"),)
    cn_customs_paid_by = models.CharField(default="sender", max_length=10, choices=CN_CUSTOMS_PAY_BYS, blank=True)
    pdf_info = models.TextField(blank=True, default="")
    
    # # yd/yd_retoure/dhl_eco/dhl_pre/postnl
    tracking_number = models.CharField(max_length="20", blank=True)
    tracking_number_created_at = models.DateTimeField(blank=True, null=True)    
    
    # # yd_retoure/dhl_eco/dhl_pre/postnl
    retoure_tracking_number = models.CharField(max_length="20", blank=True)
    retoure_routing_code = models.CharField(max_length="20", blank=True)
    retoure_tracking_number_created_at = models.DateTimeField(blank=True, null=True)
    
    # # 
    STATUSES = (
            ('draft', u'草稿'),
            ('confirmed', u'确认提交'),
            ('proccessing_at_yde', u'韵达欧洲处理中'),
            ('transit_to_destination_country', u'运输至目的国家途中'),
            ('custom_clearance_at_destination_country', u'目的国清关中'),
            ('distributing_at_destination_country', u'目的国中转派送'),
            ('distributed_at_destination_country', u'包裹已送达'),
            ('error', u'异常，等待处理'),
            )
    status = models.CharField(u'状态', max_length=50, choices=STATUSES, default="draft")
    is_deleted = models.NullBooleanField(default=False)
    SYNC_STATUSES = (
            ('need_to_sync', u'需要同步至ERP'),
            ('waiting_to_sync', u'等待同步至ERP'),
            ('synced', u'已同步至ERP'),
            )
    sync_status = models.CharField(u'同步至ERP状态', max_length=50, choices=SYNC_STATUSES, default="need_to_sync")
    mawb = models.ForeignKey('Mawb', related_name="mawbs", null=True,blank=True)
    exported_at = models.DateTimeField(null=True, blank=True)
    export_proof_printed_at=models.DateTimeField(null=True,blank=True)
    ############
    # # 20151214
    cn_tax_to_pay_cny = models.FloatField(default=0)
    cn_tax_paid_cny = models.FloatField(default=0)
    customs_code_forced = models.CharField(max_length=20, default="", blank=True)
    processing_msg = models.TextField(blank=True, null=True)
    
    internal_histories = JSONField(default=[], blank=True, null=True)    
    '''
    [{
      "datetime":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
      "staff":user.get_full_name(),
      "description":"CN customs checked"
      }]
    '''
    other_infos = JSONField(default={}, blank=True, null=True)
    '''
    {
        "third_party_tracking_number":"123456",
        "third_party_name":"其它快递"
    }
    '''    
    def get_retoure_routing_code(self):
        return self.retoure_routing_code.replace('.', '').replace(' ', '')
    def get_total_value(self):
        tv = 0
        for detail in self.goodsdetails.all():
            tv += detail.qty * detail.item_price_eur            
        return tv
    def get_sfz_status(self):
        if self.sfz_status == "2":
            if 'yd' in self.type.code:
                url = getattr(settings, 'ODOO_URL', 'localhost:8069')
                username = getattr(settings, 'ODOO_USERNAME', '')
                password = getattr(settings, 'ODOO_PASSWORD', '')
                uid = getattr(settings, 'ODOO_UID', -1)
                db = getattr(settings, 'ODOO_DB', '')
                try:
                    if uid < 1:
                        common = xmlrpclib.ServerProxy('%s/xmlrpc/2/common' % url)
                        uid = common.authenticate(db, username, password, {})
                    models = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % url)
                
                    result = models.execute_kw(db, uid, password,
                        'yunda2.shipment.cn.idcard', 'search_read',
                        # [[['cn_name', '=', self.receiver_name], ['cn_mobile', '=', self.receiver_mobile]]],
                        [[['cn_name', '=', self.receiver_name]]],
                        {'fields': ['idcard_number'], 'limit': 1})
                    if result:
                        self.sfz_status = "1"
                        self.save() 
                except Exception as e:
                    logger.error(e)
                    pass  # TODO 服务器连接不上通知
            else:
                self.sfz_status = "0"
                self.save()
            # checking
        return self.sfz_status
    def get_sfz_number(self):
        if self.sfz_status == "1":
            if 'yd' in self.type.code:
                url = getattr(settings, 'ODOO_URL', 'localhost:8069')
                username = getattr(settings, 'ODOO_USERNAME', '')
                password = getattr(settings, 'ODOO_PASSWORD', '')
                uid = getattr(settings, 'ODOO_UID', -1)
                db = getattr(settings, 'ODOO_DB', '')
                try:
                    if uid < 1:
                        common = xmlrpclib.ServerProxy('%s/xmlrpc/2/common' % url)
                        uid = common.authenticate(db, username, password, {})
                    models = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % url)
                
                    result = models.execute_kw(db, uid, password,
                        'yunda2.shipment.cn.idcard', 'search_read',
                        [[['cn_name', '=', self.receiver_name],
                          # ['cn_mobile', '=', self.receiver_mobile]
                          ]],
                        {'fields': ['idcard_number'], 'limit': 1})
                    return result and result[0]['idcard_number'] or ''
                except:
                    # TODO 服务器连接不上通知
                    return ''
        return False
    
    def get_sfz_image(self):
        if self.sfz_status == "1":
            if 'yd' in self.type.code:
                url = getattr(settings, 'ODOO_URL', 'localhost:8069')
                username = getattr(settings, 'ODOO_USERNAME', '')
                password = getattr(settings, 'ODOO_PASSWORD', '')
                uid = getattr(settings, 'ODOO_UID', -1)
                db = getattr(settings, 'ODOO_DB', '')
                try:
                    if uid < 1:
                        common = xmlrpclib.ServerProxy('%s/xmlrpc/2/common' % url)
                        uid = common.authenticate(db, username, password, {})
                    models = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % url)
                
                    result = models.execute_kw(db, uid, password,
                        'yunda2.shipment.cn.idcard', 'search_read',
                        [[['cn_name', '=', self.receiver_name],
                          # ['cn_mobile', '=', self.receiver_mobile]
                          ]],
                        {'fields': ['idcard_number', 'image_file'], 'limit': 1})
                    return result and (result[0]['idcard_number'], result[0]['image_file']) or (False, False)
                except:
                    # TODO 服务器连接不上通知
                    return (False, False)
        return (False, False)
    
    def _get_fee(self, weight, length, width, height):
        vWeight = length * width * height / self.json_prices['volume_weight_rate']
        if weight < vWeight:
            weight = vWeight        
        if self.json_prices['type'] == "linear":
            if weight <= self.json_prices['starting_weight_kg']:
                return self.json_prices['starting_price'];
            else:                
                return math.ceil((weight - self.json_prices['starting_weight_kg']) / self.json_prices['weight_interval']) * self.json_prices['continuing_price'] + self.json_prices['starting_price'];
        else:
            return self.json_prices["%.0f" % (math.ceil(weight / self.json_prices['weight_interval']) * 10 * self.json_prices['weight_interval'])];
    
    def get_fee(self):
        return self._get_fee(self.weight_kg, self.length_cm, self.width_cm, self.height_cm)
    
    def get_real_fee(self):
        return self._get_fee(self.real_weight_kg, self.real_length_cm, self.real_width_cm, self.real_height_cm)
    
    def get_cn_customs(self):
        # TODO don't forget to update when new cn customs
        ############
        # # 20151214
        if self.customs_code_forced:
            return self.customs_code_forced
        if 'dhl' in self.type.code:
            return 'dhl'
        elif 'postnl' in self.type.code:
            return 'postnl'
        elif 'yd' in self.type.code:
            code = 'ctu'
            for detail in self.goodsdetails.all():
                if detail.cn_customs_tax_name not in [u'奶粉', u'成人奶粉', u'婴儿奶粉', u'铁元']:
                    return 'default'
                return code
        else:
            return ''
    def get_receiver_name_en(self):
        return _zh2py(self.receiver_name)
    def get_receiver_company_en(self):
        return _zh2py(self.receiver_company)
    def get_receiver_province_en(self):
        return _zh2py(self.receiver_province)
    def get_receiver_city_en(self):
        return _zh2py(self.receiver_city)
    def get_receiver_district_en(self):
        return _zh2py(self.receiver_district)
    def get_receiver_address_en(self):
        return _zh2py(self.receiver_address)
    def get_receiver_address2_en(self):
        return _zh2py(self.receiver_address2)
            
    
class GoodsDetail(models.Model):
    intl_parcel = models.ForeignKey(IntlParcel, null=True, related_name='goodsdetails')
    description = models.CharField(u'货物描述', max_length=50,)
    cn_customs_tax_catalog_name = models.CharField(u'主分类', max_length=50, blank=True)
    cn_customs_tax_name = models.CharField(u'二级分类', max_length=50, blank=True)
    qty = models.FloatField(u'数量',)
    item_net_weight_kg = models.FloatField(u'单件净重 Kg',)
    item_price_eur = models.FloatField(u'单价 €',)
    original_country = models.CharField(u'原产地', max_length=2, default='DE')
    
    ############
    # # 20151214
    product = models.ForeignKey("Product", null=True, blank=True, on_delete=models.SET_NULL)

    def __unicode__(self):
        return self.intl_parcel.yde_number + " " + self.description
    def get_total_value(self):
        return self.item_price_eur * self.qty

class History(models.Model):
    intl_parcel = models.ForeignKey(IntlParcel, null=True, related_name='histories')
    created_at = models.DateTimeField(u'记录时间', null=True, default=datetime.now)
    description = models.TextField(u'记录内容',)
    visible_to_customer = models.BooleanField(default=True)
    staff = models.ForeignKey(User, null=True, blank=True)
    tracking_pushed = models.BooleanField(default=False)
    tracking_pushed_at = models.DateTimeField(null=True, blank=True)

class Level(models.Model):
    code = models.CharField(max_length=10, default="test")
    name = models.CharField(max_length=30, default="Test")
    def __unicode__(self):
        return u"%s(%s)" % (self.name, self.code)

    
class PriceLevel(models.Model):
    level = models.ForeignKey(Level)
    currency_type = models.CharField(max_length=3, default="cny")
    # prices_json = models.TextField(default='''{type:"table", volume_weight_rate:100000, table:{"1.0":10,"2.0":20}}
# {type:"linear", volume_weight_rate:100000, starting_weight_kg:1, starting_price:10, continuing_weight_kg:0.5, continuing_price:2.5}''')
    parcel_type = models.ForeignKey(ParcelType)
    json_prices = JSONField(default='''{"type":"table","volume_weight_rate":6000,
"1.0":10,
"2.0":20,
"3.0":10,
"4.0":10,
"5.0":10,
"6.0":10,
"7.0":10,
"8.0":10,
"9.0":10,
"10.0":10,
"11.0":10,
"12.0":10,
"13.0":10,
"14.0":10,
"15.0":10,
"16.0":10,
"17.0":10,
"18.0":10,
"19.0":10,
"20.0":10,
"21.0":10,
"22.0":10,
"23.0":10,
"24.0":10,
"25.0":10,
"26.0":10,
"27.0":10,
"28.0":10,
"29.0":10,
"30.0":10}

{"type":"linear","volume_weight_rate":6000,"starting_weight_kg":1,"starting_price":9.5,"continuing_weight_kg":0.5,"continuing_price":2.4}''')
    def __unicode__(self):
        return u"%s-%s-%s" % (self.level, self.parcel_type, self.currency_type)
    
class Gss(models.Model):
    qr_api_url = models.CharField(max_length=100)
    qr_traderId = models.CharField(max_length=50)
    qr_passwd = models.CharField(max_length=50)
    qr_buz_type = models.CharField(max_length=50)
    qr_version = models.CharField(max_length=50)
    qr_data_style = models.CharField(max_length=50)
    qr_sign_infor = models.CharField(max_length=50, blank=True)
    
    add_tracking_api_url = models.CharField(max_length=100)
    get_tracking_api_url = models.CharField(max_length=100)
    tracking_username = models.CharField(max_length=50)
    tracking_passwd = models.CharField(max_length=50)
    tracking_version = models.CharField(max_length=50)
    
    cn_customs_code = models.CharField(max_length=50)
        
    def __unicode__(self):
        return u"%s" % self.cn_customs_code

    def save(self, *args, **kwargs):
        encryptString = "buz_type"
        encryptString += self.qr_buz_type
        encryptString += "data_style"
        encryptString += self.qr_data_style
        encryptString += "traderId"
        encryptString += self.qr_traderId
        encryptString += "version"
        encryptString += self.qr_version
        encryptString += self.qr_passwd
        
        t_encrypt = "account"
        t_encrypt += self.tracking_username
        t_encrypt += "version"
        t_encrypt += self.tracking_version
        t_encrypt += self.tracking_passwd
        
        self.qr_sign_infor = hashlib.md5(encryptString).hexdigest()
        super(Gss, self).save(*args, **kwargs)


class Mawb(models.Model):
    mawb_number = models.CharField("Name",max_length=20, unique=True, validators=[field_validator_only_alphabeta_num])
    number=models.CharField(max_length=20,blank=True)
    cn_customs = models.CharField(max_length=20, validators=[field_validator_only_alphabeta_num])
    need_receiver_name_mobiles = models.BooleanField(default=False)
    need_total_value_per_sender = models.BooleanField(default=False)
    receiver_name_mobiles = JSONField(default=[], null=True, blank=True)  # ["name+mobile"]
    created_at = models.DateTimeField(default=datetime.now)
    STATUSES = (
            ('draft', u'Draft'),
            ('warehouse_open', u'Open at Warehouse'),
            ('warehouse_closed', u'Closed at Warehouse'),
            ('transfered_to_partner', u'Transfered to partner'),
            ('flied_to_dest', u'Flied to destination country'),
            ('landed_at_dest', u'Landed at destination country'),
            ('customs_cleared', u'Customs clearance finished at destination country'),
            ('error', u'Error'),
            )
    status = models.CharField(max_length=50, choices=STATUSES, default="draft")
    histories = JSONField(default=[], blank=True, null=True)

    def __unicode__(self):
        return u"%s" % self.mawb_number

class Batch(models.Model):
    mawb = models.ForeignKey(Mawb, related_name="batches")
    order_number = models.IntegerField()
    sign = models.CharField(max_length=20, validators=[field_validator_only_alphabeta_num])
    color = models.CharField(max_length=7)    
    total_value_per_sender = JSONField(default={}, null=True, blank=True)  # {"name+tel",100}
    max_value = models.FloatField()
    yids = JSONField(default=[], null=True, blank=True)  # [yid]
    STATUSES = (
            ('warehouse_open', u'Open at Warehouse'),
            ('warehouse_closed', u'Closed at Warehouse'),
            ('export_customs_cleared', u'Export customs cleared'),
            ('error', u'Error'),
            )
    status = models.CharField(max_length=50, choices=STATUSES, default="warehouse_open")
    histories = JSONField(default=[], null=True, blank=True)

def add_to_mawb(mawb_number, parcel_yid, receiver_name_mobile=None, sender_name_tel=None, total_value=0):
    mawb = Mawb.objects.get(mawb_number=mawb_number)
    if mawb.need_receiver_name_mobiles:
        receiver_name_mobiles = mawb.receiver_name_mobiles
        if receiver_name_mobile in mawb.receiver_name_mobiles:
            return False, False  # goto waiting
        else:
            if mawb.need_total_value_per_sender:
                batches = mawb.batches.filter(status="warehouse_open").order_by('order_number')
                for batch in batches:
                    values = batch.total_value_per_sender
                    if sender_name_tel not in values:
                        
                        values[sender_name_tel] = total_value
                        yids = batch.yids
                        yids.append(parcel_yid)
                        batch.yids = yids
                        batch.total_value_per_sender = values
                        batch.save()
                        receiver_name_mobiles.append(receiver_name_mobile)
                        mawb.receiver_name_mobiles = receiver_name_mobiles
                        mawb.save()
                        return batch.color, batch.sign                
                    else:
                        if values[sender_name_tel] + total_value > batch.max_value:
                            continue
                        else:
                            values[sender_name_tel] += total_value
                            yids = batch.yids
                            yids.append(parcel_yid)
                            batch.yids = yids
                            batch.total_value_per_sender = values
                            batch.save()
                            receiver_name_mobiles.append(receiver_name_mobile)
                            mawb.receiver_name_mobiles = receiver_name_mobiles
                            mawb.save()
                            return batch.color, batch.sign
                return False, False  # goto waiting
                        
            else:
                batch = mawb.batches.filter(status="warehouse_open")[0]
                yids = batch.yids
                yids.append(parcel_yid)
                batch.yids = yids
                batch.save()
                receiver_name_mobiles.append(receiver_name_mobile)
                mawb.receiver_name_mobiles = receiver_name_mobiles
                mawb.save()
                return batch.color, batch.sign 
    else:
        if mawb.need_total_value_per_sender:
            batches = mawb.batches.filter(status="warehouse_open").order_by('order_number')
            for batch in batches:
                values = batch.total_value_per_sender
                if sender_name_tel not in values:
                    
                    values[sender_name_tel] = total_value
                    batch.total_value_per_sender = values
                    yids = batch.yids
                    yids.append(parcel_yid)
                    batch.yids = yids
                    batch.save()
                    return batch.color, batch.sign                
                else:
                    if values[sender_name_tel] + total_value > batch.max_value:
                        continue
                    else:
                        values[sender_name_tel] += total_value
                        batch.total_value_per_sender = values
                        yids = batch.yids
                        yids.append(parcel_yid)
                        batch.yids = yids
                        batch.save()
                        return batch.color, batch.sign
            return False, False  # goto waiting
                        
        else:
            batch = mawb.batches.filter(status="warehouse_open")[0]
            yids = batch.yids
            yids.append(parcel_yid)
            batch.yids = yids
            batch.save()
            return batch.color, batch.sign

############
# # 20151214   
class Product(models.Model):
    en_name = models.CharField(max_length=100)
    cn_name = models.CharField(max_length=100)
    
    description = models.CharField(max_length=100)    
    cn_tax_name = models.CharField(max_length=100)
    cn_tax_number = models.CharField(max_length=10)
    cn_tax_standard_price_cny = models.FloatField()
    cn_tax_rate = models.FloatField()
    cn_tax_unit = models.CharField(max_length=10)
    cn_real_unit_tax_cny = JSONField(default=[],blank=True,null=True)  # {"msd":50,"ctu":80}
    
    price_eur = models.FloatField()
    unit = models.CharField(max_length=10)
    unit_net_weight_volumn = models.FloatField()
    net_weight_volumn_unit = models.CharField(max_length=5)  # kg or ml
    
    sku = models.CharField(max_length=50, unique=True)
    yid = models.CharField(max_length=40, blank=True)
    url = models.CharField(max_length=256)
    small_pic_url = models.CharField(max_length=50, blank=True)
    price_pic_url = models.CharField(max_length=50, blank=True)
    
    product_categories = models.ManyToManyField("ProductCategory")
    product_brand = models.ForeignKey("ProductBrand", null=True, blank=True)
    
    histories = JSONField(default=[], blank=True, null=True)
  
class ProductCategory(models.Model):
    product_main_category = models.ForeignKey("ProductMainCategory")
    cn_name = models.CharField(max_length=100,)
    en_name = models.CharField(max_length=100,)
    histories = JSONField(default=[], blank=True, null=True)
    def __unicode__(self):
        return u"%s: %s-%s" % (self.product_main_category, self.cn_name, self.en_name)
    class Meta:
        unique_together = (("cn_name", "product_main_category"), ("en_name", "product_main_category"),)

    
class ProductMainCategory(models.Model):
    cn_name = models.CharField(max_length=100, unique=True)
    en_name = models.CharField(max_length=100, unique=True)
    histories = JSONField(default=[], blank=True, null=True)
    def __unicode__(self):
        return u"%s-%s" % (self.cn_name, self.en_name)

class ProductBrand(models.Model):
    cn_name = models.CharField(max_length=100, unique=True)
    en_name = models.CharField(max_length=100, unique=True)
    histories = JSONField(default=[], blank=True, null=True)
    def __unicode__(self):
        return u"%s-%s" % (self.cn_name, self.en_name)
    
class CnCustoms(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)
    settings = JSONField(default=
'''{"need_receiver_name_mobiles":true,
"need_total_value_per_sender":true,
"total_value_per_sender_eur":1000,
"need_sfz":true,
"batch_settings":[{"order_number":1,"sign":"","color":""},
{"order_number":2,"sign":"","color":""}
]}''')
    

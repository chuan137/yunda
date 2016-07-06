# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.models import User
from django import forms
from yunda_user.models import Branch
from yunda_commen.commen_utils import get_seq_by_code, get_settings
from datetime import datetime
from math import ceil
from lbl_retoure_label import Dhl_Retoure
from django.conf import settings
from django.core import validators as field_validators
from django.core.exceptions import ValidationError
import re
from django.shortcuts import get_object_or_404
import hashlib
#from celery.worker.strategy import default

gettext = lambda s: s
DHL_RETOURE_NUMBER_SEQ_CODE = getattr(settings, 'DHL_RETOURE_NUMBER_SEQ_CODE', False)
ADRDRESS_TEMPLATE_NUMBER_SEQ_CODE = getattr(settings, 'ADRDRESS_TEMPLATE_NUMBER_SEQ_CODE', False)

def _get_check_digit(number):
    # _code = str(code)
    a = 0
    b = 0
    d = True
    for c in str(number):
        if d:
            a += int(c)
        else:
            b += int(c)
        d = not d
    a = a * 4 + b * 9
    a = str(a)
    if a[len(a) - 1:] == '0':
        return 0
    else:
        return 10 - int(a[len(a) - 1:])

def field_validator_only_alphabeta_num(value):
    p = re.compile(u'^[a-zA-Z0-9\s\-,.()äÄöÖüÜ]+$')
    if not p.match(value):
        raise ValidationError(_('Only german/english alphabeta, numbers, and ",.-()" allowed: %(value)s'), params={'value': value},)

def field_validator_only_chinese(value):
    p = re.compile(u'^[\s\u4e00-\u9fa5]+$')
    if not p.match(value):
        raise ValidationError(_('Only chinese allowed: %(value)s'), params={'value': value},)

def field_validator_chinese_and_alphabeta(value):
    p = re.compile(u'^[a-zA-Z0-9\s\-,.()\u4e00-\u9fa5]+$')
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

# Create your models here.
class ParcelType(models.Model):
    name = models.CharField(_('Name'), max_length=50)
    code = models.CharField(_('Code'), max_length=50, default="default")
    description = models.TextField(_('Description'))
    to_country_code = models.CharField(_('Destination country'), max_length=2, help_text=_('ISO country code.'))
    max_weight_kg = models.FloatField(_('Max weight (kg)'))
    need_shenfenzheng = models.BooleanField(_('Need shenfenzheng'), default=True)
    customs = models.CharField(_('Customs '), max_length=500, help_text=_('Use comma between different customs.'))
    has_customs_tax = models.BooleanField(_('Has CN customs tax'), default=True, blank=True)
    
    # ## default price info
    start_price_eur = models.FloatField(_('Start price (EUR)'))
    start_weight_kg = models.FloatField(_('Start weight (KG)'))
    continuing_price_eur = models.FloatField(_('Continuing price (EUR)'))
    continuing_weight_kg = models.FloatField(_('Continuing weight (KG)'))
    volume_weight_rate = models.FloatField(_('Volume weight rate'))
    
    branch_start_price_eur = models.FloatField(_('Branch start price (EUR)'))
    branch_start_weight_kg = models.FloatField(_('Branch start weight (KG)'))
    branch_continuing_price_eur = models.FloatField(_('Branch continuing price (EUR)'))
    branch_continuing_weight_kg = models.FloatField(_('Branch continuing weight (KG)'))
    branch_volume_weight_rate = models.FloatField(_('Branch volume weight rate'))
    
    # yde number
    next_value = models.BigIntegerField(_('Next value'), default=1)
    prefix = models.CharField(max_length=10, blank=True)
    digit_length = models.SmallIntegerField(default=0)
    draft_next_value = models.BigIntegerField(default=1)
       
    # ## end default price info
    
    def __unicode__(self):
        return self.name
    
    def get_next_yde_number(self):
        result = self.prefix + "%0" + str(self.digit_length) + "d%d"
        result = result % (self.next_value, _get_check_digit(self.next_value))
        self.next_value = self.next_value + 1
        self.save()
        return result
    
    def get_next_draft_yde_number(self):
        result = "draft%0" + str(self.digit_length) + "d%d"
        result = result % (self.draft_next_value, _get_check_digit(self.draft_next_value))
        self.draft_next_value = self.draft_next_value + 1
        self.save()
        return result
    
    def get_price_by_user(self, user, is_user_id=False):
        if is_user_id:
            user = User.objects.get(pk=user)
        try:
            price = CustomerParcelPrice.objects.get(customer=user, parcel_type=self)
            start_price_eur = price.start_price_eur
            start_weight_kg = price.start_weight_kg
            continuing_price_eur = price.continuing_price_eur
            continuing_weight_kg = price.continuing_weight_kg
            volume_weight_rate = price.volume_weight_rate
        except CustomerParcelPrice.DoesNotExist:
            start_price_eur = self.start_price_eur
            start_weight_kg = self.start_weight_kg
            continuing_price_eur = self.continuing_price_eur
            continuing_weight_kg = self.continuing_weight_kg
            volume_weight_rate = self.volume_weight_rate
        try:
            branch_price = BranchParcelPrice.objects.get(branch=user.userprofile.branch, parcel_type=self)
            branch_start_price_eur = branch_price.start_price_eur
            branch_start_weight_kg = branch_price.start_weight_kg
            branch_continuing_price_eur = branch_price.continuing_price_eur
            branch_continuing_weight_kg = branch_price.continuing_weight_kg
            branch_volume_weight_rate = branch_price.volume_weight_rate
        except BranchParcelPrice.DoesNotExist:
            branch_start_price_eur = self.branch_start_price_eur
            branch_start_weight_kg = self.branch_start_weight_kg
            branch_continuing_price_eur = self.branch_continuing_price_eur
            branch_continuing_weight_kg = self.branch_continuing_weight_kg
            branch_volume_weight_rate = self.branch_volume_weight_rate
        return (start_price_eur, start_weight_kg, continuing_price_eur, continuing_weight_kg, volume_weight_rate ,
            branch_start_price_eur, branch_start_weight_kg, branch_continuing_price_eur, branch_continuing_weight_kg, branch_volume_weight_rate)
            
class ParcelPriceLevel(models.Model):
    name = models.CharField(max_length=15)
    code = models.CharField(max_length=15)    
    parcel_type = models.ForeignKey(ParcelType)
    CURRENCY_TYPES = (
            ('eur', _('EUR')),
            ('cny', _('CNY')),
            )
    currency_type = models.CharField(_(u'货币类型'), max_length=3, choices=CURRENCY_TYPES, default="draft")
    start_price = models.FloatField(u'首重价格 ￥')
    start_weight_kg = models.FloatField(u'首重重量 Kg')
    continuing_price = models.FloatField(u'续重价格 ￥')
    continuing_weight_kg = models.FloatField(u'续重重量 Kg')
    volume_weight_rate = models.FloatField(u'体积重量比', null=True)
    description = models.TextField(u'说明', blank=True)
    
    def __unicode__(self):
        return self.code + ' - ' + self.name
 
class CustomerParcelPrice(models.Model):
    parcel_type = models.ForeignKey(ParcelType)
    
    start_price_eur = models.FloatField(_('Start price (EUR)'))
    start_weight_kg = models.FloatField(_('Start weight (KG)'))
    continuing_price_eur = models.FloatField(_('Continuing price (EUR)'))
    continuing_weight_kg = models.FloatField(_('Continuing weight (KG)'))
    volume_weight_rate = models.FloatField(_('Volume weight rate'))
    
    branch_start_price_eur = models.FloatField(_('Branch start price (EUR)'))
    branch_start_weight_kg = models.FloatField(_('Branch start weight (KG)'))
    branch_continuing_price_eur = models.FloatField(_('Branch continuing price (EUR)'))
    branch_continuing_weight_kg = models.FloatField(_('Branch continuing weight (KG)'))
    branch_volume_weight_rate = models.FloatField(_('Branch volume weight rate'))
    
    monthly_minimal_qty = models.IntegerField(_('Monthly minimal qty'), default=0)
    branch = models.ForeignKey(Branch, null=True,)
    customer = models.ForeignKey(User, limit_choices_to={'is_staff': False})
    def __unicode__(self):
        return "%s - %s - %s - %d" % (self.branch, self.customer.userprofile.customer_number , self.parcel_type , self.monthly_minimal_qty)

class BranchParcelPrice(models.Model):
    parcel_type = models.ForeignKey(ParcelType)
    
    start_price_eur = models.FloatField(_('Start price (EUR)'))
    start_weight_kg = models.FloatField(_('Start weight (KG)'))
    continuing_price_eur = models.FloatField(_('Continuing price (EUR)'))
    continuing_weight_kg = models.FloatField(_('Continuing weight (KG)'))
    volume_weight_rate = models.FloatField(_('Volume weight rate'))
    
    monthly_minimal_qty = models.IntegerField(_('Monthly minimal qty'), default=0)
    branch = models.ForeignKey(Branch, null=True,)
    def __unicode__(self):
        return "%s - %s - %d" % (self.branch, self.parcel_type, self.monthly_minimal_qty)

class BranchAllowedParcelPrice(models.Model):
    parcel_type = models.ForeignKey(ParcelType)
    
    start_price_eur = models.FloatField(_('Start price (EUR)'))
    start_weight_kg = models.FloatField(_('Start weight (KG)'))
    continuing_price_eur = models.FloatField(_('Continuing price (EUR)'))
    continuing_weight_kg = models.FloatField(_('Continuing weight (KG)'))
    volume_weight_rate = models.FloatField(_('Volume weight rate'))
    
    monthly_minimal_qty = models.IntegerField(_('Monthly minimal qty'), default=0)
    branch = models.ForeignKey(Branch, null=True,)
    is_default = models.BooleanField(default=False)
    
    def __unicode__(self):
        return "%s - %s - %d -%s" % (self.branch, self.parcel_type, self.monthly_minimal_qty, (self.is_default and "default" or ""))
    
PARCELSTATUSES = (
            # #for parcel payment status
            ('pr_pas_unpaid', _('Draft')),
            ('pr_pas_paid', _('Paid')),
            ('pr_pas_need_pay_rest', _('Need pay rest')),
            ('pr_pas_need_pay_rest_complete', _('Complete')),
            ('pr_pas_rest_auto_paid_complete', _('Complete')),
            ('pr_pas_no_rest_complete', _('Complete')),
            # #for parcel cn tax status
            ('pr_cts_unpaid', _('Draft')),
            ('pr_cts_sender_paid', _('Paid by sender')),
            ('pr_cts_sender_pay_need_pay_rest', _('Need pay rest by sender')),
            ('pr_cts_sender_pay_need_pay_rest_complete', _('Complete')),
            ('pr_cts_sender_pay_complete', _('Complete')),
            ('pr_cts_sender_pay_paid_back_complete', _('Complete')),
            ('pr_cts_sender_pay_0tax', _('No Tax')),
            ('pr_cts_sender_pay_0tax_need_pay_rest', _('Need pay')),
            ('pr_cts_sender_pay_0tax_need_pay_rest_complete', _('Complete')),
            ('pr_cts_sender_pay_0tax_rest_auto_paid_complete', _('Complete')),
            ('pr_cts_receiver_pay', _('Receiver will pay')),
            ('pr_cts_receiver_pay_need_pay', _('Need pay by receiver')),
            ('pr_cts_receiver_pay_need_pay_complete', _('Complete')),
            ('pr_cts_receiver_pay_0tax_complete', _('Complete')),
            # #for parcel position status
            ('pr_pos_sender', _('At sender')),
            ('pr_pos_way_from_sender_to_op', _('Way from sender to operation center')),
            ('pr_pos_op', _('At operation center')),
            ('pr_pos_waiting_to_export', _('Waiting to export')),
            ('pr_pos_flied', _('Flied')),
            ('pr_pos_destination_customs', _('At destination customs')),
            ('pr_pos_destination_yunda', _('At destination yunda')),
            ('pr_pos_canceled', _('Canceled')),  # #有且仅有pr_pos_sender、pr_pos_way_from_sender_to_op和pr_pos_op三个状态下可以cancel
            
            # #others
            ('others', _('Others')),
            )
PARCEL_POS_STATUSES = (
            # #for parcel position status
            ('pr_pos_sender', _('At sender')),
            ('pr_pos_way_from_sender_to_op', _('Way from sender to operation center')),
            ('pr_pos_op', _('At operation center')),
            ('pr_pos_waiting_to_export', _('Waiting to export')),
            ('pr_pos_flied', _('Flied')),
            ('pr_pos_destination_customs', _('At destination customs')),
            ('pr_pos_destination_yunda', _('At destination yunda')),
            ('pr_pos_canceled', _('Canceled')),  # #有且仅有pr_pos_sender、pr_pos_way_from_sender_to_op和pr_pos_op三个状态下可以cancel
            
            # #others
            ('others', _('Others')),
            )
PARCEL_PAS_STATUSES = (
            # #for parcel payment status
            ('pr_pas_unpaid', _('Draft')),
            ('pr_pas_paid', _('Paid')),
            ('pr_pas_need_pay_rest', _('Need pay rest')),
            ('pr_pas_need_pay_rest_complete', _('Complete')),
            ('pr_pas_rest_auto_paid_complete', _('Complete')),
            ('pr_pas_no_rest_complete', _('Complete')),
            
            # #others
            ('others', _('Others')),
            )
PARCEL_CTX_STATUSES = (
            # #for parcel cn tax status
            ('pr_cts_unpaid', _('Draft')),
            ('pr_cts_sender_paid', _('Paid by sender')),
            ('pr_cts_sender_pay_need_pay_rest', _('Need pay rest by sender')),
            ('pr_cts_sender_pay_need_pay_rest_complete', _('Complete')),
            ('pr_cts_sender_pay_complete', _('Complete')),
            ('pr_cts_sender_pay_paid_back_complete', _('Complete')),
            ('pr_cts_sender_pay_0tax', _('No Tax')),
            ('pr_cts_sender_pay_0tax_need_pay_rest', _('Need pay')),
            ('pr_cts_sender_pay_0tax_need_pay_rest_complete', _('Complete')),
            ('pr_cts_sender_pay_0tax_rest_auto_paid_complete', _('Complete')),
            ('pr_cts_receiver_pay', _('Receiver will pay')),
            ('pr_cts_receiver_pay_need_pay', _('Need pay by receiver')),
            ('pr_cts_receiver_pay_need_pay_complete', _('Complete')),
            ('pr_cts_receiver_pay_0tax_complete', _('Complete')),
            # #others
            ('others', _('Others')),
            )
class ParcelStatusHistory(models.Model):
    TYPES = (
            ('payment_status', _('Payment status')),
            ('position_status', _('Position status')),
            ('cn_tax_status', _('CN tax status')),
            ('others', _('Others')),
            )
    type = models.CharField(max_length=20, choices=TYPES)
    
    status = models.CharField(max_length=60, choices=PARCELSTATUSES)
    create_at = models.DateTimeField()
    parcel = models.ForeignKey('Parcel', null=True)
    operator = models.ForeignKey(User, null=True)

DHL_RETOURE_LABEL_STATUSES = (
            # #for retoure label payment status
            ('rl_pas_unpaid', _('Draft')),
            ('rl_pas_paid', _('Paid')),
            
            # #for retoure label position status
            ('rl_pos_sender', _('At sender')),
            ('rl_pos_op', _('At operation center')),
            ('rl_pos_canceled', _('Canceled')),  # #有且仅有unpaid状态下可以cancel
            
            # #others
            ('others', _('Others')),
            )
class DhlRetoureLabelStatusHistory(models.Model):
    TYPES = (
            ('payment_status', _('Payment status')),
            ('position_status', _('Position status')),
            ('others', _('Others')),
            )
    type = models.CharField(max_length=20, choices=TYPES)
    
    status = models.CharField(max_length=30, choices=DHL_RETOURE_LABEL_STATUSES)
    create_at = models.DateTimeField()
    dhl_retoure_label = models.ForeignKey('DhlRetoureLabel', null=True)
    operator = models.ForeignKey(User, null=True)
    
    
class Parcel(models.Model):
    type = models.ForeignKey(ParcelType)
    sender_name = models.CharField(_('Sender name'), max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_name2 = models.CharField(_('Sender name2'), blank=True, max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_company = models.CharField(_('Sender company'), blank=True, max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_state = models.CharField(_('Sender state'), blank=True, max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_city = models.CharField(_('Sender city'), max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_postcode = models.CharField(_('Sender postcode'), max_length=5, validators=[field_validator_german_postcode])
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
    
    weight_kg = models.FloatField(_('Weight (kg)'), validators=[field_validators.MinValueValidator(0.01)])
    length_cm = models.FloatField(_('Length (cm)'), validators=[field_validators.MinValueValidator(0.01)])
    width_cm = models.FloatField(_('Width (cm)'), validators=[field_validators.MinValueValidator(0.01)])
    height_cm = models.FloatField(_('Height (cm)'), validators=[field_validators.MinValueValidator(0.01)])
    real_weight_kg = models.FloatField(_('Real weight (kg)'), default=0, blank=True) 
    real_length_cm = models.FloatField(_('Real Length (cm)'), default=0, blank=True)
    real_width_cm = models.FloatField(_('Real Width (cm)'), default=0, blank=True)
    real_height_cm = models.FloatField(_('Real Height (cm)'), default=0, blank=True)
    
    real_cn_customs_tax_cny = models.FloatField(_('Real customs tax (CNY)'), default=0, blank=True)
    
    start_price_eur = models.FloatField(_('Start price (EUR)'), default=0, blank=True)
    start_weight_kg = models.FloatField(_('Start weight (KG)'), default=0.1, blank=True)
    continuing_price_eur = models.FloatField(_('Continuing price (EUR)'), default=0, blank=True)
    continuing_weight_kg = models.FloatField(_('Continuing weight (KG)'), default=0.1, blank=True)
    volume_weight_rate = models.FloatField(_('Volume weight rate'), default=1, blank=True)
    
    branch_start_price_eur = models.FloatField(_('Branch start price (EUR)'), default=0, blank=True)
    branch_start_weight_kg = models.FloatField(_('Branch start weight (KG)'), default=0.1, blank=True)
    branch_continuing_price_eur = models.FloatField(_('Branch continuing price (EUR)'), default=0, blank=True)
    branch_continuing_weight_kg = models.FloatField(_('Branch continuing weight (KG)'), default=0.1, blank=True)
    branch_volume_weight_rate = models.FloatField(_('Branch volume weight rate'), default=1, blank=True)
    
    tracking_number = models.CharField(_('Tracking number'), max_length=15, blank=True)
    tracking_number_created_at = models.DateTimeField(null=True, blank=True)
    yde_number = models.CharField(_('YDE number'), max_length=32, blank=True)
    created_at = models.DateTimeField(_('Created at'), null=True)
    printed_at = models.DateTimeField(_('Printed at'), null=True, blank=True)
    
    sender_pay_cn_customs = models.BooleanField(default=True)
    
    user = models.ForeignKey(User, null=True)
    salesman = models.ForeignKey(User, null=True, related_name="Parcel.salesman", limit_choices_to={'is_staff': True})
    branch = models.ForeignKey('yunda_user.Branch', null=True)
    
    payment_status = models.CharField(max_length=60, default='pr_pas_unpaid', choices=PARCEL_PAS_STATUSES)
    position_status = models.CharField(max_length=60, default='pr_pos_sender', choices=PARCEL_POS_STATUSES)
    cn_tax_status = models.CharField(max_length=60, default='pr_cts_unpaid', choices=PARCEL_CTX_STATUSES)
    
    fee_paid_eur = models.FloatField(default=0)
    cn_tax_paid_cny = models.FloatField(default=0)

    eur_to_cny_rate = models.FloatField(default=8)
    
    is_delete = models.NullBooleanField(default=False)
    
    is_synced = models.NullBooleanField(default=False)
    has_cn_id = models.NullBooleanField(default=False)
    
       
    def __unicode__(self):
        return self.yde_number + "-" + self.tracking_number
    def get_has_cn_id(self):
        if self.has_cn_id: return True
        else:
            try:
                CnShenfengzheng.objects.get(name=self.receiver_name, mobile=self.receiver_mobile)
                self.has_cn_id = True
                self.save()
                return True
            except CnShenfengzheng.MultipleObjectsReturned:
                self.has_cn_id = True
                self.save()
                return True
            except CnShenfengzheng.DoesNotExist:
                return False
    def is_print(self):
        if self.printed_at:
            return True
        else:
            return False
    def get_current_usable_actions(self):
        actions = []
        if self.payment_status == 'pr_pas_unpaid' and self.cn_tax_status == 'pr_cts_unpaid':
            # 新建的parcel
            actions += [  {'name':_('Edit'), 'url':'edit', 'is_form':False},
                        {'name':_('Pay'), 'url':'pay', 'is_form':True}, {'name':_('Delete'), 'url':'delete', 'is_form':True}]
        elif self.position_status != 'pr_pos_canceled':
            if self.printed_at:
                actions.append({'name':_('Print again'), 'url':'print', 'is_form':False})
            else:
                actions.append({'name':_('Print'), 'url':'print', 'is_form':False})
        if (self.cn_tax_status in ['pr_cts_sender_pay_0tax_need_pay_rest', 'pr_cts_sender_pay_need_pay_rest']) or \
           self.payment_status == 'pr_pas_need_pay_rest':
            actions.append({'name':_('Pay rest'), 'url':'pay-rest', 'is_form':True})
        return actions
    
#     def save(self, *args, **kwargs):
#         if not self.yde_number:
#             self.yde_number = self.type.get_next_draft_yde_number()
#         super(Parcel, self).save(*args, **kwargs)
    
    def get_fee_eur(self):
        v_weight_kg = self.length_cm * self.width_cm * self.height_cm / self.volume_weight_rate
        weight_kg = (self.weight_kg > v_weight_kg) and self.weight_kg or v_weight_kg
        weight_kg = weight_kg < self.start_weight_kg and self.start_weight_kg or weight_kg
        fee = self.start_price_eur
        fee += ceil((weight_kg - self.start_weight_kg) / self.continuing_weight_kg) * self.continuing_price_eur
        return fee
    
    def get_real_fee_eur(self):
        real_v_weight_kg = self.real_length_cm * self.real_width_cm * self.real_height_cm / self.volume_weight_rate
        real_weight_kg = (self.real_weight_kg > real_v_weight_kg) and self.real_weight_kg or real_v_weight_kg
        real_weight_kg = real_weight_kg < self.start_weight_kg and self.start_weight_kg or real_weight_kg
        fee = self.start_price_eur
        fee += ceil((real_weight_kg - self.start_weight_kg) / self.continuing_weight_kg) * self.continuing_price_eur
        return fee
    
    def get_cn_customs_tax_cny(self):
        tax_cny = 0
        for parcel_detail in self.details.all():
            tax_cny += parcel_detail.get_cn_customs_tax_cny()
        return tax_cny
    
    def get_due_cn_customs_tax_cny(self):
        tax_cny = self.get_cn_customs_tax_cny() 
        if tax_cny > 50:return tax_cny
        else:return 0
    
    def get_value_cny(self):
        value_cny = 0
        for parcel_detail in self.details.all():
            value_cny += parcel_detail.get_value_cny()
        return value_cny
    
    def can_book_it(self):
        if self.is_delete:
            return (False, ugettext('Already deleted'))
        detail_set = self.details.all()
        if self.get_value_cny() > 1000:
            if detail_set.count() > 1:
                return (False, ugettext("More than one piece when > 1000 CNY."))
            elif detail_set[0].qty > 1:
                return (False, ugettext("More than one piece when > 1000 CNY."))
        for detail in detail_set:
            if detail.cn_customs_tax.is_forbidden:
                return (False, detail.description + " " + ugettext("is forbidden by chinese customs."))
        fee_due_to = self.get_fee_eur()
        if self.sender_pay_cn_customs:
            fee_due_to += self.get_due_cn_customs_tax_cny() / self.eur_to_cny_rate
        if self.user.userprofile.current_deposit + self.user.userprofile.credit < fee_due_to:
            return (False, ugettext("Short of deposit, please charge your deposit."))             
        return (True, "")  
    
    def book_it(self):
        self.yde_number = self.type.get_next_yde_number()
        fee_due_to = self.get_fee_eur()
        self.user.userprofile.pay_to_yunda(fee_due_to, "parcel_payment", self.yde_number)
        self.payment_status = "pr_pas_paid"
        if self.sender_pay_cn_customs:
            tax_due_to = self.get_due_cn_customs_tax_cny() / self.eur_to_cny_rate
            if tax_due_to > 0:
                self.user.userprofile.pay_to_yunda(tax_due_to, "customs_payment", self.yde_number)
                ParcelStatusHistory.objects.create(type="cn_tax_status",
                                           status="pr_cts_sender_paid",
                                           create_at=datetime.now(),
                                           parcel=self)            
                self.cn_tax_status = "pr_cts_sender_paid"
            else:
                self.cn_tax_status = "pr_cts_sender_pay_0tax"
        else:
            self.cn_tax_status = "pr_cts_receiver_pay"
                
        ParcelStatusHistory.objects.create(type="payment_status",
                                           status=self.payment_status,
                                           create_at=datetime.now(),
                                           parcel=self)
        self.save()
        
class CnCustomsTax(models.Model):
    cn_name = models.CharField(_('Chinese name'), max_length=50,)
    en_name = models.CharField(_('English name'), max_length=50, blank=True,)
    cn_custom_number = models.CharField(_('CN custom number'), max_length=10)
    hs_code = models.CharField(_('HS code'), max_length=10, blank=True)
    tax_rate = models.FloatField(_('Tax rate'))
    standard_unit_price_cny = models.FloatField(_('Standard unit price (CNY)'))
    charge_by_weight = models.BooleanField(_('Charge by weight'), default=False)
    forbidden_customs = models.CharField(_('Forbidden customs '), max_length=500, help_text=_('Use comma between different customs.'), blank=True)
    is_forbidden = models.NullBooleanField(default=False)
    is_active = models.BooleanField(default=True)
    categories = models.ManyToManyField('CnCustomsTaxCatalog', blank=True)
    # catalog = models.ManyToManyField('CnCustomsTaxCatalog')
    
    def get_tax_rate_to_display(self):
        if self.charge_by_weight:
            return "%.0f CNY/KG" % (self.tax_rate * self.standard_unit_price_cny)
        else:
            return "{:.0f}%".format(self.tax_rate * 100)
    
    def get_cn_tax_cny(self, value_eur, net_weight_kg, eur_to_cny_rate):
        return self.get_value_cny(value_eur, net_weight_kg, eur_to_cny_rate) * self.tax_rate
    
    def get_value_cny(self, value_eur, net_weight_kg, eur_to_cny_rate):
        if self.charge_by_weight:
            return self.standard_unit_price_cny * net_weight_kg
        else:
            value_cny = value_eur * eur_to_cny_rate
            if value_cny in [self.standard_unit_price_cny / 2, self.standard_unit_price_cny * 2]:
                return self.standard_unit_price_cny
            else:
                return value_cny
    def __unicode__(self):
        return self.cn_name

class ParcelDetail(models.Model):
    parcel = models.ForeignKey(Parcel, related_name='details')
    description = models.CharField(_('Description'), max_length=50, validators=[field_validator_only_alphabeta_num])
    cn_customs_tax = models.ForeignKey('CnCustomsTax', null=True,)
    qty = models.FloatField(_('Qty'), validators=[field_validators.MinValueValidator(0.01)])
    item_net_weight_kg = models.FloatField(_('Item net weight (KG)'), validators=[field_validators.MinValueValidator(0.01)])
    item_price_eur = models.FloatField(_('Item price (EUR)'), validators=[field_validators.MinValueValidator(0.01)])
    original_country = models.CharField(_('Original country'), max_length=2, default='DE')
    
    def __unicode__(self):
        return self.parcel.yde_number + " " + self.description
    
    def get_cn_customs_tax_cny(self):
        return self.cn_customs_tax.get_cn_tax_cny(self.item_price_eur, self.item_net_weight_kg, self.parcel.eur_to_cny_rate) * self.qty
    
    def get_value_cny(self):
        return self.cn_customs_tax.get_value_cny(self.item_price_eur, self.item_net_weight_kg, self.parcel.eur_to_cny_rate) * self.qty

class CnCustomsTaxCatalog(models.Model):
    cn_name = models.CharField(_('Chinese name'), max_length=50, unique=True)
    en_name = models.CharField(_('English name'), max_length=50, blank=True,)
    # cn_customs_taxs = models.ManyToManyField(CnCustomsTax, null=True)
    def __unicode__(self):
        return self.cn_name
    

class CnShenfengzheng(models.Model):
    number = models.CharField(_('Shenfengzheng number'), max_length=20)
    name = models.CharField(_('Chinese name'), max_length=20)
    mobile = models.CharField(_('Mobilephone'), max_length=15)
    image = models.BinaryField(_('Image'), help_text='Jpeg format.')
    
class SenderTemplate(models.Model):
    yid = models.CharField(_("YID"), max_length="40", blank=True)
    user = models.ForeignKey(User)
    yde_number = models.CharField(_('YDE number'), max_length=15, blank=True)
    sender_name = models.CharField(_('Sender name'), max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_name2 = models.CharField(_('Sender name2'), blank=True, max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_company = models.CharField(_('Sender company'), blank=True, max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_state = models.CharField(_('Sender state'), blank=True, max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_city = models.CharField(_('Sender city'), max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_postcode = models.CharField(_('Sender postcode'), max_length=5, validators=[field_validator_german_postcode])
    sender_street = models.CharField(_('Sender street'), max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_add = models.CharField(_('Sender street addition'), blank=True, max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_hause_number = models.CharField(_('Sender hause number'), max_length=10, validators=[field_validator_only_alphabeta_num])
    sender_tel = models.CharField(_('Sender telephone'), max_length=15)
    sender_email = models.EmailField(_('Sender email'), blank=True, validators=[field_validators.EmailValidator])
    sender_country = models.CharField(_('Sender country'), max_length=2, default="DE")
    
    class Meta:
        unique_together = ( 'user', 
                            'sender_name',
                            'sender_name2',
                            'sender_company',
                            'sender_state',
                            'sender_city',
                            'sender_postcode',
                            'sender_street',
                            'sender_add',
                            'sender_hause_number',
                            'sender_tel',
                            'sender_email',
                            )

    def setYid(self):
        self.yid = hashlib.md5("sendertemplate%d" % self.id).hexdigest()
        self.save()
        
    def __unicode__(self):
        return "Sender template" + (self.yde_number or "")
    
#     def save(self, *args, **kwargs):
#         if not self.yde_number:
#             #self.yde_number = get_seq_by_code(ADRDRESS_TEMPLATE_NUMBER_SEQ_CODE, True)
#             self.yde_number=hashlib.md5("sndt%d" % self.id).hexdigest()
#         super(SenderTemplate, self).save(*args, **kwargs)
    
class ReceiverTemplate(models.Model):
    yid = models.CharField(_("YID"), max_length="40", blank=True)
    user = models.ForeignKey(User)
    yde_number = models.CharField(_('YDE number'), max_length=15, blank=True)
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
    
    class Meta:
        unique_together = ( 'user', 
                            'receiver_name',
                            'receiver_company',
                            'receiver_province',
                            'receiver_city',
                            'receiver_district',
                            'receiver_postcode',
                            'receiver_address',
                            'receiver_address2',
                            'receiver_mobile',
                            'receiver_email',
                            )

    def setYid(self):
        self.yid = hashlib.md5("receivertemplate%d" % self.id).hexdigest()
        self.save()
        
    def __unicode__(self):
        return "Receiver template" + (self.yde_number or "")
    
#     def save(self, *args, **kwargs):
#         if not self.yde_number:
#             #self.yde_number = get_seq_by_code(ADRDRESS_TEMPLATE_NUMBER_SEQ_CODE, True)
#             self.yde_number=hashlib.md5("rcvt%d" % self.id).hexdigest()
#         super(ReceiverTemplate, self).save(*args, **kwargs)
    
class DhlRetoureLabel(models.Model):
    yid = models.CharField(_("YID"), max_length="40", blank=True)
    user = models.ForeignKey(User)
    sender_name = models.CharField(_('Sender name'), max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_name2 = models.CharField(_('Sender name2'), blank=True, max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_company = models.CharField(_('Sender company'), blank=True, max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_state = models.CharField(_('Sender state'), blank=True, max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_city = models.CharField(_('Sender city'), max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_postcode = models.CharField(_('Sender postcode'), max_length=5, validators=[field_validator_german_postcode])
    sender_street = models.CharField(_('Sender street'), max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_add = models.CharField(_('Sender street addition'), blank=True, max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_hause_number = models.CharField(_('Sender hause number'), max_length=10, validators=[field_validator_only_alphabeta_num])
    sender_tel = models.CharField(_('Sender telephone'), max_length=15)
    sender_email = models.EmailField(_('Sender email'), blank=True, validators=[field_validators.EmailValidator])
    retoure_yde_number = models.CharField(blank=True, max_length=12)
    tracking_number = models.CharField(_("Tracking number"), blank=True, max_length=12)
    is_deleted = models.NullBooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    pdf_file = models.BinaryField(blank=True)
    printed_at = models.DateTimeField(_('Printed at'), null=True)
    created_at = models.DateTimeField()
    payment_status = models.CharField(max_length=60, default='rl_pas_unpaid', choices=DHL_RETOURE_LABEL_STATUSES)
    position_status = models.CharField(max_length=60, default='rl_pos_sender', choices=DHL_RETOURE_LABEL_STATUSES)
    STATUSES = (
              ('draft', u'草稿'),
              ('confirmed', u'已提交'),
              ('finished', u'已使用'),
              )
    status = models.CharField(max_length=20, default='draft', choices=STATUSES)
    yd_pdf_file = models.BinaryField(blank=True)
    currency_type = models.CharField(max_length=3, default='cny')
    price = models.FloatField(default=3.9)
    routing_code=models.CharField(blank=True,max_length=20)
    def __unicode__(self):
        return self.retoure_yde_number or ''
    def get_customer_number(self):
        return self.user.userprofile.customer_number or ''
    def is_print(self):
        if self.printed_at:
            return True
        else:
            return False
    def save(self, *args, **kwargs):
        if not self.retoure_yde_number:
            self.retoure_yde_number = get_seq_by_code(DHL_RETOURE_NUMBER_SEQ_CODE, True)          
        super(DhlRetoureLabel, self).save(*args, **kwargs) 
    def get_routing_code(self):
        return self.routing_code.replace('.','').replace(' ','')     
    
    def can_book_it(self):
        if self.is_deleted:
            return (False, ugettext('Already deleted'))
        if self.payment_status == "rl_pas_paid":
            return (False, ugettext('Already paid'))
        if self.user.userprofile.current_deposit + self.user.userprofile.credit < get_settings().dhl_retoure_price_eur:
            return (False, _("Short of deposit, please charge your deposit."))             
        return (True, "") 
        
    def book_it(self):
        
        name = (self.sender_name or "") + u" " + (self.sender_name2 or "") + u" " + (self.sender_company or "")
        if len(name) < 51:
            firstname = name
            lastname = ""
        else:
            firstname = name[0:50]
            lastname = name[50:100]
        
        attributes, pdf = Dhl_Retoure.getLabel(firstname, lastname, self.sender_street, self.sender_hause_number, \
                                              self.sender_postcode, self.sender_city, self.retoure_yde_number)
        if not attributes:
            # TODO Wenn error
            return False
        else:
            self.pdf_file = pdf
            self.tracking_number = attributes['idc']
            self.payment_status = 'rl_pas_paid'
            
            self.user.userprofile.pay_to_yunda(get_settings().dhl_retoure_price_eur,
                                                       "retoure_label_payment",
                                                       self.retoure_yde_number)
            DhlRetoureLabelStatusHistory.objects.create(type="payment_status",
                                           status=self.payment_status,
                                           create_at=datetime.now(),
                                           dhl_retoure_label=self)
            self.save()
    def get_current_usable_actions(self):
        actions = []
        if self.payment_status == 'rl_pas_unpaid':
            # 新建的parcel
            actions += [  # {'name':_('Edit'), 'url':'edit','is_form':False}, 
                        {'name':_('Pay'), 'url':'pay', 'is_form':True}, {'name':_('Delete'), 'url':'delete', 'is_form':True}]
        elif self.position_status != 'rl_pos_canceled':
            if self.printed_at:
                actions.append({'name':_('Print again'), 'url':'print', 'is_form':False})
            else:
                actions.append({'name':_('Print'), 'url':'print', 'is_form':False})
        return actions

class RetoureHistory(models.Model):
    retoure = models.ForeignKey(DhlRetoureLabel, null=True, related_name='histories')
    created_at = models.DateTimeField(u'记录时间', null=True,default=datetime.now)
    description = models.TextField(u'记录内容',)
    visible_to_customer=models.BooleanField(default=True)
    staff=models.ForeignKey(User,null=True)

###################################################################
# for  version update
class SenderTemplateTmp(models.Model):
    yid = models.CharField(_("YID"), max_length="40", blank=True)
    user = models.ForeignKey(User)
    yde_number = models.CharField(_('YDE number'), max_length=15, blank=True)
    sender_name = models.CharField(_('Sender name'), max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_name2 = models.CharField(_('Sender name2'), blank=True, max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_company = models.CharField(_('Sender company'), blank=True, max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_state = models.CharField(_('Sender state'), blank=True, max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_city = models.CharField(_('Sender city'), max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_postcode = models.CharField(_('Sender postcode'), max_length=5, validators=[field_validator_german_postcode])
    sender_street = models.CharField(_('Sender street'), max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_add = models.CharField(_('Sender street addition'), blank=True, max_length=25, validators=[field_validator_only_alphabeta_num])
    sender_hause_number = models.CharField(_('Sender hause number'), max_length=10, validators=[field_validator_only_alphabeta_num])
    sender_tel = models.CharField(_('Sender telephone'), max_length=15)
    sender_email = models.EmailField(_('Sender email'), blank=True, validators=[field_validators.EmailValidator])
    sender_country = models.CharField(_('Sender country'), max_length=2, default="DE")
    
    class Meta:
        unique_together = ( 'user', 
                            'sender_name',
                            'sender_name2',
                            'sender_company',
                            'sender_state',
                            'sender_city',
                            'sender_postcode',
                            'sender_street',
                            'sender_add',
                            'sender_hause_number',
                            'sender_tel',
                            'sender_email',
                            )
    
    def setYid(self):
        self.yid = hashlib.md5("sendertemplate%d" % self.id).hexdigest()
        self.save()
        
    def __unicode__(self):
        return "Sender template" + (self.yde_number or "")
    
#     def save(self, *args, **kwargs):
#         if not self.yde_number:
#             #self.yde_number = get_seq_by_code(ADRDRESS_TEMPLATE_NUMBER_SEQ_CODE, True)
#             self.yde_number=hashlib.md5("sndt%d" % self.id).hexdigest()
#         super(SenderTemplate, self).save(*args, **kwargs)
    
class ReceiverTemplateTmp(models.Model):
    yid = models.CharField(_("YID"), max_length="40", blank=True)
    user = models.ForeignKey(User)
    yde_number = models.CharField(_('YDE number'), max_length=15, blank=True)
    receiver_name = models.CharField(_('Receiver name'), max_length=50, validators=[field_validator_only_chinese])
    receiver_company = models.CharField(_('Receiver company'),blank=True, default="",  max_length=50, validators=[field_validator_chinese_and_alphabeta])
    receiver_province = models.CharField(_('Receiver province'), max_length=20, validators=[field_validator_only_chinese])
    receiver_city = models.CharField(_('Receiver city'), blank=True,default="", max_length=20, validators=[field_validator_only_chinese])
    receiver_district = models.CharField(_('Receiver district'), blank=True,default="", max_length=20, validators=[field_validator_only_chinese])
    receiver_postcode = models.CharField(_('Receiver postcode'), default="", max_length=6, validators=[field_validator_chinese_postcode])
    receiver_address = models.CharField(_('Receiver address'), max_length=50, validators=[field_validator_chinese_and_alphabeta])
    receiver_address2 = models.CharField(_('Receiver address2'), blank=True,default="", max_length=50, validators=[field_validator_chinese_and_alphabeta])
    receiver_mobile = models.CharField(_('Receiver mobilephone'), max_length=11, validators=[field_validator_chinese_mobile_phone])
    receiver_email = models.EmailField(_('Receiver email'), default="", blank=True,validators=[field_validators.EmailValidator])
    receiver_country = models.CharField(_('Receiver country'), max_length=2, default="CN")
    
    class Meta:
        unique_together = ( 'user', 
                            'receiver_name',
                            'receiver_company',
                            'receiver_province',
                            'receiver_city',
                            'receiver_district',
                            'receiver_postcode',
                            'receiver_address',
                            'receiver_address2',
                            'receiver_mobile',
                            'receiver_email',
                            )
    
    def setYid(self):
        self.yid = hashlib.md5("receivertemplate%d" % self.id).hexdigest()
        self.save()
        
    def __unicode__(self):
        return "Receiver template" + (self.yde_number or "")
    
#     def save(self, *args, **kwargs):
#         if not self.yde_number:
#             #self.yde_number = get_seq_by_code(ADRDRESS_TEMPLATE_NUMBER_SEQ_CODE, True)
#             self.yde_number=hashlib.md5("rcvt%d" % self.id).hexdigest()
#         super(ReceiverTemplate, self).save(*args, **kwargs)

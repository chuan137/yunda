# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _
from userena.compat import sha_constructor
import random
from datetime import datetime
# from yunda_parcel.models import (ParcelType, ParcelPrice)

# Create your models here.
class Branch(models.Model):
    name = models.CharField(_('Branch name'), max_length=50, unique=True)
    code = models.CharField(_('Code'), max_length=8, unique=True)
    branch_number = models.CharField(_('Branch number'), max_length=6, blank=True)
    company = models.CharField(_('Company'), max_length=50, blank=True)
    street = models.CharField(_('Street'), max_length=50)
    hause_number = models.CharField(_('Hause number'), max_length=10, blank=True)
    street_add = models.CharField(_('Addtion'), max_length=50, blank=True)
    postcode = models.CharField(_('Postcode'), max_length=10)
    city = models.CharField(_('City'), max_length=20)
    state = models.CharField(_('State'), max_length=20, blank=True)
    COUNTRIES = (
                ('DE', _('Germany')),
                ('CN', _('China')),
                ('HK', _('Hongkong')),
                ('TW', _('Taiwan')),
                ('MO', _('Macau')),
                )
    country_code = models.CharField(_('Country'), max_length=2, choices=COUNTRIES)
    tel = models.CharField(_('Telphone'), max_length=20)
    fax = models.CharField(_('Fax'), max_length=20, blank=True)
    vat_id = models.CharField(_('Vat ID'), max_length=20, blank=True)
    register_number = models.CharField(_('Register number'), max_length=30, blank=True)
    is_active = models.BooleanField(_('Is Active'), default=False)
    is_default = models.BooleanField(default=False)
    super_user = models.ForeignKey(User, related_name="Branch.super_user")
    
    def __unicode__(self):
        return "%s (%s-%s)" % (self.name, self.code, self.branch_number)
    
    def save(self, *args, **kwargs):
        if not self.branch_number:
            self.branch_number = "000"
        if not self.code:
            self.code = sha_constructor(str(random.random()).encode('utf-8')).hexdigest()[:8]
        super(Branch, self).save(*args, **kwargs)

   
class StaffProfile(models.Model):
    user = models.OneToOneField(User)
    staff_number = models.CharField(_('Staff number'), max_length=10, blank=True)
    branch = models.ForeignKey('Branch', limit_choices_to={'is_active':True}, null=True)
    def __unicode__(self):
        return self.user.__unicode__() + " " + self.staff_number
    def save(self, *args, **kwargs):
        if not self.staff_number:
            self.staff_number = "000"        
        super(StaffProfile, self).save(*args, **kwargs)

class DepositTransfer(models.Model):
    user = models.ForeignKey(User)
    created_at = models.DateTimeField(_('Created at'))
    amount = models.FloatField(_('Amount'))
    TRANSFER_TYPES = (
                ('deposit_entry', _('deposit entry')),
                ('deposit_withdraw', _('deposit withdraw')),
                ('parcel_payment', _('Parcel payment')),
                ('parcel_canceled', _('Parcel canceled')),
                ('customs_payment', _('Customs payment')),
                ('customs_pay_back', _('Customs pay_back')),
                ('retoure_label_payment', _('Retoure label payment')),
                ('others', _('Others')),
                )
    type = models.CharField(_('Type'), max_length=30, choices=TRANSFER_TYPES)
    operator = models.ForeignKey(User, limit_choices_to={'is_staff': True}, related_name="FundTransfer.operator", null=True)
    ref = models.CharField(_('Reference'), max_length=50, blank=True)
    
    def __unicode__(self):
        return self.user.userprofile.customer_number + ' - ' + self.ref
    
    def customer_number(self):
        return self.user.userprofile.customer_number
    customer_number.short_description = 'Customer number'

class InvoiceHistory(models.Model):
    user = models.ForeignKey(User)
    created_at = models.DateTimeField(_('Created at'))
    amount = models.FloatField(_('Amount'))
    TYPES = (
                ('parcel', _('Parcel')),
                ('retoure_labbel', _('Retoure label')),
                ('cn_tax', _('CN tax')),
                ('others', _('Others')),
                )
    type = models.CharField(_('Type'), max_length=30, choices=TYPES)
    yde_number = models.CharField(max_length=30, blank=True)
    tracking_number = models.CharField(max_length=30, blank=True)
    is_refound = models.BooleanField(default=False)
    is_invoiced = models.BooleanField(default=False)
    invoice_number = models.CharField(max_length=30, blank=True)

class DepositTransferNew(models.Model):
    user = models.ForeignKey(User)
    created_at = models.DateTimeField(u'时间',default=datetime.now)
    amount = models.FloatField(u'金额')
    origin = models.CharField(blank=True, max_length=40)
    ref = models.TextField("Description", blank=True)
    
    def __unicode__(self):
        return self.user.userprofile.customer_number + ' - ' + self.ref
    
    def customer_number(self):
        return self.user.userprofile.customer_number
    customer_number.short_description = u'客户编号'

class Invoice(models.Model):
    user = models.ForeignKey(User)
    created_at = models.DateTimeField(u'时间')
    number = models.CharField(max_length=20)
    amount = models.FloatField(u'金额')
    pdf_file = models.BinaryField()
    
    def __unicode__(self):
        return "%s%s" % (self.user.userprofile.customer_number , self.created_at.strftime("%Y-%m-%d"))
    

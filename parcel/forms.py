# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from parcel import models
from django.core import validators

import re

class IntlParcelForm(forms.ModelForm):

    type_code = forms.CharField()
    save_sender = forms.CharField(required=False)
    save_receiver = forms.CharField(required=False)
        
    class Meta:
        model = models.IntlParcel
        # exclude = ('created_at','user','salesman','branch')
        fields = [
                  # #sender
                  'sender_name', 'sender_name2', 'sender_company', 'sender_city',
                  'sender_postcode', 'sender_street', 'sender_add', 'sender_hause_number',
                  'sender_tel', 'sender_email',
                  # #receiver
                  'receiver_name', 'receiver_company', 'receiver_province', 'receiver_city',
                  'receiver_district', 'receiver_postcode', 'receiver_address', 'receiver_address2',
                  'receiver_mobile', 'receiver_email',
                  
                  # #others
                  'ref', 'weight_kg', 'length_cm', 'width_cm', 'height_cm',
                  'cn_customs_paid_by'
                  ]

       
     
class ParcelDetailForm(forms.ModelForm):
    
    class Meta:
        model = models.GoodsDetail
        fields = ['description', 'cn_customs_tax_catalog_name', 'cn_customs_tax_name', 'qty',
                'item_net_weight_kg', 'item_price_eur']

class DhlRetoureLabelForm(forms.ModelForm):    
    class Meta:
        # model = models.DhlRetoureLabel
        fields = [  # #sender
                  'sender_name', 'sender_name2', 'sender_company', 'sender_city',
                  'sender_postcode', 'sender_street', 'sender_add', 'sender_hause_number',
                  'sender_tel'
                  ]

regex_de_fr = r"^[\sa-zA-ZàâäôéèëêïîçùûüÿæœÀÂÄÔÉÈËÊÏÎŸÇÙÛÜÆŒäöüßÄÖÜẞñÑ\.\,\-\/\#]+$"
regex_de_fr_num = r"^[\s0-9a-zA-ZàâäôéèëêïîçùûüÿæœÀÂÄÔÉÈËÊÏÎŸÇÙÛÜÆŒäöüßÄÖÜẞñÑ\.\,\-\/\#]+$"
class InvoiceAddressForm(forms.Form):
    customer_number = forms.CharField(required=True, max_length=10, validators=[
            validators.RegexValidator(r"^[0-9a-zA-Z]+$", _('Enter a valid customer number.'), 'invalid')
        ])
    
    first_name = forms.CharField(required=True, max_length=30, validators=[
            validators.RegexValidator(regex_de_fr, u'仅能输入英文、德文以及.,-/#符号。', 'invalid')
        ])
    last_name = forms.CharField(required=True, max_length=30, validators=[
            validators.RegexValidator(regex_de_fr, u'仅能输入英文、德文以及.,-/#符号。', 'invalid')
        ])
    
    company = forms.CharField(required=False, max_length=50, validators=[
            validators.RegexValidator(regex_de_fr_num, u'仅能输入英文、德文、数字以及.,-/#符号。', 'invalid')
        ])
    street = forms.CharField(required=True, max_length=50, validators=[
            validators.RegexValidator(regex_de_fr_num, u'仅能输入英文、德文、数字以及.,-/#符号。', 'invalid')
        ])
    hause_number = forms.CharField(required=True, max_length=10, validators=[
            validators.RegexValidator(regex_de_fr_num, u'仅能输入英文、德文、数字以及.,-/#符号。', 'invalid')
        ])
    street_add = forms.CharField(required=False, max_length=50, validators=[
            validators.RegexValidator(regex_de_fr_num, u'仅能输入英文、德文、数字以及.,-/#符号。', 'invalid')
        ])
    city = forms.CharField(required=True, max_length=20, validators=[
            validators.RegexValidator(regex_de_fr_num, u'仅能输入英文、德文、数字以及.,-/#符号。', 'invalid')
        ])
    state = forms.CharField(required=False, max_length=20, validators=[
            validators.RegexValidator(regex_de_fr_num, u'仅能输入英文、德文、数字以及.,-/#符号。', 'invalid')
        ])
    postcode = forms.CharField(required=True, max_length=10, validators=[
            validators.RegexValidator(r"^[0-9]+$", u'邮编格式不正确。', 'invalid')
        ])
    tel = forms.CharField(required=True, max_length=20, validators=[
            validators.RegexValidator(r"^[0-9]+$", u'电话号码格式不正确', 'invalid')
        ])
    vat_id = forms.CharField(required=False, max_length=20, validators=[
            validators.RegexValidator(r"^[0-9a-zA-Z\-]+$", u"仅能输入数字和字母。", 'invalid')
        ])    
    COUNTRIES = (
                ('DE', _('Germany')),
                ('CN', _('China')),
                ('HK', _('Hongkong')),
                ('TW', _('Taiwan')),
                ('MO', _('Macau')),
                )
    country_code = forms.ChoiceField(choices=COUNTRIES, required=True)
    
class MawbForm(forms.ModelForm):
    class Meta:
        model = models.Mawb
        fields = ['mawb_number', 'cn_customs', 'need_receiver_name_mobiles',
                'need_total_value_per_sender', ]
    
class BatchForm(forms.ModelForm):
    class Meta:
        model = models.Batch
        fields = ['order_number', 'sign', 'color', 'max_value']

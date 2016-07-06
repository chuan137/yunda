# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from yunda_parcel import models
from yunda_parcel.models import CnCustomsTax, ParcelType
import re


class ParcelForm(forms.ModelForm):
    # save_sender_template = forms.BooleanField(label=_('Save as Template'))
    # save_receiver_template = forms.BooleanField(label=_('Save as Template'))
#     TYPES = []
# #     parcel_type=forms.ChoiceField(label=_('Type'), choices=TYPES)
    CN_CUSTOMS_PAY_BYS = (('sender', _('Sender')),
                        ('receiver', _('Receiver')),
                        )
    cn_customs_pay_by = forms.ChoiceField(label=_('Cn customs tax pay by'), choices=CN_CUSTOMS_PAY_BYS, widget=forms.RadioSelect)
    # cn_customs_pay_by.empty_label = None
    # cn_customs_pay_by.widget=forms.RadioSelect
    def __init__(self, *args, **kwargs):
        super(ParcelForm, self).__init__(*args, **kwargs) 
        self.fields['type'].empty_label = None
        self.fields['type'].label = _('Parcel type')
        
    class Meta:
        model = models.Parcel
        # exclude = ('created_at','user','salesman','branch')
        fields = ['type',  # 'sender_pay_cn_customs',
                  # #sender
                  'sender_name', 'sender_name2', 'sender_company', 'sender_city',
                  'sender_postcode', 'sender_street', 'sender_add', 'sender_hause_number',
                  'sender_tel', 'sender_email',
                  # #receiver
                  'receiver_name', 'receiver_company', 'receiver_province', 'receiver_city',
                  'receiver_district', 'receiver_postcode', 'receiver_address', 'receiver_address2',
                  'receiver_mobile', 'receiver_email',
                  
                  # #others
                  'ref', 'weight_kg', 'length_cm', 'width_cm',
                  'height_cm',
                  ]
        widgets = {
                 'type':forms.RadioSelect(),
                 }
       
     
class ParcelDetailForm(forms.ModelForm):
#     TAX_CN_CATALOGS = ((u'--', "0"),(u'--', "0"))
#     TAX_CN_NAMES = ((u'--', "0"),(u'--', "0"))
    cn_customs_tax_catalog = forms.IntegerField(required=True)
    cn_customs_tax = forms.IntegerField(required=True)
    
#     def clean_description(self):
#         value = self.cleaned_data['description']
#         p = re.compile(u'^[a-zA-Z0-9\s\-,.()äÄöÖüÜ]+$')
#         if not p.match(value):
#             raise forms.ValidationError(_('Only german/english alphabeta, numbers, and ",.-()" allowed'))
#          
#         return value
    
    class Meta:
        model = models.ParcelDetail
        exclude = ('parcel', 'cn_customs_tax')

class ParcelBookItForm(forms.Form):
    yde_number = forms.CharField()

class DhlRetoureLabelForm(forms.ModelForm):
    save_sender = forms.CharField(required=False)
    class Meta:
        model = models.DhlRetoureLabel
        fields = [  # #sender
                  'sender_name', 'sender_name2', 'sender_company', 'sender_city',
                  'sender_postcode', 'sender_street', 'sender_add', 'sender_hause_number',
                  'sender_tel','sender_email',
                  ]
class DhlRetoureLabelBookItForm(forms.Form):
    retoure_yde_number = forms.CharField()
    
class CnCustomsTaxUploadForm(forms.Form):
    file = forms.FileField(label="Choose excel to upload")
    
class SenderTemplateForm(forms.ModelForm):    
    class Meta:
        model = models.SenderTemplate
        fields=[  # #sender
                  'sender_name', 'sender_name2', 'sender_company', 'sender_city',
                  'sender_postcode', 'sender_street', 'sender_add', 'sender_hause_number',
                  'sender_tel','sender_email',
                  ]


class ReceiverTemplateForm(forms.ModelForm):    
    class Meta:
        model = models.ReceiverTemplate
        fields=[  # #sender
                  'receiver_name', 'receiver_company', 'receiver_province', 'receiver_city',
                  'receiver_district', 'receiver_postcode', 'receiver_address', 'receiver_address2',
                  'receiver_mobile','receiver_email',
                  ]
        
        

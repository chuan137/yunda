# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from cn_shenfenzheng import models

class CnShenfenzhengForm(forms.ModelForm):
    
    #shenfenzheng = forms.TextInput()
    class Meta:
        model = models.CnShenfengzheng
        fields = [
                  'number', 'name', 'mobile',#'shenfenzheng1'      
                  ]
#     def is_valid(self):
#         pass
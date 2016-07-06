# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from messenge import models
import re

class SubjectForm(forms.ModelForm):
    class Meta:
        model = models.Subject
        # exclude = ('created_at','user','salesman','branch')
        fields = [
                  'title',
                  #'warehause_code',                  
                  ]

class AdminSubjectForm(forms.ModelForm):
    customer_number=forms.CharField(max_length=20,required=True)
    class Meta:
        model = models.Subject
        # exclude = ('created_at','user','salesman','branch')
        fields = [
                  'title',
                  #'warehause_code',                  
                  ]
       
     
class MessengeForm(forms.ModelForm):
    content=forms.CharField(max_length=200)
    class Meta:
        model = models.Messenge
        fields = [
                  'content'                
                  ]
        widgets = {
          'content': forms.Textarea(attrs={'rows':3, 'cols':15}),
        }


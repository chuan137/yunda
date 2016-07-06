# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from yadmin.models import DespositEntry
import re


class DespositEntryForm(forms.ModelForm):    
    class Meta:
        model = DespositEntry
        fields = ['customer_number', 'amount', 'origin','ref']
        
        

# -*- coding: utf-8 -*-
from django import forms
from alipay.models import AlipayDepositOrder


class AlipayDepositOrder(forms.ModelForm):
    
    class Meta:
        model=AlipayDepositOrder
        fields=['amount']



# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from yunda_commen.commen_utils import get_seq_by_code


# Create your models here.

class AlipayDepositOrder(models.Model):
    yid = models.CharField(blank=True, max_length=10)
    user = models.ForeignKey(User)
    amount = models.FloatField()
    currency_type = models.CharField(default='eur', max_length=3)    
    created_at = models.DateTimeField(default=datetime.now)
    success_at = models.DateTimeField(null=True)
    alipay_no = models.CharField(blank=True, max_length=50)
    
    status = models.CharField(default='DRAFT', max_length=20)# payment website status

    
    def save(self,*args, **kwargs):
        if not self.yid:
            self.yid=get_seq_by_code('deposit_order',True)
        super(AlipayDepositOrder, self).save(*args, **kwargs)
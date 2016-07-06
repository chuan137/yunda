# -*- coding: utf-8 -*-
from django.db import models
from datetime import datetime
from django.utils.translation import ugettext_lazy as _

# Create your models here.
class Sequence(models.Model):
    code = models.CharField(max_length=30, unique=True)
    next_value = models.BigIntegerField(default=1)
    interval = models.PositiveSmallIntegerField(default=1)
    last_datetime = models.DateTimeField(default=datetime.now)
    RENEW_TYPES = (
                ('N', _('None')),
                ('Y', _('By year')),
                ('M', _('By Month')),
                ('D', _('By Day')),
                )
    renew_type = models.CharField(max_length=1, choices=RENEW_TYPES)
    prefix = models.CharField(max_length=50, help_text=_("Year-%y/%Y, Month-%m, Day-%d"), blank=True)
    suffix = models.CharField(max_length=50, help_text=_("Year-%y/%Y, Month-%m, Day-%d"), blank=True)
    digit_length = models.SmallIntegerField(default=0)
    
    def __unicode__(self):
        return self.code
    
class Settings(models.Model):
    code = models.CharField(default="default", max_length=10, unique=True)
    eur_to_cny_rate = models.FloatField(default=7.2)
    currency_change_margin = models.FloatField(default=0.05)
    dhl_retoure_price_eur = models.FloatField(default=3.9)
    dhl_retoure_price_cny = models.FloatField(default=29)
    deposit_short_fee_eur = models.FloatField(default=3)
    cn_tax_to_eur_rate=models.FloatField(default=6.8)
    
    def __unicode__(self):
        return "Setting " + self.code
        



    
        
        
    
    

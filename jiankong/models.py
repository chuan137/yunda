# -*- coding: utf-8 -*-
from django.db import models
from jsonfield.fields import JSONField
from pychart.color import blanchedalmond
from parcel.models import Mawb, ParcelType
from datetime import datetime



# Create your models here.
class IntlParcelJiankong(models.Model): 
    yid = models.CharField("Parcel yid", max_length=40, blank=False, unique=True)
    customer_number = models.CharField(max_length=10, blank=False) 
    tracking_number = models.CharField(max_length=20, blank=False)
    type_code = models.CharField(max_length=40, blank=True)
    mawb = models.ForeignKey(Mawb, blank=True, null=True)
    finished_jiankong = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(blank=True, null=True)
    opc_arrived_at = models.DateTimeField("OPC arrived at", blank=True, null=True)
    opc_export_ready_at = models.DateTimeField("OPC export ready at", blank=True, null=True)
    opc_export_customs_finished_at = models.DateTimeField("OPC export customs cleared at", blank=True, null=True)
    opc_flied_at = models.DateTimeField("OPC flied to destination country at", blank=True, null=True)
    destination_country_arrived_at = models.DateTimeField(blank=True, null=True)
    import_customs_finished_at = models.DateTimeField(blank=True, null=True)
    local_opc_received_at = models.DateTimeField(blank=True, null=True)
    delivery_staff_asigned_at = models.DateTimeField(blank=True, null=True)
    deliveried_at = models.DateTimeField(blank=True, null=True)
    
    status = models.CharField(blank=True, max_length=40)
    newest_datetime = models.DateTimeField(blank=True, null=True)
    last_checked_at = models.DateTimeField(default=datetime.strptime("1998-08-08 08:08:08", '%Y-%m-%d %H:%M:%S'))
    
    messages = JSONField(blank=True, null=True)  # [{datetime:"2015-12-03 12:30:30",staff:"aaa",text:u"asfdaf afd"}]
    days_delayed = models.IntegerField(null=True, blank=True)
    
    
    
    
    


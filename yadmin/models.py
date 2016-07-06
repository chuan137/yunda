from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

# Create your models here.

class DespositEntry(models.Model):
    yid = models.CharField(max_length=40, blank=True)
    customer_number = models.CharField(max_length=10)
    amount = models.FloatField()    
    origin = models.CharField(max_length=40, blank=True)
    ref = models.CharField("Description", max_length=50, blank=True)
    
    created_at = models.DateTimeField(default=datetime.now)
    created_by = models.ForeignKey(User, null=True, related_name="despositentry.created_by")
    
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, null=True, blank=True,related_name="despositentry.approved_by")
    

class DespositWithdraw(models.Model):
    yid = models.CharField(max_length=40, blank=True)
    customer_number = models.CharField(max_length=10)
    amount = models.FloatField()    
    origin = models.CharField(max_length=40, blank=True)
    ref = models.CharField("Description", max_length=50, blank=True)
    
    created_at = models.DateTimeField(default=datetime.now)
    created_by = models.ForeignKey(User, null=True, related_name="despositwithdraw.created_by")
    
    approved_at = models.DateTimeField(null=True)
    approved_by = models.ForeignKey(User, null=True, related_name="despositwithdraw.approved_by")
    

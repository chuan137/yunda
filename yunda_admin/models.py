from django.db import models
from django.contrib.auth.models import User

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from yunda_commen.commen_utils import get_seq_by_code
from datetime import datetime
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class DepositEntry(models.Model):
    customer_number = models.CharField(max_length=20)
    CURRENCY_TYPES = (
                ('eur', _('EUR')),
                ('cny', _('CNY')),
                )
    deposit_currency_type = models.CharField(_('Deposit currency type'), max_length=3, choices=CURRENCY_TYPES, help_text="Will be change to EUR")
    amount = models.FloatField()
    internal_id = models.CharField(max_length=20)
    transfer_prove_image = models.BinaryField(null=True)
    transfer_prove_image_file_type = models.CharField(null=True, max_length=5)
    created_by = models.ForeignKey(User, limit_choices_to={'is_staff': True}, related_name="DepositEntry.created_by",)
    created_at = models.DateTimeField(default=datetime.now)
    verified_by = models.ForeignKey(User, limit_choices_to={'is_staff': True}, related_name="DepositEntry.verified_by", null=True)
    verified_at = models.DateTimeField(null=True)
    
    bank_arrived_at = models.DateTimeField(null=True)
    bank_arrived_set_by = models.ForeignKey(User, limit_choices_to={'is_staff': True}, related_name="DepositEntry.bank_arrived_set_by", null=True)
    bank_arrived_verified_at = models.DateTimeField(null=True)
    bank_arrived_verified_by = models.ForeignKey(User, limit_choices_to={'is_staff': True}, related_name="DepositEntry.bank_arrived_verified_by", null=True)
 
    def __unicode__(self):
        return self.internal_id + ' - ' + self.customer_number
        
    def is_verified(self):
        if self.verified_by and self.verified_at:
            return True
        else:
            return False
    is_verified.admin_order_field="verified_at"
    is_verified.boolean=True
    is_verified.short_description="Verified?"

class DepositWithdraw(models.Model):
    customer_number = models.CharField(max_length=20)
    CURRENCY_TYPES = (
                ('eur', _('EUR')),
                )
    deposit_currency_type = models.CharField(_('Deposit currency type'), max_length=3, choices=CURRENCY_TYPES, help_text="Will be change to EUR")
    amount = models.FloatField()
    internal_id = models.CharField(max_length=20)
      
    created_by = models.ForeignKey(User, limit_choices_to={'is_staff': True}, related_name="DepositWithdraw.created_by",)
    created_at = models.DateTimeField(default=datetime.now)
    verified_by = models.ForeignKey(User, limit_choices_to={'is_staff': True}, related_name="DepositWithdraw.verified_by", null=True)
    verified_at = models.DateTimeField(null=True)
    
    def __unicode__(self):
        return self.internal_id + ' - ' + self.customer_number
        
    def is_verified(self):
        if self.verified_by and self.verified_at:
            return True
        else:
            return False
    is_verified.admin_order_field="verified_at"
    is_verified.boolean=True
    is_verified.short_description="Verified?"
    


from django.contrib import admin
from yunda_admin import models
from yunda_commen import commen_utils
from datetime import datetime
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from userena.models import UserProfile

# Register your models here.
@admin.register(models.DepositEntry)
class DepositEntryAdmin(admin.ModelAdmin):
    fields = ('customer_number', 'deposit_currency_type', 'amount')
    actions = ['transfer_verify']
    list_display = ('internal_id', 'customer_number', 'deposit_currency_type', 'amount', 'created_by', 'created_at', 'is_verified', 'verified_by', 'verified_at')
    list_filter = ('customer_number', 'created_at', 'verified_at')
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by_id = request.user.id
        if not obj.internal_id:
            obj.internal_id = commen_utils.get_seq_by_code('deposit_entry_id', with_check_digit=True)
        admin.ModelAdmin.save_model(self, request, obj, form, change)
    
    def transfer_verify(self, request, queryset):
        entry = queryset.first()
        if not entry.verified_at:        
            customer_profile = get_object_or_404(UserProfile, customer_number=entry.customer_number)
            
            if entry.deposit_currency_type == 'cny':
                setting = commen_utils.get_settings()
                amount = entry.amount / setting.eur_to_cny_rate * (1 - setting.currency_change_margin)
            else:
                amount = entry.amount            
            customer_profile.pay_to_customer(amount, 'deposit_entry', entry.internal_id, request.user)
            queryset.update(verified_by=request.user, verified_at=datetime.now())
            
    transfer_verify.short_description = "Verify"

@admin.register(models.DepositWithdraw)
class DepositWithdrawAdmin(admin.ModelAdmin):
    fields = ('customer_number', 'deposit_currency_type', 'amount')
    actions = ['transfer_verify']
    list_display = ('internal_id', 'customer_number', 'deposit_currency_type', 'amount', 'created_by', 'created_at', 'is_verified', 'verified_by', 'verified_at')
    list_filter = ('customer_number', 'created_at', 'verified_at')
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by_id = request.user.id
        if not obj.internal_id:
            obj.internal_id = commen_utils.get_seq_by_code('deposit_entry_id', with_check_digit=True)
        admin.ModelAdmin.save_model(self, request, obj, form, change)
    
    def transfer_verify(self, request, queryset):
        entry = queryset.first()
        if not entry.verified_at:
            queryset.update(verified_by=request.user, verified_at=datetime.now())
            customer_profile = get_object_or_404(UserProfile, customer_number=entry.customer_number)
            
            amount = entry.amount            
            customer_profile.pay_to_yunda(amount, 'deposit_withdraw', entry.internal_id, request.user)
         
    transfer_verify.short_description = "Verify"

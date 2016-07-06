from django.contrib import admin
from yunda_user import models as yunda_user_models
from userena.models import UserProfile
from import_export.admin import ImportExportMixin
from import_export import resources
from django.contrib.auth.models import User
# Register your models here.

class BranchAdmin(admin.ModelAdmin):
    exclude = ('code', 'branch_number')

class StaffProfileAdmin(admin.ModelAdmin):
    pass

class DepositTransferAdmin(admin.ModelAdmin):
    list_display = ('customer_number', 'type', 'operator', 'amount', 'ref', 'created_at')

class InvoiceHistoryAdmin(admin.ModelAdmin):
    pass

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'created_at', 'amount')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('customer_number', 'get_user_full_name', 'get_user_email','deposit_currency_type', 'current_deposit', 'credit', 'level')
    def get_user_full_name(self, obj):
        return obj.user.get_full_name()
    get_user_full_name.short_description = 'Name'
    get_user_full_name.admin_order_field = 'user'
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'
    get_user_email.admin_order_field = 'user__email'
    search_fields = ('customer_number',)
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(UserProfileAdmin, self).get_search_results(request, queryset, search_term)
        queryset |= self.model.objects.filter(user__email__icontains=search_term)
        return queryset, use_distinct

class DepositTransferNewAdmin(admin.ModelAdmin):
    list_display = ('get_customer_number', 'amount', 'origin', 'ref', 'created_at')
    def get_customer_number(self,obj):
        return obj.user.userprofile.customer_number
    get_customer_number.short_description = 'Customer number'
    get_customer_number.admin_order_field = 'user__userprofile__customer_number'
    
    search_fields = ('origin','ref')
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(DepositTransferNewAdmin, self).get_search_results(request, queryset, search_term)
        queryset |= self.model.objects.filter(user__email__icontains=search_term)
        queryset |= self.model.objects.filter(user__userprofile__customer_number__icontains=search_term)
        return queryset, use_distinct
class UserProxy(User):
    class Meta:
        proxy = True
class UserResource(resources.ModelResource):
    class Meta:
        model = UserProxy
        fields = ('email','first_name', 'last_name')
class UserAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = UserResource

admin.site.register(yunda_user_models.Branch, BranchAdmin)
admin.site.register(yunda_user_models.StaffProfile, StaffProfileAdmin)
admin.site.register(yunda_user_models.DepositTransfer, DepositTransferAdmin)
admin.site.register(yunda_user_models.InvoiceHistory, InvoiceHistoryAdmin)
admin.site.register(yunda_user_models.Invoice, InvoiceAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(yunda_user_models.DepositTransferNew, DepositTransferNewAdmin)
admin.site.register(UserProxy, UserAdmin)


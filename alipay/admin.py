from django.contrib import admin
from alipay import models

# Register your models here.
class AlipayDepositOrderAdmin(admin.ModelAdmin):
    list_display = ('yid', 'user', 'amount','currency_type','created_at','success_at')
    list_filter = ('user','currency_type')
admin.site.register(models.AlipayDepositOrder, AlipayDepositOrderAdmin)


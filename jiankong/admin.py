from django.contrib import admin
from jiankong import models

# Register your models here.
class IntlParcelJiankongAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'type_code', 'mawb','customer_number','finished_jiankong','status')
    list_filter = ('type_code', 'mawb', 'customer_number','status')
admin.site.register(models.IntlParcelJiankong, IntlParcelJiankongAdmin)
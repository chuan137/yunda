from django.contrib import admin
from yadmin import models

# Register your models here.
class DespositEntryAdmin(admin.ModelAdmin):
    list_display = ('customer_number', 'amount','origin', 'ref','created_at','created_by','approved_by')
    search_fields = ('customer_number', 'amount','origin', 'ref')    

admin.site.register(models.DespositEntry, DespositEntryAdmin)


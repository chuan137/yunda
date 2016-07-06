from django.contrib import admin
from cn_shenfenzheng import models

# Register your models here.
class CnShenfenzhengAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.CnShenfengzheng, CnShenfenzhengAdmin)
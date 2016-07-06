from django.contrib import admin
from yunda_parcel import models 
from import_export.admin import ImportExportMixin
from import_export import resources, widgets

from yunda_parcel.models import CnCustomsTaxCatalog
from django.utils.translation import ugettext_lazy as _
# Register your models here.
from django.conf import settings
import os
import json


class ParcelTypeAdmin(admin.ModelAdmin):
    pass
    
class CustomerParcelPriceAdmin(admin.ModelAdmin):
    pass
class BranchParcelPriceAdmin(admin.ModelAdmin):
    pass
class BranchAllowedParcelPriceAdmin(admin.ModelAdmin):
    pass
class ParcelAdmin(admin.ModelAdmin):
    list_filter = ('payment_status', 'position_status', 'cn_tax_status',
                   'is_delete', 'is_synced',)
    list_display = ('yde_number', 'user', 'created_at', 'payment_status', 'tracking_number')
    

class CnCustomsTaxResource(resources.ModelResource):
    
    def import_obj(self, obj, data, dry_run):
        """
        """
        if data['charge_by_weight'] == "":
            data['charge_by_weight'] = False
        else:
            data['charge_by_weight'] = True
            
        if data['is_forbidden'] == "":
            data['is_forbidden'] = False
        else:
            data['is_forbidden'] = True
        
        if data['categories'] == "":
            data['categories'] = None
        else:
            catalog_ids = ""
            for catalog_name in data['categories'].split(','):
                catalog = CnCustomsTaxCatalog.objects.get_or_create(cn_name=catalog_name)[0]
                catalog_ids += ','
                catalog_ids += str(catalog.id)
            data['categories'] = catalog_ids.split(',', 1)[1]
        try:
            for tax in models.CnCustomsTax.objects.filter(cn_name=data['cn_name'], is_active=True):
                tax.is_active = False
                tax.save()
        except models.CnCustomsTax.DoesNotExist:
            pass
        
        super(CnCustomsTaxResource, self).import_obj(obj, data, dry_run)
              
    class Meta:
        model = models.CnCustomsTax
        fields = ('id', 'cn_name', 'cn_custom_number', 'tax_rate', 'charge_by_weight', 'standard_unit_price_cny', 'is_forbidden', 'categories')
  
class CnCustomsTaxAdmin(ImportExportMixin, admin.ModelAdmin):
    list_filter = ['charge_by_weight', 'is_forbidden', 'is_active', 'categories']
    resource_class = CnCustomsTaxResource
    list_display = ['cn_name', 'cn_custom_number', 'tax_rate', 'standard_unit_price_cny', 'charge_by_weight', 'is_active']
    ordering = ['cn_custom_number']
    actions = ['action_deactive', 'action_create_script', 'action_create_script_new']
    
    def action_deactive(self, request, queryset):
        rows_updated = queryset.update(is_active=False)
        if rows_updated == 1:
            message_bit = "1 tax rule was"
        else:
            message_bit = "%s tax rules were" % rows_updated
        self.message_user(request, "%s successfully deactived." % message_bit)
    action_deactive.short_description = _("Deactive") 
    def action_create_script(self, request, queryset):
        data_catalogs = []
        for catalog in CnCustomsTaxCatalog.objects.all():
            data_catalog = {'name':catalog.cn_name,
                          'id':catalog.id}
            taxes = []
            for tax in catalog.cncustomstax_set.filter(is_active=True):
                taxes.append({
                              'id':tax.id,
                              'name':tax.cn_name
                              })
            data_catalog['taxes'] = taxes
            data_catalogs.append(data_catalog)
        file_name = os.path.join(settings.STATICFILES_DIRS[0], 'cn_tax_catalog.json')
        with open(file_name, 'w') as out:
            out.write(json.dumps(data_catalogs))
        
        return True
    action_create_script.short_description = _('Create json js')
    
    def action_create_script_new(self, request, queryset):
        data_catalogs = {}
        key_catalogs = []
        shuijin={}
        for catalog in CnCustomsTaxCatalog.objects.all():
            taxes = []
            for tax in catalog.cncustomstax_set.filter(is_active=True):
                taxes.append(tax.cn_name)
                shuijin[tax.cn_name]={"tax_rate":tax.tax_rate,
                                      "standard_unit_price_cny":tax.standard_unit_price_cny,
                                      "charge_by_weight":tax.charge_by_weight,
                                      "standard_unit_price_cny":tax.standard_unit_price_cny,}
            data_catalogs[catalog.cn_name] = taxes
            key_catalogs.append(catalog.cn_name)
        file_name = os.path.join(settings.STATICFILES_DIRS[0], 'cn_tax_catalog_new.json')
        with open(file_name, 'w') as out:
            out.write(json.dumps({"catalogs":data_catalogs, "keys":key_catalogs,"taxes":shuijin}))
        
        return True
    action_create_script_new.short_description = _('Create json js, NEW')
            
    
class ParcelDetailAdmin(admin.ModelAdmin):
    pass

class CnCustomsTaxCatalogResource(resources.ModelResource):
    def import_obj(self, obj, data, dry_run):
        """
        """
        
        
        super(CnCustomsTaxCatalogResource, self).import_obj(obj, data, dry_run)
    class Meta:
        model = models.CnCustomsTaxCatalog
        fields = ('id', 'cn_name', 'en_name')

class CnCustomsTaxCatalogAdmin(ImportExportMixin, admin.ModelAdmin):
    list_filter = ['cn_name']
    resource_class = CnCustomsTaxCatalogResource
class CnShenfengzhengAdmin(admin.ModelAdmin):
    pass
class SenderTemplateAdmin(admin.ModelAdmin):
    pass
class ReceiverTemplateAdmin(admin.ModelAdmin):
    pass
class DhlRetoureLabelAdmin(admin.ModelAdmin):
    list_display = ('get_customer_number', 'created_at', 'payment_status', 'tracking_number')
#    list_filter = ('type','status','is_deleted','sync_status')
    search_fields = ('retoure_yde_number','tracking_number','sender_name')
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(DhlRetoureLabelAdmin, self).get_search_results(request, queryset, search_term)
        queryset |= self.model.objects.filter(user__userprofile__customer_number__icontains=search_term)
        return queryset, use_distinct

class ParcelStatusHistoryAdmin(admin.ModelAdmin):
    pass
class DhlRetoureLabelStatusHistoryAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.ParcelType, ParcelTypeAdmin)
admin.site.register(models.CustomerParcelPrice, CustomerParcelPriceAdmin)
admin.site.register(models.BranchParcelPrice, BranchParcelPriceAdmin)
admin.site.register(models.BranchAllowedParcelPrice, BranchAllowedParcelPriceAdmin)
admin.site.register(models.Parcel, ParcelAdmin)
admin.site.register(models.CnCustomsTax, CnCustomsTaxAdmin)
admin.site.register(models.ParcelDetail, ParcelDetailAdmin)
admin.site.register(models.CnCustomsTaxCatalog, CnCustomsTaxCatalogAdmin)
admin.site.register(models.CnShenfengzheng, CnShenfengzhengAdmin)
admin.site.register(models.SenderTemplate, SenderTemplateAdmin)
admin.site.register(models.ReceiverTemplate, ReceiverTemplateAdmin)
admin.site.register(models.DhlRetoureLabel, DhlRetoureLabelAdmin)
admin.site.register(models.DhlRetoureLabelStatusHistory, DhlRetoureLabelStatusHistoryAdmin)
admin.site.register(models.ParcelStatusHistory, ParcelStatusHistoryAdmin)

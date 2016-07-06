from django.contrib import admin
from parcel import models
# Register your models here.
class ParcelTypeAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.ParcelType, ParcelTypeAdmin)

class PriceLevelAdmin(admin.ModelAdmin):
    list_display = ('level', 'currency_type', 'parcel_type','json_prices')
    list_filter = ('level', 'currency_type', 'parcel_type')
admin.site.register(models.PriceLevel, PriceLevelAdmin)

class LevelAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.Level, LevelAdmin)

class GoodsDetailInline(admin.TabularInline):
    model=models.GoodsDetail
    extra=0

class HistoryInline(admin.TabularInline):
    model=models.History
    extra=0

class IntlParcelAdmin(admin.ModelAdmin):
    list_display = ('sender_name', 'receiver_name','yde_number', 'get_customer_number','type', 'booked_fee')
    list_filter = ('type','status','is_deleted','sync_status',)
    def get_customer_number(self, obj):
        return obj.user.userprofile.customer_number
    get_customer_number.short_description = 'Customer number'
    get_customer_number.admin_order_field = 'user__userprofile__customer_number'
    
    inlines=[GoodsDetailInline,HistoryInline]
    search_fields = ('yde_number','tracking_number','sender_name','receiver_name')
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(IntlParcelAdmin, self).get_search_results(request, queryset, search_term)
        queryset |= self.model.objects.filter(user__userprofile__customer_number__icontains=search_term)
        return queryset, use_distinct
admin.site.register(models.IntlParcel, IntlParcelAdmin)

class GssAdmin(admin.ModelAdmin):
    list_display = ('cn_customs_code', 'qr_traderId', 'tracking_username')
admin.site.register(models.Gss, GssAdmin)

class BatchInline(admin.TabularInline):
    model=models.Batch
    extra=0

class MawbAdmin(admin.ModelAdmin):
    list_display = ('mawb_number', 'cn_customs','need_receiver_name_mobiles', 'need_total_value_per_sender','status','created_at','id')
    list_filter = ('cn_customs','status','created_at')
    inlines=[BatchInline]
admin.site.register(models.Mawb, MawbAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('en_name', 'cn_name','unit_net_weight_volumn', 'net_weight_volumn_unit','price_eur','cn_tax_name','cn_tax_number','cn_tax_standard_price_cny','cn_tax_rate','cn_tax_unit','get_product_categories','get_product_brand')
    def get_product_categories(self,obj):
        categories=u""
        for category in obj.product_categories.all():
            categories+= u"%s-%s => %s-%s | " % (category.product_main_category.cn_name,category.product_main_category.en_name,
                                             category.cn_name,category.en_name)
        return categories
    get_product_categories.short_description="Category"
    def get_product_brand(self,obj):
        return u"%s-%s" % (obj.product_brand.cn_name,obj.product_brand.en_name)
    get_product_brand.short_description="Brand"
    get_product_brand.admin_order_field="product_brand__cn_name"
    
admin.site.register(models.Product, ProductAdmin)

class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('en_name', 'cn_name','get_product_main_category', 'histories')
    def get_product_main_category(self,obj):
        return u"%s - %s" % (obj.product_main_category.cn_name,obj.product_main_category.en_name)
    get_product_main_category.short_description="Main category"
    get_product_main_category.admin_order_field="product_main_category__cn_name"
admin.site.register(models.ProductCategory, ProductCategoryAdmin)

class ProductMainCategoryAdmin(admin.ModelAdmin):
    list_display = ('en_name', 'cn_name', 'histories')
admin.site.register(models.ProductMainCategory, ProductMainCategoryAdmin)

class ProductBrandAdmin(admin.ModelAdmin):
    list_display = ('en_name', 'cn_name', 'histories')
admin.site.register(models.ProductBrand, ProductBrandAdmin)

class CnCustomsAdmin(admin.ModelAdmin):
    list_display = ('name', 'code','is_active', 'settings')
admin.site.register(models.CnCustoms, CnCustomsAdmin)


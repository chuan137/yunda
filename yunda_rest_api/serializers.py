from yunda_parcel import models as parcel_models
from rest_framework import serializers
from django.contrib.auth.models import User
from userena.models import UserProfile


class ParcelDetailField(serializers.RelatedField):
    def to_representation(self, value):
        return {'description':value.description,
                'qty':value.qty,
                'item_net_weight_kg':value.item_net_weight_kg,
                'item_price_eur':value.item_price_eur,
                'original_country':value.original_country,
                
                'cn_name':value.cn_customs_tax.cn_name,
                'en_name':value.cn_customs_tax.en_name,
                'cn_custom_number':value.cn_customs_tax.cn_custom_number,
                'hs_code': value.cn_customs_tax.hs_code,
                'tax_rate':value.cn_customs_tax.tax_rate,
                'standard_unit_price_cny':value.cn_customs_tax.standard_unit_price_cny,
                'charge_by_weight':value.cn_customs_tax.charge_by_weight,
                
                }

class UserField(serializers.RelatedField):
    def to_representation(self, value):
        return value.userprofile.customer_number

class BranchField(serializers.RelatedField):
    def to_representation(self, value):
        return value.branch_number
    
class TypeField(serializers.RelatedField):
    def to_representation(self, value):
        return value.code
    
class ParcelSerializer(serializers.ModelSerializer):
    details = ParcelDetailField(many=True, read_only=True)
    user = UserField(read_only=True)
    salesman = UserField(read_only=True)
    branch = BranchField(read_only=True)
    type = TypeField(read_only=True)
    class Meta:
        model = parcel_models.Parcel
        fields = ('type',
                                 
                  'sender_name',
                  'sender_name2',
                  'sender_company',
                  'sender_state',
                  'sender_city',
                  'sender_postcode',
                  'sender_street',
                  'sender_add',
                  'sender_hause_number',
                  'sender_tel',
                  'sender_email',
                  'sender_country',
                  
                  'receiver_name',
                  'receiver_company',
                  'receiver_province',
                  'receiver_city',
                  'receiver_district',
                  'receiver_postcode',
                  'receiver_address',
                  'receiver_address2',
                  'receiver_mobile',
                  'receiver_email',
                  'receiver_country',
                  
                  'ref',
                  'weight_kg',
                  'length_cm',
                  'width_cm',
                  'height_cm',
                  'real_weight_kg',
                  'real_length_cm',
                  'real_width_cm',
                  'real_height_cm',
                  'real_cn_customs_tax_cny',
                  
                  'start_price_eur',
                  'start_weight_kg',
                  'continuing_price_eur',
                  'continuing_weight_kg',
                  'volume_weight_rate',
                  
                  'branch_start_price_eur',
                  'branch_start_weight_kg',
                  'branch_continuing_price_eur',
                  'branch_continuing_weight_kg',
                  'branch_volume_weight_rate',
                  
                  'tracking_number',
                  'tracking_number_created_at',
                  'yde_number',
                  'created_at',
                  'printed_at',
                  'sender_pay_cn_customs',
                  
                  'user',
                  'salesman',
                  'branch',
                  'payment_status',
                  'position_status',
                  'cn_tax_status',
                  'fee_paid_eur',
                  'cn_tax_paid_cny',
                  'eur_to_cny_rate',
                  
                  'is_delete',
                  
                  'details',
                  )
class ProfileUserField(serializers.RelatedField):
    def to_representation(self, value):
        return {'name':value.first_name + ' ' + value.last_name, 'email':value.email}
class NameField(serializers.RelatedField):
    def to_representation(self, value):
        return value.first_name + ' ' + value.last_name
class CustomerSerializer(serializers.ModelSerializer):
    user = ProfileUserField(read_only=True)
    salesman = UserField(read_only=True)
    branch = BranchField(read_only=True)
    #name = NameField(queryset='user')
    class Meta:
        model = UserProfile
        fields = ('user',
                  #'name',
                  'customer_number',
                  'company',
                  'street',
                  'hause_number',
                  'street_add',
                  'postcode',
                  'city',
                  'state',
                  'country_code',
                  'tel',
                  'fax',
                  'vat_id',
                  'salesman',
                  'branch',
                  'deposit_currency_type',
                  )

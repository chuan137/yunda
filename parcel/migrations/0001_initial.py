# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import parcel.models
import jsonfield.fields
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order_number', models.IntegerField()),
                ('sign', models.CharField(max_length=20, validators=[parcel.models.field_validator_only_alphabeta_num])),
                ('color', models.CharField(max_length=7)),
                ('total_value_per_sender', jsonfield.fields.JSONField(default={})),
                ('max_value', models.FloatField()),
                ('yids', jsonfield.fields.JSONField(default=[])),
                ('status', models.CharField(default=b'warehouse_open', max_length=50, choices=[(b'warehouse_open', 'Open at Warehouse'), (b'warehouse_closed', 'Closed at Warehouse'), (b'export_customs_cleared', 'Export customs cleared'), (b'error', 'Error')])),
                ('histories', jsonfield.fields.JSONField(default=[])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GoodsDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=50, verbose_name='\u8d27\u7269\u63cf\u8ff0')),
                ('cn_customs_tax_catalog_name', models.CharField(max_length=50, verbose_name='\u4e3b\u5206\u7c7b', blank=True)),
                ('cn_customs_tax_name', models.CharField(max_length=50, verbose_name='\u4e8c\u7ea7\u5206\u7c7b', blank=True)),
                ('qty', models.FloatField(verbose_name='\u6570\u91cf')),
                ('item_net_weight_kg', models.FloatField(verbose_name='\u5355\u4ef6\u51c0\u91cd Kg')),
                ('item_price_eur', models.FloatField(verbose_name='\u5355\u4ef7 \u20ac')),
                ('original_country', models.CharField(default=b'DE', max_length=2, verbose_name='\u539f\u4ea7\u5730')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Gss',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('qr_api_url', models.CharField(max_length=100)),
                ('qr_traderId', models.CharField(max_length=50)),
                ('qr_passwd', models.CharField(max_length=50)),
                ('qr_buz_type', models.CharField(max_length=50)),
                ('qr_version', models.CharField(max_length=50)),
                ('qr_data_style', models.CharField(max_length=50)),
                ('qr_sign_infor', models.CharField(max_length=50, blank=True)),
                ('add_tracking_api_url', models.CharField(max_length=100)),
                ('get_tracking_api_url', models.CharField(max_length=100)),
                ('tracking_username', models.CharField(max_length=50)),
                ('tracking_passwd', models.CharField(max_length=50)),
                ('tracking_version', models.CharField(max_length=50)),
                ('cn_customs_code', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, null=True, verbose_name='\u8bb0\u5f55\u65f6\u95f4')),
                ('description', models.TextField(verbose_name='\u8bb0\u5f55\u5185\u5bb9')),
                ('visible_to_customer', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IntlParcel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('yid', models.CharField(max_length=b'40', verbose_name='YID', blank=True)),
                ('sender_name', models.CharField(max_length=25, verbose_name='Sender name', validators=[parcel.models.field_validator_only_alphabeta_num])),
                ('sender_name2', models.CharField(blank=True, max_length=25, verbose_name='Sender name2', validators=[parcel.models.field_validator_only_alphabeta_num])),
                ('sender_company', models.CharField(blank=True, max_length=25, verbose_name='Sender company', validators=[parcel.models.field_validator_only_alphabeta_num])),
                ('sender_state', models.CharField(blank=True, max_length=25, verbose_name='Sender state', validators=[parcel.models.field_validator_only_alphabeta_num])),
                ('sender_city', models.CharField(max_length=25, verbose_name='Sender city', validators=[parcel.models.field_validator_only_alphabeta_num])),
                ('sender_postcode', models.CharField(max_length=5, verbose_name='Sender postcode')),
                ('sender_street', models.CharField(max_length=25, verbose_name='Sender street', validators=[parcel.models.field_validator_only_alphabeta_num])),
                ('sender_add', models.CharField(blank=True, max_length=25, verbose_name='Sender street addition', validators=[parcel.models.field_validator_only_alphabeta_num])),
                ('sender_hause_number', models.CharField(max_length=10, verbose_name='Sender hause number', validators=[parcel.models.field_validator_only_alphabeta_num])),
                ('sender_tel', models.CharField(max_length=15, verbose_name='Sender telephone')),
                ('sender_email', models.EmailField(blank=True, max_length=75, verbose_name='Sender email', validators=[django.core.validators.EmailValidator])),
                ('sender_country', models.CharField(default=b'DE', max_length=2, verbose_name='Sender country')),
                ('receiver_name', models.CharField(max_length=50, verbose_name='Receiver name', validators=[parcel.models.field_validator_only_chinese])),
                ('receiver_company', models.CharField(blank=True, max_length=50, verbose_name='Receiver company', validators=[parcel.models.field_validator_chinese_and_alphabeta])),
                ('receiver_province', models.CharField(max_length=20, verbose_name='Receiver province', validators=[parcel.models.field_validator_only_chinese])),
                ('receiver_city', models.CharField(blank=True, max_length=20, verbose_name='Receiver city', validators=[parcel.models.field_validator_only_chinese])),
                ('receiver_district', models.CharField(blank=True, max_length=20, verbose_name='Receiver district', validators=[parcel.models.field_validator_only_chinese])),
                ('receiver_postcode', models.CharField(blank=True, max_length=6, verbose_name='Receiver postcode', validators=[parcel.models.field_validator_chinese_postcode])),
                ('receiver_address', models.CharField(max_length=50, verbose_name='Receiver address', validators=[parcel.models.field_validator_chinese_and_alphabeta])),
                ('receiver_address2', models.CharField(blank=True, max_length=50, verbose_name='Receiver address2', validators=[parcel.models.field_validator_chinese_and_alphabeta])),
                ('receiver_mobile', models.CharField(max_length=11, verbose_name='Receiver mobilephone', validators=[parcel.models.field_validator_chinese_mobile_phone])),
                ('receiver_email', models.EmailField(blank=True, max_length=75, verbose_name='Receiver email', validators=[django.core.validators.EmailValidator])),
                ('receiver_country', models.CharField(default=b'CN', max_length=2, verbose_name='Receiver country')),
                ('ref', models.CharField(max_length=50, verbose_name='Ref number', blank=True)),
                ('weight_kg', models.FloatField(default=0.1, verbose_name='Weight (kg)', validators=[django.core.validators.MinValueValidator(0.01)])),
                ('length_cm', models.FloatField(default=0.1, verbose_name='Length (cm)', validators=[django.core.validators.MinValueValidator(0.01)])),
                ('width_cm', models.FloatField(default=0.1, verbose_name='Width (cm)', validators=[django.core.validators.MinValueValidator(0.01)])),
                ('height_cm', models.FloatField(default=0.1, verbose_name='Height (cm)', validators=[django.core.validators.MinValueValidator(0.01)])),
                ('real_weight_kg', models.FloatField(default=0.1, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('real_length_cm', models.FloatField(default=0.1, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('real_width_cm', models.FloatField(default=0.1, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('real_height_cm', models.FloatField(default=0.1, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('booked_fee', models.FloatField(default=0)),
                ('currency_type', models.CharField(max_length=3)),
                ('json_prices', jsonfield.fields.JSONField(default={})),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('printed_at', models.DateTimeField(null=True, verbose_name='Printed at')),
                ('yde_number', models.CharField(max_length=b'20', verbose_name='Order number', blank=True)),
                ('sfz_status', models.CharField(default=b'2', max_length=1, blank=True, choices=[(b'0', '\u4e0d\u9700\u8eab\u4efd\u8bc1'), (b'1', '\u5df2\u4e0a\u4f20'), (b'2', '\u672a\u4e0a\u4f20')])),
                ('cn_customs_paid_by', models.CharField(default=b'sender', max_length=10, blank=True, choices=[(b'sender', '\u53d1\u4ef6\u4eba'), (b'receiver', '\u6536\u4ef6\u4eba')])),
                ('pdf_info', models.TextField(default=b'', blank=True)),
                ('tracking_number', models.CharField(max_length=b'20', blank=True)),
                ('tracking_number_created_at', models.DateTimeField(null=True, blank=True)),
                ('retoure_tracking_number', models.CharField(max_length=b'20', blank=True)),
                ('retoure_routing_code', models.CharField(max_length=b'20', blank=True)),
                ('retoure_tracking_number_created_at', models.DateTimeField(null=True, blank=True)),
                ('status', models.CharField(default=b'draft', max_length=50, verbose_name='\u72b6\u6001', choices=[(b'draft', '\u8349\u7a3f'), (b'confirmed', '\u786e\u8ba4\u63d0\u4ea4'), (b'proccessing_at_yde', '\u97f5\u8fbe\u6b27\u6d32\u5904\u7406\u4e2d'), (b'transit_to_destination_country', '\u8fd0\u8f93\u81f3\u76ee\u7684\u56fd\u5bb6\u9014\u4e2d'), (b'custom_clearance_at_destination_country', '\u76ee\u7684\u56fd\u6e05\u5173\u4e2d'), (b'distributing_at_destination_country', '\u76ee\u7684\u56fd\u4e2d\u8f6c\u6d3e\u9001'), (b'distributed_at_destination_country', '\u5305\u88f9\u5df2\u9001\u8fbe'), (b'error', '\u5f02\u5e38\uff0c\u7b49\u5f85\u5904\u7406')])),
                ('is_deleted', models.NullBooleanField(default=False)),
                ('sync_status', models.CharField(default=b'need_to_sync', max_length=50, verbose_name='\u540c\u6b65\u81f3ERP\u72b6\u6001', choices=[(b'need_to_sync', '\u9700\u8981\u540c\u6b65\u81f3ERP'), (b'waiting_to_sync', '\u7b49\u5f85\u540c\u6b65\u81f3ERP'), (b'synced', '\u5df2\u540c\u6b65\u81f3ERP')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(default=b'test', max_length=10)),
                ('name', models.CharField(default=b'Test', max_length=30)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Mawb',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mawb_number', models.CharField(unique=True, max_length=20, validators=[parcel.models.field_validator_only_alphabeta_num])),
                ('cn_customs', models.CharField(max_length=20, validators=[parcel.models.field_validator_only_alphabeta_num])),
                ('need_receiver_name_mobiles', models.BooleanField(default=False)),
                ('need_total_value_per_sender', models.BooleanField(default=False)),
                ('receiver_name_mobiles', jsonfield.fields.JSONField(default=[])),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('status', models.CharField(default=b'draft', max_length=50, choices=[(b'draft', 'Draft'), (b'warehouse_open', 'Open at Warehouse'), (b'warehouse_closed', 'Closed at Warehouse'), (b'transfered_to_partner', 'Transfered to partner'), (b'flied_to_dest', 'Flied to destination country'), (b'landed_at_dest', 'Landed at destination country'), (b'customs_cleared', 'Customs clearance finished at destination country'), (b'error', 'Error')])),
                ('histories', jsonfield.fields.JSONField(default=[])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ParcelType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=30)),
                ('description', models.TextField(default=b'Parcel description')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PriceLevel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('currency_type', models.CharField(default=b'cny', max_length=3)),
                ('json_prices', jsonfield.fields.JSONField(default=b'{"type":"table","volume_weight_rate":6000,\n"1.0":10,\n"2.0":20,\n"3.0":10,\n"4.0":10,\n"5.0":10,\n"6.0":10,\n"7.0":10,\n"8.0":10,\n"9.0":10,\n"10.0":10,\n"11.0":10,\n"12.0":10,\n"13.0":10,\n"14.0":10,\n"15.0":10,\n"16.0":10,\n"17.0":10,\n"18.0":10,\n"19.0":10,\n"20.0":10,\n"21.0":10,\n"22.0":10,\n"23.0":10,\n"24.0":10,\n"25.0":10,\n"26.0":10,\n"27.0":10,\n"28.0":10,\n"29.0":10,\n"30.0":10}\n\n{"type":"linear","volume_weight_rate":6000,"starting_weight_kg":1,"starting_price":9.5,"continuing_weight_kg":0.5,"continuing_price":2.4}')),
                ('level', models.ForeignKey(to='parcel.Level')),
                ('parcel_type', models.ForeignKey(to='parcel.ParcelType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='intlparcel',
            name='type',
            field=models.ForeignKey(related_name='intlparcels', to='parcel.ParcelType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='intlparcel',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='history',
            name='intl_parcel',
            field=models.ForeignKey(related_name='histories', to='parcel.IntlParcel', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='history',
            name='staff',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='goodsdetail',
            name='intl_parcel',
            field=models.ForeignKey(related_name='goodsdetails', to='parcel.IntlParcel', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='batch',
            name='mawb',
            field=models.ForeignKey(related_name='batches', to='parcel.Mawb'),
            preserve_default=True,
        ),
    ]

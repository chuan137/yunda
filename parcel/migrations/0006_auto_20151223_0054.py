# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('parcel', '0005_auto_20151207_1401'),
    ]

    operations = [
        migrations.CreateModel(
            name='CnCustoms',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(unique=True, max_length=20)),
                ('name', models.CharField(max_length=50)),
                ('is_active', models.BooleanField(default=False)),
                ('settings', jsonfield.fields.JSONField(default=b'{"need_receiver_name_mobiles":true,\n"need_total_value_per_sender":true,\n"total_value_per_sender_eur":1000,\n"need_sfz":true,\n"batch_settings":[{"order_number":1,"sign":"","color":""},\n{"order_number":2,"sign":"","color":""}\n]}')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('en_name', models.CharField(max_length=100)),
                ('cn_name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
                ('cn_tax_name', models.CharField(max_length=100)),
                ('cn_tax_number', models.CharField(max_length=10)),
                ('cn_tax_standard_price_cny', models.FloatField()),
                ('cn_tax_rate', models.FloatField()),
                ('cn_tax_unit', models.CharField(max_length=10)),
                ('cn_real_unit_tax_cny', jsonfield.fields.JSONField(default=[])),
                ('price_eur', models.FloatField()),
                ('unit', models.CharField(max_length=10)),
                ('unit_net_weight_volumn', models.FloatField()),
                ('net_weight_volumn_unit', models.CharField(max_length=5)),
                ('sku', models.CharField(unique=True, max_length=50)),
                ('yid', models.CharField(max_length=40, blank=True)),
                ('url', models.CharField(max_length=256)),
                ('small_pic_url', models.CharField(max_length=50, blank=True)),
                ('price_pic_url', models.CharField(max_length=50, blank=True)),
                ('histories', jsonfield.fields.JSONField(default=[], null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductBrand',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cn_name', models.CharField(unique=True, max_length=100)),
                ('en_name', models.CharField(unique=True, max_length=100)),
                ('histories', jsonfield.fields.JSONField(default=[])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cn_name', models.CharField(max_length=100)),
                ('en_name', models.CharField(max_length=100)),
                ('histories', jsonfield.fields.JSONField(default=[])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductMainCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cn_name', models.CharField(unique=True, max_length=100)),
                ('en_name', models.CharField(unique=True, max_length=100)),
                ('histories', jsonfield.fields.JSONField(default=[])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='productcategory',
            name='product_main_category',
            field=models.ForeignKey(to='parcel.ProductMainCategory'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='productcategory',
            unique_together=set([('en_name', 'product_main_category'), ('cn_name', 'product_main_category')]),
        ),
        migrations.AddField(
            model_name='product',
            name='product_brand',
            field=models.ForeignKey(blank=True, to='parcel.ProductBrand', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='product_categories',
            field=models.ManyToManyField(to='parcel.ProductCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='goodsdetail',
            name='product',
            field=models.ForeignKey(blank=True, to='parcel.Product', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='intlparcel',
            name='cn_tax_paid_cny',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='intlparcel',
            name='cn_tax_to_pay_cny',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='intlparcel',
            name='customs_code_forced',
            field=models.CharField(default=b'', max_length=20),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='intlparcel',
            name='internal_histories',
            field=jsonfield.fields.JSONField(default=[], null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='intlparcel',
            name='processing_msg',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='history',
            name='staff',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='history',
            name='tracking_pushed_at',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yunda_parcel', '0002_auto_20150330_2055'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParcelPriceLevel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=15)),
                ('code', models.CharField(max_length=15)),
                ('currency_type', models.CharField(default=b'draft', max_length=3, verbose_name='\u8d27\u5e01\u7c7b\u578b', choices=[(b'eur', 'EUR'), (b'cny', 'CNY')])),
                ('start_price', models.FloatField(verbose_name='\u9996\u91cd\u4ef7\u683c \uffe5')),
                ('start_weight_kg', models.FloatField(verbose_name='\u9996\u91cd\u91cd\u91cf Kg')),
                ('continuing_price', models.FloatField(verbose_name='\u7eed\u91cd\u4ef7\u683c \uffe5')),
                ('continuing_weight_kg', models.FloatField(verbose_name='\u7eed\u91cd\u91cd\u91cf Kg')),
                ('volume_weight_rate', models.FloatField(null=True, verbose_name='\u4f53\u79ef\u91cd\u91cf\u6bd4')),
                ('description', models.TextField(verbose_name='\u8bf4\u660e', blank=True)),
                ('parcel_type', models.ForeignKey(to='yunda_parcel.ParcelType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RetoureHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, null=True, verbose_name='\u8bb0\u5f55\u65f6\u95f4')),
                ('description', models.TextField(verbose_name='\u8bb0\u5f55\u5185\u5bb9')),
                ('visible_to_customer', models.BooleanField(default=True)),
                ('retoure', models.ForeignKey(related_name='histories', to='yunda_parcel.DhlRetoureLabel', null=True)),
                ('staff', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='dhlretourelabel',
            name='currency_type',
            field=models.CharField(default=b'cny', max_length=3),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dhlretourelabel',
            name='price',
            field=models.FloatField(default=3.9),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dhlretourelabel',
            name='routing_code',
            field=models.CharField(max_length=20, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dhlretourelabel',
            name='status',
            field=models.CharField(default=b'draft', max_length=20, choices=[(b'draft', '\u8349\u7a3f'), (b'confirmed', '\u5df2\u63d0\u4ea4'), (b'finished', '\u5df2\u4f7f\u7528')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dhlretourelabel',
            name='yd_pdf_file',
            field=models.BinaryField(blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dhlretourelabel',
            name='yid',
            field=models.CharField(max_length=b'40', verbose_name='YID', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='receivertemplate',
            name='yid',
            field=models.CharField(max_length=b'40', verbose_name='YID', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sendertemplate',
            name='yid',
            field=models.CharField(max_length=b'40', verbose_name='YID', blank=True),
            preserve_default=True,
        ),
    ]

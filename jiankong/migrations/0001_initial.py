# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parcel', '0004_auto_20151013_2348'),
    ]

    operations = [
        migrations.CreateModel(
            name='IntlParcelJiankong',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('yid', models.CharField(unique=True, max_length=40)),
                ('customer_number', models.CharField(max_length=10)),
                ('tracking_number', models.CharField(max_length=20)),
                ('type_code', models.CharField(max_length=40, blank=True)),
                ('finished_jiankong', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(null=True, blank=True)),
                ('opc_arrived_at', models.DateTimeField(null=True, verbose_name=b'OPC arrived at', blank=True)),
                ('opc_export_ready_at', models.DateTimeField(null=True, verbose_name=b'OPC export ready at', blank=True)),
                ('opc_export_customs_finished_at', models.DateTimeField(null=True, verbose_name=b'OPC export customs cleared at', blank=True)),
                ('opc_flied_at', models.DateTimeField(null=True, verbose_name=b'OPC flied to destination country at', blank=True)),
                ('destination_country_arrived_at', models.DateTimeField(null=True, blank=True)),
                ('import_customs_finished_at', models.DateTimeField(null=True, blank=True)),
                ('local_opc_received_at', models.DateTimeField(null=True, blank=True)),
                ('delivery_staff_asigned_at', models.DateTimeField(null=True, blank=True)),
                ('deliveried_at', models.DateTimeField(null=True, blank=True)),
                ('status', models.CharField(max_length=40, blank=True)),
                ('newest_datetime', models.DateTimeField(null=True, blank=True)),
                ('mawb', models.ForeignKey(blank=True, to='parcel.Mawb', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yunda_parcel', '0005_auto_20151012_0152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parcel',
            name='printed_at',
            field=models.DateTimeField(null=True, verbose_name='Printed at', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='parcel',
            name='real_cn_customs_tax_cny',
            field=models.FloatField(default=0, verbose_name='Real customs tax (CNY)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='parcel',
            name='tracking_number_created_at',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='parcel',
            name='yde_number',
            field=models.CharField(max_length=32, verbose_name='YDE number', blank=True),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('yunda_commen', '0002_auto_20150330_2055'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='dhl_retoure_price_cny',
            field=models.FloatField(default=29),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sequence',
            name='last_datetime',
            field=models.DateTimeField(default=datetime.datetime.now),
            preserve_default=True,
        ),
    ]

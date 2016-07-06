# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('yunda_commen', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sequence',
            name='last_datetime',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 30, 20, 55, 28, 467133)),
            preserve_default=True,
        ),
    ]

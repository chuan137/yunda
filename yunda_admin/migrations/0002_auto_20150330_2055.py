# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('yunda_admin', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='depositentry',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 30, 20, 55, 28, 513769)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='depositwithdraw',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 30, 20, 55, 28, 514797)),
            preserve_default=True,
        ),
    ]

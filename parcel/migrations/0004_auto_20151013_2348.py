# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parcel', '0003_auto_20151012_0018'),
    ]

    operations = [
        migrations.AddField(
            model_name='history',
            name='tracking_pushed',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='history',
            name='tracking_pushed_at',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]

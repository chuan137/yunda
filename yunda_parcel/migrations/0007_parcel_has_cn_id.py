# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yunda_parcel', '0006_auto_20151130_0021'),
    ]

    operations = [
        migrations.AddField(
            model_name='parcel',
            name='has_cn_id',
            field=models.NullBooleanField(default=False),
            preserve_default=True,
        ),
    ]

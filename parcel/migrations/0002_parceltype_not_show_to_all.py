# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parcel', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='parceltype',
            name='not_show_to_all',
            field=models.NullBooleanField(default=False),
            preserve_default=True,
        ),
    ]

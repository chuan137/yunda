# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userena', '0004_userprofile_allow_dhl_no_retoure'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='trusted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]

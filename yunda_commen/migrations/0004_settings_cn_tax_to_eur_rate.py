# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yunda_commen', '0003_auto_20151011_1834'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='cn_tax_to_eur_rate',
            field=models.FloatField(default=6.8),
            preserve_default=True,
        ),
    ]

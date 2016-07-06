# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jiankong', '0005_intlparceljiankong_messages'),
    ]

    operations = [
        migrations.AddField(
            model_name='intlparceljiankong',
            name='days_delayed',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intlparceljiankong',
            name='yid',
            field=models.CharField(unique=True, max_length=40, verbose_name=b'Parcel yid'),
            preserve_default=True,
        ),
    ]

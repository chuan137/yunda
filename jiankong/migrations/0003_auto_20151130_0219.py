# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('jiankong', '0002_intlparceljiankong_last_checked_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intlparceljiankong',
            name='last_checked_at',
            field=models.DateTimeField(default=datetime.datetime.now, null=True, blank=True),
            preserve_default=True,
        ),
    ]

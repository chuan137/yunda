# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('jiankong', '0003_auto_20151130_0219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intlparceljiankong',
            name='last_checked_at',
            field=models.DateTimeField(default=datetime.datetime(1998, 8, 8, 8, 8, 8)),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jiankong', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='intlparceljiankong',
            name='last_checked_at',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]

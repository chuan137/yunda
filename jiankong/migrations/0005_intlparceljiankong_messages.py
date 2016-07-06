# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('jiankong', '0004_auto_20151130_0307'),
    ]

    operations = [
        migrations.AddField(
            model_name='intlparceljiankong',
            name='messages',
            field=jsonfield.fields.JSONField(null=True, blank=True),
            preserve_default=True,
        ),
    ]

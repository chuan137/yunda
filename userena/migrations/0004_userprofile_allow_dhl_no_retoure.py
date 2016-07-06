# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userena', '0003_userprofile_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='allow_dhl_no_retoure',
            field=models.NullBooleanField(default=False),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parcel', '0001_initial'),
        ('userena', '0002_userprofile_is_synced'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='level',
            field=models.ForeignKey(to='parcel.Level', null=True),
            preserve_default=True,
        ),
    ]

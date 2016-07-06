# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parcel', '0002_parceltype_not_show_to_all'),
    ]

    operations = [
        migrations.RenameField(
            model_name='parceltype',
            old_name='not_show_to_all',
            new_name='show_to_all',
        ),
    ]

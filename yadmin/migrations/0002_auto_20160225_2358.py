# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('yadmin', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='despositentry',
            name='approved_at',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='despositentry',
            name='approved_by',
            field=models.ForeignKey(related_name='despositentry.approved_by', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]

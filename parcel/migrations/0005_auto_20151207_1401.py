# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import parcel.models


class Migration(migrations.Migration):

    dependencies = [
        ('parcel', '0004_auto_20151013_2348'),
    ]

    operations = [
        migrations.AddField(
            model_name='intlparcel',
            name='export_proof_printed_at',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='intlparcel',
            name='exported_at',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='intlparcel',
            name='mawb',
            field=models.ForeignKey(related_name='mawbs', blank=True, to='parcel.Mawb', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mawb',
            name='number',
            field=models.CharField(max_length=20, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mawb',
            name='mawb_number',
            field=models.CharField(unique=True, max_length=20, verbose_name=b'Name', validators=[parcel.models.field_validator_only_alphabeta_num]),
            preserve_default=True,
        ),
    ]

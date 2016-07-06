# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Sequence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(unique=True, max_length=30)),
                ('next_value', models.BigIntegerField(default=1)),
                ('interval', models.PositiveSmallIntegerField(default=1)),
                ('last_datetime', models.DateTimeField(default=datetime.datetime(2015, 3, 16, 14, 44, 1, 699027))),
                ('renew_type', models.CharField(max_length=1, choices=[(b'N', 'None'), (b'Y', 'By year'), (b'M', 'By Month'), (b'D', 'By Day')])),
                ('prefix', models.CharField(help_text='Year-%y/%Y, Month-%m, Day-%d', max_length=50, blank=True)),
                ('suffix', models.CharField(help_text='Year-%y/%Y, Month-%m, Day-%d', max_length=50, blank=True)),
                ('digit_length', models.SmallIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(default=b'default', unique=True, max_length=10)),
                ('eur_to_cny_rate', models.FloatField(default=7.2)),
                ('currency_change_margin', models.FloatField(default=0.05)),
                ('dhl_retoure_price_eur', models.FloatField(default=3.9)),
                ('deposit_short_fee_eur', models.FloatField(default=3)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

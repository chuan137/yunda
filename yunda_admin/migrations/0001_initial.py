# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DepositEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('customer_number', models.CharField(max_length=20)),
                ('deposit_currency_type', models.CharField(help_text=b'Will be change to EUR', max_length=3, verbose_name='Deposit currency type', choices=[(b'eur', 'EUR'), (b'cny', 'CNY')])),
                ('amount', models.FloatField()),
                ('internal_id', models.CharField(max_length=20)),
                ('transfer_prove_image', models.BinaryField(null=True)),
                ('transfer_prove_image_file_type', models.CharField(max_length=5, null=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2015, 3, 16, 14, 44, 1, 756606))),
                ('verified_at', models.DateTimeField(null=True)),
                ('bank_arrived_at', models.DateTimeField(null=True)),
                ('bank_arrived_verified_at', models.DateTimeField(null=True)),
                ('bank_arrived_set_by', models.ForeignKey(related_name='DepositEntry.bank_arrived_set_by', to=settings.AUTH_USER_MODEL, null=True)),
                ('bank_arrived_verified_by', models.ForeignKey(related_name='DepositEntry.bank_arrived_verified_by', to=settings.AUTH_USER_MODEL, null=True)),
                ('created_by', models.ForeignKey(related_name='DepositEntry.created_by', to=settings.AUTH_USER_MODEL)),
                ('verified_by', models.ForeignKey(related_name='DepositEntry.verified_by', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DepositWithdraw',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('customer_number', models.CharField(max_length=20)),
                ('deposit_currency_type', models.CharField(help_text=b'Will be change to EUR', max_length=3, verbose_name='Deposit currency type', choices=[(b'eur', 'EUR')])),
                ('amount', models.FloatField()),
                ('internal_id', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2015, 3, 16, 14, 44, 1, 758435))),
                ('verified_at', models.DateTimeField(null=True)),
                ('created_by', models.ForeignKey(related_name='DepositWithdraw.created_by', to=settings.AUTH_USER_MODEL)),
                ('verified_by', models.ForeignKey(related_name='DepositWithdraw.verified_by', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

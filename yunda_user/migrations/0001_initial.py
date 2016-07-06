# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='Branch name')),
                ('code', models.CharField(unique=True, max_length=8, verbose_name='Code')),
                ('branch_number', models.CharField(max_length=6, verbose_name='Branch number', blank=True)),
                ('company', models.CharField(max_length=50, verbose_name='Company', blank=True)),
                ('street', models.CharField(max_length=50, verbose_name='Street')),
                ('hause_number', models.CharField(max_length=10, verbose_name='Hause number', blank=True)),
                ('street_add', models.CharField(max_length=50, verbose_name='Addtion', blank=True)),
                ('postcode', models.CharField(max_length=10, verbose_name='Postcode')),
                ('city', models.CharField(max_length=20, verbose_name='City')),
                ('state', models.CharField(max_length=20, verbose_name='State', blank=True)),
                ('country_code', models.CharField(max_length=2, verbose_name='Country', choices=[(b'DE', 'Germany'), (b'CN', 'China'), (b'HK', 'Hongkong'), (b'TW', 'Taiwan'), (b'MO', 'Macau')])),
                ('tel', models.CharField(max_length=20, verbose_name='Telphone')),
                ('fax', models.CharField(max_length=20, verbose_name='Fax', blank=True)),
                ('vat_id', models.CharField(max_length=20, verbose_name='Vat ID', blank=True)),
                ('register_number', models.CharField(max_length=30, verbose_name='Register number', blank=True)),
                ('is_active', models.BooleanField(default=False, verbose_name='Is Active')),
                ('is_default', models.BooleanField(default=False)),
                ('super_user', models.ForeignKey(related_name='Branch.super_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DepositTransfer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(verbose_name='Created at')),
                ('amount', models.FloatField(verbose_name='Amount')),
                ('type', models.CharField(max_length=30, verbose_name='Type', choices=[(b'deposit_entry', 'deposit entry'), (b'deposit_withdraw', 'deposit withdraw'), (b'parcel_payment', 'Parcel payment'), (b'parcel_canceled', 'Parcel canceled'), (b'customs_payment', 'Customs payment'), (b'customs_pay_back', 'Customs pay_back'), (b'retoure_label_payment', 'Retoure label payment'), (b'others', 'Others')])),
                ('ref', models.CharField(max_length=50, verbose_name='Reference', blank=True)),
                ('operator', models.ForeignKey(related_name='FundTransfer.operator', to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InvoiceHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(verbose_name='Created at')),
                ('amount', models.FloatField(verbose_name='Amount')),
                ('type', models.CharField(max_length=30, verbose_name='Type', choices=[(b'parcel', 'Parcel'), (b'retoure_labbel', 'Retoure label'), (b'cn_tax', 'CN tax'), (b'others', 'Others')])),
                ('yde_number', models.CharField(max_length=30, blank=True)),
                ('tracking_number', models.CharField(max_length=30, blank=True)),
                ('is_refound', models.BooleanField(default=False)),
                ('is_invoiced', models.BooleanField(default=False)),
                ('invoice_number', models.CharField(max_length=30, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StaffProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('staff_number', models.CharField(max_length=10, verbose_name='Staff number', blank=True)),
                ('branch', models.ForeignKey(to='yunda_user.Branch', null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

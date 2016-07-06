# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yunda_user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserenaSignup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_active', models.DateTimeField(help_text='The last date that the user was active.', null=True, verbose_name='last active', blank=True)),
                ('activation_key', models.CharField(max_length=40, verbose_name='activation key', blank=True)),
                ('activation_notification_send', models.BooleanField(default=False, help_text='Designates whether this user has already got a notification about activating their account.', verbose_name='notification send')),
                ('email_unconfirmed', models.EmailField(help_text='Temporary email address when the user requests an email change.', max_length=75, verbose_name='unconfirmed email address', blank=True)),
                ('email_confirmation_key', models.CharField(max_length=40, verbose_name='unconfirmed email verification key', blank=True)),
                ('email_confirmation_key_created', models.DateTimeField(null=True, verbose_name='creation date of email confirmation key', blank=True)),
                ('user', models.OneToOneField(related_name='userena_signup', verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'userena registration',
                'verbose_name_plural': 'userena registrations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('privacy', models.CharField(default=b'closed', help_text='Designates who can view your profile.', max_length=15, verbose_name='privacy', choices=[(b'open', 'Open'), (b'registered', 'Registered'), (b'closed', 'Closed')])),
                ('customer_number', models.CharField(max_length=10, verbose_name='Customer number', blank=True)),
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
                ('deposit_currency_type', models.CharField(help_text=b'Will be change to EUR', max_length=3, verbose_name='Deposit currency type', choices=[(b'eur', 'EUR'), (b'cny', 'CNY')])),
                ('current_deposit', models.FloatField(default=0, verbose_name='Current deposit (EUR)')),
                ('credit', models.FloatField(default=0, verbose_name='Credit (EUR)')),
                ('branch', models.ForeignKey(blank=True, to='yunda_user.Branch', null=True)),
                ('salesman', models.ForeignKey(related_name='UserProfile.salesman', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.OneToOneField(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'permissions': (('view_profile', 'Can view profile'),),
            },
            bases=(models.Model,),
        ),
    ]

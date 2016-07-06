# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import yunda_parcel.models
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yunda_parcel', '0003_auto_20151011_1847'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReceiverTemplateTmp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('yid', models.CharField(max_length=b'40', verbose_name='YID', blank=True)),
                ('yde_number', models.CharField(max_length=15, verbose_name='YDE number', blank=True)),
                ('receiver_name', models.CharField(max_length=50, verbose_name='Receiver name', validators=[yunda_parcel.models.field_validator_only_chinese])),
                ('receiver_company', models.CharField(default=b'', max_length=50, verbose_name='Receiver company', blank=True, validators=[yunda_parcel.models.field_validator_chinese_and_alphabeta])),
                ('receiver_province', models.CharField(max_length=20, verbose_name='Receiver province', validators=[yunda_parcel.models.field_validator_only_chinese])),
                ('receiver_city', models.CharField(default=b'', max_length=20, verbose_name='Receiver city', blank=True, validators=[yunda_parcel.models.field_validator_only_chinese])),
                ('receiver_district', models.CharField(default=b'', max_length=20, verbose_name='Receiver district', blank=True, validators=[yunda_parcel.models.field_validator_only_chinese])),
                ('receiver_postcode', models.CharField(default=b'', max_length=6, verbose_name='Receiver postcode', validators=[yunda_parcel.models.field_validator_chinese_postcode])),
                ('receiver_address', models.CharField(max_length=50, verbose_name='Receiver address', validators=[yunda_parcel.models.field_validator_chinese_and_alphabeta])),
                ('receiver_address2', models.CharField(default=b'', max_length=50, verbose_name='Receiver address2', blank=True, validators=[yunda_parcel.models.field_validator_chinese_and_alphabeta])),
                ('receiver_mobile', models.CharField(max_length=11, verbose_name='Receiver mobilephone', validators=[yunda_parcel.models.field_validator_chinese_mobile_phone])),
                ('receiver_email', models.EmailField(default=b'', max_length=75, verbose_name='Receiver email', blank=True, validators=[django.core.validators.EmailValidator])),
                ('receiver_country', models.CharField(default=b'CN', max_length=2, verbose_name='Receiver country')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SenderTemplateTmp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('yid', models.CharField(max_length=b'40', verbose_name='YID', blank=True)),
                ('yde_number', models.CharField(max_length=15, verbose_name='YDE number', blank=True)),
                ('sender_name', models.CharField(max_length=25, verbose_name='Sender name', validators=[yunda_parcel.models.field_validator_only_alphabeta_num])),
                ('sender_name2', models.CharField(blank=True, max_length=25, verbose_name='Sender name2', validators=[yunda_parcel.models.field_validator_only_alphabeta_num])),
                ('sender_company', models.CharField(blank=True, max_length=25, verbose_name='Sender company', validators=[yunda_parcel.models.field_validator_only_alphabeta_num])),
                ('sender_state', models.CharField(blank=True, max_length=25, verbose_name='Sender state', validators=[yunda_parcel.models.field_validator_only_alphabeta_num])),
                ('sender_city', models.CharField(max_length=25, verbose_name='Sender city', validators=[yunda_parcel.models.field_validator_only_alphabeta_num])),
                ('sender_postcode', models.CharField(max_length=5, verbose_name='Sender postcode', validators=[yunda_parcel.models.field_validator_german_postcode])),
                ('sender_street', models.CharField(max_length=25, verbose_name='Sender street', validators=[yunda_parcel.models.field_validator_only_alphabeta_num])),
                ('sender_add', models.CharField(blank=True, max_length=25, verbose_name='Sender street addition', validators=[yunda_parcel.models.field_validator_only_alphabeta_num])),
                ('sender_hause_number', models.CharField(max_length=10, verbose_name='Sender hause number', validators=[yunda_parcel.models.field_validator_only_alphabeta_num])),
                ('sender_tel', models.CharField(max_length=15, verbose_name='Sender telephone')),
                ('sender_email', models.EmailField(blank=True, max_length=75, verbose_name='Sender email', validators=[django.core.validators.EmailValidator])),
                ('sender_country', models.CharField(default=b'DE', max_length=2, verbose_name='Sender country')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='sendertemplatetmp',
            unique_together=set([('user', 'sender_name', 'sender_name2', 'sender_company', 'sender_state', 'sender_city', 'sender_postcode', 'sender_street', 'sender_add', 'sender_hause_number', 'sender_tel', 'sender_email')]),
        ),
        migrations.AlterUniqueTogether(
            name='receivertemplatetmp',
            unique_together=set([('user', 'receiver_name', 'receiver_company', 'receiver_province', 'receiver_city', 'receiver_district', 'receiver_postcode', 'receiver_address', 'receiver_address2', 'receiver_mobile', 'receiver_email')]),
        ),
    ]

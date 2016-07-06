# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yunda_user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DepositTransferNew',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, verbose_name='\u65f6\u95f4')),
                ('amount', models.FloatField(verbose_name='\u91d1\u989d')),
                ('origin', models.CharField(max_length=40, blank=True)),
                ('ref', models.TextField(verbose_name=b'Description', blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(verbose_name='\u65f6\u95f4')),
                ('number', models.CharField(max_length=20)),
                ('amount', models.FloatField(verbose_name='\u91d1\u989d')),
                ('pdf_file', models.BinaryField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

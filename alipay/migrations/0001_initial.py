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
            name='AlipayDepositOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('yid', models.CharField(max_length=10, blank=True)),
                ('amount', models.FloatField()),
                ('currency_type', models.CharField(default=b'eur', max_length=3)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('success_at', models.DateTimeField(null=True)),
                ('alipay_no', models.CharField(max_length=50, blank=True)),
                ('status', models.CharField(default=b'DRAFT', max_length=20)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

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
            name='DespositEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('yid', models.CharField(max_length=40, blank=True)),
                ('customer_number', models.CharField(max_length=10)),
                ('amount', models.FloatField()),
                ('origin', models.CharField(max_length=40, blank=True)),
                ('ref', models.CharField(max_length=50, verbose_name=b'Description', blank=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('approved_at', models.DateTimeField(null=True)),
                ('approved_by', models.ForeignKey(related_name='despositentry.approved_by', to=settings.AUTH_USER_MODEL, null=True)),
                ('created_by', models.ForeignKey(related_name='despositentry.created_by', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DespositWithdraw',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('yid', models.CharField(max_length=40, blank=True)),
                ('customer_number', models.CharField(max_length=10)),
                ('amount', models.FloatField()),
                ('origin', models.CharField(max_length=40, blank=True)),
                ('ref', models.CharField(max_length=50, verbose_name=b'Description', blank=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('approved_at', models.DateTimeField(null=True)),
                ('approved_by', models.ForeignKey(related_name='despositwithdraw.approved_by', to=settings.AUTH_USER_MODEL, null=True)),
                ('created_by', models.ForeignKey(related_name='despositwithdraw.created_by', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

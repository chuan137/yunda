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
            name='Messenge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, verbose_name='\u5efa\u7acb\u65f6\u95f4')),
                ('first_read_at', models.DateTimeField(null=True, verbose_name='\u67e5\u770b\u65f6\u95f4')),
                ('content', models.TextField(verbose_name='\u6d88\u606f\u5185\u5bb9')),
                ('created_by_stuff', models.NullBooleanField(verbose_name='\u7cfb\u7edf\u56de\u590d')),
                ('stuff_name', models.CharField(max_length=50, null=True, verbose_name=b'\xe5\xae\xa2\xe6\x9c\x8d\xe5\xa7\x93\xe5\x90\x8d')),
                ('sync_status', models.CharField(default=b'need_to_sync', max_length=30, verbose_name='\u540c\u6b65\u81f3ERP\u72b6\u6001', choices=[(b'need_to_sync', '\u9700\u8981\u540c\u6b65\u81f3ERP'), (b'waiting_to_sync', '\u7b49\u5f85\u540c\u6b65\u81f3ERP'), (b'synced', '\u5df2\u540c\u6b65\u81f3ERP')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('yid', models.CharField(max_length=b'40', blank=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, verbose_name='\u5efa\u7acb\u65f6\u95f4')),
                ('closed_at', models.DateTimeField(null=True, verbose_name='\u5b8c\u7ed3\u65f6\u95f4')),
                ('created_by_stuff', models.NullBooleanField(verbose_name='\u7cfb\u7edf\u901a\u77e5')),
                ('title', models.CharField(max_length=80, verbose_name='\u6807\u9898')),
                ('has_unread_messenge', models.BooleanField(default=False, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe6\x9c\x89\xe6\x9c\xaa\xe8\xaf\xbb\xe5\x9b\x9e\xe5\xa4\x8d')),
                ('has_staff_unread', models.BooleanField(default=True)),
                ('sync_status', models.CharField(default=b'need_to_sync', max_length=30, verbose_name='\u540c\u6b65\u81f3ERP\u72b6\u6001', choices=[(b'no_need_to_sync', '\u4e0d\u9700\u540c\u6b65\u81f3ERP'), (b'need_to_sync', '\u9700\u8981\u540c\u6b65\u81f3ERP'), (b'waiting_to_sync', '\u7b49\u5f85\u540c\u6b65\u81f3ERP'), (b'synced', '\u5df2\u540c\u6b65\u81f3ERP')])),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='messenge',
            name='subject',
            field=models.ForeignKey(related_name='messenges', to='messenge.Subject', null=True),
            preserve_default=True,
        ),
    ]

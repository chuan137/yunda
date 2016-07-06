# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cn_shenfenzheng.field_validator


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CnShenfengzheng',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.CharField(max_length=20, verbose_name='\u8eab\u4efd\u8bc1\u53f7\u7801', validators=[cn_shenfenzheng.field_validator.field_validator_cn_shenfenzheng])),
                ('name', models.CharField(max_length=20, verbose_name='\u59d3\u540d', validators=[cn_shenfenzheng.field_validator.field_validator_only_chinese])),
                ('mobile', models.CharField(max_length=15, verbose_name='\u624b\u673a\u53f7\u7801', validators=[cn_shenfenzheng.field_validator.field_validator_chinese_mobile_phone])),
                ('sync_status', models.CharField(default=b'need_to_sync', max_length=20, verbose_name='\u540c\u6b65\u81f3ERP\u72b6\u6001', choices=[(b'need_to_sync', '\u9700\u8981\u540c\u6b65\u81f3ERP'), (b'waiting_to_sync', '\u7b49\u5f85\u540c\u6b65\u81f3ERP'), (b'synced', '\u5df2\u540c\u6b65\u81f3ERP'), (b'error', '\u540c\u6b65\u8fc7\u7a0b\u51fa\u9519')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

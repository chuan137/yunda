# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parcel', '0006_auto_20151223_0054'),
    ]

    operations = [
        migrations.AddField(
            model_name='intlparcel',
            name='other_infos',
            field=jsonfield.fields.JSONField(default={}, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='batch',
            name='histories',
            field=jsonfield.fields.JSONField(default=[], null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='batch',
            name='total_value_per_sender',
            field=jsonfield.fields.JSONField(default={}, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='batch',
            name='yids',
            field=jsonfield.fields.JSONField(default=[], null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='goodsdetail',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='parcel.Product', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intlparcel',
            name='customs_code_forced',
            field=models.CharField(default=b'', max_length=20, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intlparcel',
            name='printed_at',
            field=models.DateTimeField(null=True, verbose_name='Printed at', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mawb',
            name='histories',
            field=jsonfield.fields.JSONField(default=[], null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mawb',
            name='receiver_name_mobiles',
            field=jsonfield.fields.JSONField(default=[], null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='product',
            name='cn_real_unit_tax_cny',
            field=jsonfield.fields.JSONField(default=[], null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='productbrand',
            name='histories',
            field=jsonfield.fields.JSONField(default=[], null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='productcategory',
            name='histories',
            field=jsonfield.fields.JSONField(default=[], null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='productmaincategory',
            name='histories',
            field=jsonfield.fields.JSONField(default=[], null=True, blank=True),
            preserve_default=True,
        ),
    ]

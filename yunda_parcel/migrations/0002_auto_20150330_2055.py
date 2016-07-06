# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import yunda_parcel.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('yunda_parcel', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='parcel',
            name='is_synced',
            field=models.NullBooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='parcel',
            name='receiver_country',
            field=models.CharField(default=b'CN', max_length=2, verbose_name='Receiver country'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dhlretourelabel',
            name='sender_hause_number',
            field=models.CharField(max_length=10, verbose_name='Sender hause number', validators=[yunda_parcel.models.field_validator_only_alphabeta_num]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='parcel',
            name='cn_tax_status',
            field=models.CharField(default=b'pr_cts_unpaid', max_length=60, choices=[(b'pr_cts_unpaid', 'Draft'), (b'pr_cts_sender_paid', 'Paid by sender'), (b'pr_cts_sender_pay_need_pay_rest', 'Need pay rest by sender'), (b'pr_cts_sender_pay_need_pay_rest_complete', 'Complete'), (b'pr_cts_sender_pay_complete', 'Complete'), (b'pr_cts_sender_pay_paid_back_complete', 'Complete'), (b'pr_cts_sender_pay_0tax', 'No Tax'), (b'pr_cts_sender_pay_0tax_need_pay_rest', 'Need pay'), (b'pr_cts_sender_pay_0tax_need_pay_rest_complete', 'Complete'), (b'pr_cts_sender_pay_0tax_rest_auto_paid_complete', 'Complete'), (b'pr_cts_receiver_pay', 'Receiver will pay'), (b'pr_cts_receiver_pay_need_pay', 'Need pay by receiver'), (b'pr_cts_receiver_pay_need_pay_complete', 'Complete'), (b'pr_cts_receiver_pay_0tax_complete', 'Complete'), (b'others', 'Others')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='parcel',
            name='height_cm',
            field=models.FloatField(verbose_name='Height (cm)', validators=[django.core.validators.MinValueValidator(0.01)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='parcel',
            name='length_cm',
            field=models.FloatField(verbose_name='Length (cm)', validators=[django.core.validators.MinValueValidator(0.01)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='parcel',
            name='payment_status',
            field=models.CharField(default=b'pr_pas_unpaid', max_length=60, choices=[(b'pr_pas_unpaid', 'Draft'), (b'pr_pas_paid', 'Paid'), (b'pr_pas_need_pay_rest', 'Need pay rest'), (b'pr_pas_need_pay_rest_complete', 'Complete'), (b'pr_pas_rest_auto_paid_complete', 'Complete'), (b'pr_pas_no_rest_complete', 'Complete'), (b'others', 'Others')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='parcel',
            name='position_status',
            field=models.CharField(default=b'pr_pos_sender', max_length=60, choices=[(b'pr_pos_sender', 'At sender'), (b'pr_pos_way_from_sender_to_op', 'Way from sender to operation center'), (b'pr_pos_op', 'At operation center'), (b'pr_pos_waiting_to_export', 'Waiting to export'), (b'pr_pos_flied', 'Flied'), (b'pr_pos_destination_customs', 'At destination customs'), (b'pr_pos_destination_yunda', 'At destination yunda'), (b'pr_pos_canceled', 'Canceled'), (b'others', 'Others')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='parcel',
            name='receiver_postcode',
            field=models.CharField(blank=True, max_length=6, verbose_name='Receiver postcode', validators=[yunda_parcel.models.field_validator_chinese_postcode]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='parcel',
            name='sender_country',
            field=models.CharField(default=b'DE', max_length=2, verbose_name='Sender country'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='parcel',
            name='sender_hause_number',
            field=models.CharField(max_length=10, verbose_name='Sender hause number', validators=[yunda_parcel.models.field_validator_only_alphabeta_num]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='parcel',
            name='weight_kg',
            field=models.FloatField(verbose_name='Weight (kg)', validators=[django.core.validators.MinValueValidator(0.01)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='parcel',
            name='width_cm',
            field=models.FloatField(verbose_name='Width (cm)', validators=[django.core.validators.MinValueValidator(0.01)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='parcel',
            name='yde_number',
            field=models.CharField(max_length=15, verbose_name='YDE number', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='parceldetail',
            name='item_net_weight_kg',
            field=models.FloatField(verbose_name='Item net weight (KG)', validators=[django.core.validators.MinValueValidator(0.01)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='parceldetail',
            name='item_price_eur',
            field=models.FloatField(verbose_name='Item price (EUR)', validators=[django.core.validators.MinValueValidator(0.01)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='parceldetail',
            name='parcel',
            field=models.ForeignKey(related_name='details', to='yunda_parcel.Parcel'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='parceldetail',
            name='qty',
            field=models.FloatField(verbose_name='Qty', validators=[django.core.validators.MinValueValidator(0.01)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='receivertemplate',
            name='receiver_postcode',
            field=models.CharField(blank=True, max_length=6, verbose_name='Receiver postcode', validators=[yunda_parcel.models.field_validator_chinese_postcode]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sendertemplate',
            name='sender_hause_number',
            field=models.CharField(max_length=10, verbose_name='Sender hause number', validators=[yunda_parcel.models.field_validator_only_alphabeta_num]),
            preserve_default=True,
        ),
    ]

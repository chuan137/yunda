# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yunda_parcel', '0004_auto_20151011_2042'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='receivertemplate',
            unique_together=set([('user', 'receiver_name', 'receiver_company', 'receiver_province', 'receiver_city', 'receiver_district', 'receiver_postcode', 'receiver_address', 'receiver_address2', 'receiver_mobile', 'receiver_email')]),
        ),
        migrations.AlterUniqueTogether(
            name='sendertemplate',
            unique_together=set([('user', 'sender_name', 'sender_name2', 'sender_company', 'sender_state', 'sender_city', 'sender_postcode', 'sender_street', 'sender_add', 'sender_hause_number', 'sender_tel', 'sender_email')]),
        ),
    ]

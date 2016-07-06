# -*- coding: utf-8 -*-
from django.db import models
from cn_shenfenzheng import field_validator


# Create your models here.
class CnShenfengzheng(models.Model):
    number = models.CharField(u'身份证号码', max_length=20, validators=[field_validator.field_validator_cn_shenfenzheng])
    name = models.CharField(u'姓名', max_length=20, validators=[field_validator.field_validator_only_chinese])
    mobile = models.CharField(u'手机号码', max_length=15, validators=[field_validator.field_validator_chinese_mobile_phone])
    SYNC_STATUSES=(
            ('need_to_sync', u'需要同步至ERP'),
            ('waiting_to_sync', u'等待同步至ERP'),
            ('synced', u'已同步至ERP'),
            ('error', u'同步过程出错'),
            )
    sync_status = models.CharField(u'同步至ERP状态',max_length=20, choices=SYNC_STATUSES, default="need_to_sync")
    # shenfenzheng1 = models.ImageField(upload_to='sfz')
    def __unicode__(self):
        return u"%s-%s-%s" % (self.name, self.mobile, self.number)

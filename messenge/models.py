# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
import hashlib
from django.conf import settings
from yunda_commen.commen_tasks import send_email

# from warehause.models import Warehause

# Create your models here.
class Subject(models.Model):
    user = models.ForeignKey(User)
    yid = models.CharField(max_length="40", blank=True)
    created_at = models.DateTimeField(u'建立时间', default=datetime.now)
    closed_at = models.DateTimeField(u"完结时间", null=True)
    created_by_stuff = models.NullBooleanField(u"系统通知")
    title = models.CharField(u'标题', max_length=80)
    has_unread_messenge = models.BooleanField("是否有未读回复", default=False)
    has_staff_unread=models.BooleanField(default=True)
    
    SYNC_STATUSES = (
            ('no_need_to_sync', u'不需同步至ERP'),
            ('need_to_sync', u'需要同步至ERP'),
            ('waiting_to_sync', u'等待同步至ERP'),
            ('synced', u'已同步至ERP'),
            )
    sync_status = models.CharField(u'同步至ERP状态', max_length=30, choices=SYNC_STATUSES, default="need_to_sync")
#     def get_warehause_name(self):
#         warehause = get_object_or_404(Warehause, code=self.warehause_code)
#         return warehause.name
    def is_closed(self):
        return self.closed_at and True or False
class Messenge(models.Model):
    subject = models.ForeignKey(Subject, null=True, related_name='messenges')
    created_at = models.DateTimeField(u'建立时间', default=datetime.now)
    first_read_at = models.DateTimeField(u'查看时间', null=True)
    content = models.TextField(u'消息内容')
    created_by_stuff = models.NullBooleanField(u"系统回复")
    stuff_name = models.CharField('客服姓名', max_length=50, null=True)
    SYNC_STATUSES = (
            ('need_to_sync', u'需要同步至ERP'),
            ('waiting_to_sync', u'等待同步至ERP'),
            ('synced', u'已同步至ERP'),
            )
    sync_status = models.CharField(u'同步至ERP状态', max_length=30, choices=SYNC_STATUSES, default="need_to_sync")
    def get_content(self):
        return self.content.replace('\n', '<br>')
    
def write_new_subject_to_customer(customer_id, title,content,stuff_name):
    subject=Subject.objects.create(user_id=customer_id,
                                   created_by_stuff=True,
                                   title=title,
                                   has_unread_messenge=True,
                                   has_staff_unread=False,
                                   )
    subject.yid = hashlib.md5("subject%d" % subject.id).hexdigest()
    subject.save()
    messenge=Messenge.objects.create(subject=subject,
                                     content=content,
                                     created_by_stuff=True,
                                     stuff_name=stuff_name,
                                     )
    email_subject=u"您有一个新工单等待处理：%s" % title
    email_content=u"亲，您好： <br>您有一个新工单，为尽量减小包裹延误，请尽快处理。<br><br>工单内容如下：<br><br>%s" % content
    email_content+=u"<br><br>回复请<a href='%s/ticket/detail/%s'>点击这里</a>（请勿直接回复邮件）。" % (getattr(settings, 'WEB_APP_ROOT_URL', "http://yunda-express.eu/de/index.html#"),
                                                                                                subject.yid)
    email_content+=u'''<br><br>祝：<br>商祺<br>韵达快递欧洲分公司
    <br>http://yunda-express.eu
    <br>QQ：2565697281
    <br>电话：06105 7178778
    <br>充值、下单：sales@yunda-express.eu
    <br>包裹调查：investigation@yunda-express.eu
    <br>投诉、客服主管：csd@yunda-express.eu
    <br>合作：cooperation@yunda-express.eu
    <br><br>通过安全、快捷的服务，传爱心、送温暖、更便利，
    <br>成为受人尊敬、值得信赖、服务更好的一流快递公司
'''
    send_email.delay(email_subject,email_content,user_id=customer_id)



        
    

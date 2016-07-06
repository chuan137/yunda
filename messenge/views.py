# -*- coding: utf-8 -*-
from userena.decorators import secure_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import string
import random
import math
# from warehause.models import Warehause
from django.db.models import Q
import pytz
from django.conf import settings
from yunda_commen.decorators import json_response
import hashlib
from django.contrib.admin.views.decorators import staff_member_required
from userena.models import UserProfile
from messenge import forms, models
from yunda_commen.commen_tasks import send_email

import logging
logger = logging.getLogger('django')

def random_str(randomlength=4):
    a = list(string.ascii_lowercase)
    random.shuffle(a)
    return ''.join(a[:randomlength])

company_code = getattr(settings, 'ODOO_COMPANY_CODE', '')

# Create your views here.


#######################################################################
# # angular 使用
#######################################################################
@json_response
@secure_required
@login_required
def json_post_subject(request):
    user_id = request.session.get('_auth_user_id')
    if request.method == 'POST':    
        subject_form = forms.SubjectForm(request.POST, request.FILES)
        messenge_form = forms.MessengeForm(request.POST, request.FILES)
        
        is_valid = True
        
        if not subject_form.is_valid():
            is_valid = False
            subject_errors = subject_form.errors
        if not messenge_form.is_valid():
            is_valid = False
            messenge_errors = messenge_form.errors
            
        if is_valid:
            subject = subject_form.save(commit=False)
            subject.user_id = user_id
            subject.created_by_stuff = False
            subject.save()
            subject.yid = hashlib.md5("subject%d" % subject.id).hexdigest()
            subject.has_staff_unread = True
            subject.save()
            
            messenge = messenge_form.save(commit=False)
            messenge.created_by_stuff = False
            messenge.subject = subject
            messenge.save()
                
            return dict(state="success",
                            yid=subject.yid)
        else:
            return dict(state='error',
                        subject_errors=subject_errors,
                        messenge_errors=messenge_errors)
            
            # user = form.save()  
    else:
        return dict(state='error-msg',
                    msg=u"未提交任何数据"
                    )

@json_response
@secure_required
@login_required
def json_post_messenge(request):
    user_id = request.session.get('_auth_user_id')
    if request.method == 'POST':
        messenge_form = forms.MessengeForm(request.POST, request.FILES)
        
        is_valid = True
        if not messenge_form.is_valid():
            is_valid = False
            messenge_errors = messenge_form.errors
            
        if is_valid:
            subject_yid = request.POST.get('yid', False)            
            if subject_yid:
                try:
                    subject = models.Subject.objects.get(user_id=user_id, yid=subject_yid, closed_at__isnull=True)
                    messenge = messenge_form.save(commit=False)
                    messenge.created_by_stuff = False
                    messenge.subject = subject
                    messenge.save()
                    subject.has_staff_unread = True
                    subject.save()
                    return dict(state='success',
                                yid=subject.yid)
                except models.Subject.DoesNotExist:
                    return dict(state='error-msg',
                                msg=u"该工单不存在或已经完结"
                                )
            else:
                return dict(state='error-msg',
                                msg=u"未提交工单号码"
                                )
        else:
            return dict(state='error',
                        messenge_errors=messenge_errors)
            
            # user = form.save()  
    else:
        return dict(state='error-msg',
                    msg=u"未提交任何数据"
                    )


def get_subject_info(subject, local=None):
    result = {}
    
    if not local:
        tz = getattr(settings, 'TIME_ZONE', 'Asia/Shanghai')
        local = pytz.timezone(tz)
            
    result['created_at'] = subject.created_at.astimezone(local).strftime("%Y-%m-%d %H:%M")
    result['closed_at'] = subject.closed_at and subject.closed_at.astimezone(local).strftime("%Y-%m-%d %H:%M") or ""
    result['is_closed'] = subject.is_closed()
    result['yid'] = subject.yid
    result['created_by_stuff'] = subject.created_by_stuff
    result['title'] = subject.title
    result['has_unread_messenge'] = subject.has_unread_messenge
    result['has_staff_unread'] = subject.has_staff_unread
    
    return result

@json_response
@secure_required
@login_required
def json_get_subject(request, yid):
    user_id = request.session.get('_auth_user_id')
    if yid:
        try:
            tz = getattr(settings, 'TIME_ZONE', 'Asia/Shanghai')
            local = pytz.timezone(tz)
            
            subject = models.Subject.objects.get(yid=yid, user_id=user_id)
            result = get_subject_info(subject, local)           
            
            messenges = []
            for messenge in subject.messenges.all():
                info = {
                    "created_at":messenge.created_at.astimezone(local).strftime("%Y-%m-%d %H:%M"),
                    "first_read_at":messenge.first_read_at and messenge.first_read_at.astimezone(local).strftime("%Y-%m-%d %H:%M") or "",
                    "content":messenge.get_content(),
                    "created_by_stuff":messenge.created_by_stuff or False,
                    "stuff_name":messenge.stuff_name or "",
                    }
                messenges.append(info)
            messenges = sorted(messenges, key=lambda k:k['created_at'], reverse=False)
            result['messenges'] = messenges
            if subject.has_unread_messenge:
                subject.has_unread_messenge = False
                subject.save()
            
            return {"state":'success', "subject":result}            
        except models.Subject.DoesNotExist:
            return dict(state="error", msg=u"未找到该工单")

@json_response
@secure_required
@login_required
def json_search_subject(request):
    user_id = request.session.get('_auth_user_id')
        
    if request.method == 'GET': 
        q = models.Subject.objects.filter(user_id=user_id)       
        page = int(request.GET.get('page', 1))
        rows = int(request.GET.get('rows', 10))
        
        s = request.GET.get('s', False)        
        if s:
            q = q.filter(title__contains=s)
        
        
        results = {}
        count = q.count()
        results['count'] = count or 0
        if count == 0:
            results['subjects'] = []
            return results
        last_page = int(math.ceil(float(count) / float(rows)))
        if page * rows > count:
            page = last_page
        
        start = (page - 1) * rows
        end = page * rows
        if end > count:
            end = count
        results['start'] = start
        results['end'] = end
        results['page'] = page
        results['rows'] = rows
        results['last_page'] = last_page   
        tz = getattr(settings, 'TIME_ZONE', 'Asia/Shanghai')
        local = pytz.timezone(tz)
        results['subjects'] = []
        for subject in q.order_by('-has_unread_messenge', '-created_at')[start:end]:
            results['subjects'].append(get_subject_info(subject, local))
        
        return results


@json_response
@secure_required
@staff_member_required
def admin_json_get_subject(request, yid):
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)       
    if yid:
        try:
            tz = getattr(settings, 'TIME_ZONE', 'Asia/Shanghai')
            local = pytz.timezone(tz)
            
            subject = models.Subject.objects.get(yid=yid)
            result = get_subject_info(subject, local)
            result['customer_number'] = subject.user.userprofile.customer_number
            result['customer_name'] = subject.user.get_full_name() or subject.user.email           
            
            messenges = []
            for messenge in subject.messenges.all():
                info = {
                    "created_at":messenge.created_at.astimezone(local).strftime("%Y-%m-%d %H:%M"),
                    "first_read_at":messenge.first_read_at and messenge.first_read_at.astimezone(local).strftime("%Y-%m-%d %H:%M") or "",
                    "content":messenge.get_content(),
                    "created_by_stuff":messenge.created_by_stuff or False,
                    "stuff_name":messenge.stuff_name or "",
                    }                
                messenges.append(info)
            messenges = sorted(messenges, key=lambda k:k['created_at'], reverse=False)
            result['messenges'] = messenges
#             if subject.has_staff_unread:
#                 subject.has_staff_unread=False
#                 subject.save()
            
            return {"state":'success', "subject":result}            
        except models.Subject.DoesNotExist:
            return dict(state="error", msg=u"No ticket found")

@json_response
@secure_required
@staff_member_required
def admin_json_post_subject(request):
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)
    if request.method == 'POST':    
        subject_form = forms.AdminSubjectForm(request.POST, request.FILES)
        messenge_form = forms.MessengeForm(request.POST, request.FILES)
        
        is_valid = True
        
        if not subject_form.is_valid():
            is_valid = False
            subject_errors = subject_form.errors
        if not messenge_form.is_valid():
            is_valid = False
            messenge_errors = messenge_form.errors
        
            
        if is_valid:
            try:
                customer = UserProfile.objects.get(customer_number=subject_form.cleaned_data['customer_number'])
                
                subject = subject_form.save(commit=False)
                subject.user_id = customer.user.id
                subject.created_by_stuff = True
                subject.save()
                subject.yid = hashlib.md5("subject%d" % subject.id).hexdigest()
                subject.has_staff_unread = False
                subject.has_unread_messenge = True
                subject.save()
                
                messenge = messenge_form.save(commit=False)
                messenge.created_by_stuff = True
                messenge.subject = subject
                messenge.stuff_name = user.get_full_name()
                messenge.save()
                
                # ##send mail to customer
                email_subject = u"您有一个新工单等待处理：%s" % subject.title
                email_content = u"亲，您好： <br>您有一个新工单，请尽快处理。<br><br>工单内容如下：<br><br>%s" % messenge.content
                email_content += u"<br><br>回复请<a href='%s/ticket/detail/%s'>点击这里</a>（请勿直接回复邮件）。" % (getattr(settings, 'WEB_APP_ROOT_URL', "http://yunda-express.eu/de/index.html#"),
                                                                                                            subject.yid)
                email_content += u'''<br><br>祝：<br>商祺<br>韵达快递欧洲分公司
<br>http://yunda-express.eu
<br>QQ：2565697281
<br>电话：06105 7178778
<br>充值、下单：sales@yunda-express.eu
<br>包裹调查：investigation@yunda-express.eu
<br>投诉、客服主管：csd@yunda-express.eu
<br>合作：cooperation@yunda-express.eu
<br><br>通过安全、快捷的服务，传爱心、送温暖、更便利，
<br>成为受人尊敬、值得信赖、服务更好的一流快递公司''' 
                send_email.delay(email_subject, email_content, to_emails=[customer.user.email])               
                # ## end send mail to customer
                return dict(state="success",
                                yid=subject.yid)
            except UserProfile.DoesNotExist:
                return dict(state='error-msg',
                            msg=u"Customer number does not exist"
                            )
            except Exception as e:
                logger.error(e)
                return dict(state='error-msg',
                            msg=e
                            )
        else:
            return dict(state='error',
                        subject_errors=subject_errors,
                        messenge_errors=messenge_errors)
            
            # user = form.save()  
    else:
        return dict(state='error-msg',
                    msg=u"No data submitted"
                    )

@json_response
@secure_required
@staff_member_required
def admin_json_post_messenge(request):
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        messenge_form = forms.MessengeForm(request.POST, request.FILES)
        
        is_valid = True
        if not messenge_form.is_valid():
            is_valid = False
            messenge_errors = messenge_form.errors
            
        if is_valid:
            subject_yid = request.POST.get('yid', False)            
            if subject_yid:
                try:
                    subject = models.Subject.objects.get(yid=subject_yid, closed_at__isnull=True)
                    messenge = messenge_form.save(commit=False)
                    messenge.created_by_stuff = True
                    messenge.subject = subject
                    messenge.stuff_name = user.get_full_name()
                    messenge.save()
                    subject.has_staff_unread = False
                    subject.has_unread_messenge = True
                    subject.save()
                    
                    # ##send mail to customer
                    email_subject = u"您收到一个客服回复 工单主题：%s" % subject.title
                    email_content = u"亲，您好： <br>工单主题：%s<br><br>您收到的客服回复内容如下：<br><br>%s" % (subject.title, messenge.content)
                    email_content += u"<br><br>查看工单全部内容或回复请<a href='%s/ticket/detail/%s'>点击这里</a>（请勿直接回复邮件）。" % (getattr(settings, 'WEB_APP_ROOT_URL', "http://yunda-express.eu/de/index.html#"),
                                                                                                                subject.yid)
                    email_content += u'''<br><br>祝：<br>商祺<br>韵达快递欧洲分公司
<br>http://yunda-express.eu
<br>QQ：2565697281
<br>电话：06105 7178778
<br>充值、下单：sales@yunda-express.eu
<br>包裹调查：investigation@yunda-express.eu
<br>投诉、客服主管：csd@yunda-express.eu
<br>合作：cooperation@yunda-express.eu
<br><br>通过安全、快捷的服务，传爱心、送温暖、更便利，
<br>成为受人尊敬、值得信赖、服务更好的一流快递公司'''
                    send_email.delay(email_subject, email_content, to_emails=[subject.user.email])                
                    # ## end send mail to customer
                    return dict(state='success',
                                yid=subject.yid)
                except models.Subject.DoesNotExist:
                    return dict(state='error-msg',
                                msg=u"Subject does not exist"
                                )
                except Exception as e:
                    logger.error(e)
                    return dict(state='error-msg',
                            msg=u"system error")

            else:
                return dict(state='error-msg',
                                msg=u"No ticket id submitted"
                                )
        else:
            return dict(state='error',
                        messenge_errors=messenge_errors)
            
            # user = form.save()  
    else:
        return dict(state='error-msg',
                    msg=u"No data submitted"
                    )

@json_response
@secure_required
@staff_member_required
def admin_json_search_subject(request):
    user_id = request.session.get('_auth_user_id')
        
    if request.method == 'GET': 
        q = models.Subject.objects      
        page = int(request.GET.get('page', 1))
        rows = int(request.GET.get('rows', 10))
        
        s = request.GET.get('s', False)        
        if s:
            q = q.filter(Q(title__contains=s) | 
                         Q(user__userprofile__customer_number__iexact=s)
                         )        
        results = {}
        count = q.count()
        results['count'] = count or 0
        if count == 0:
            results['subjects'] = []
            return results
        last_page = int(math.ceil(float(count) / float(rows)))
        if page * rows > count:
            page = last_page
        
        start = (page - 1) * rows
        end = page * rows
        if end > count:
            end = count
        results['start'] = start
        results['end'] = end
        results['page'] = page
        results['rows'] = rows
        results['last_page'] = last_page   
        tz = getattr(settings, 'TIME_ZONE', 'Asia/Shanghai')
        local = pytz.timezone(tz)
        results['subjects'] = []
        for subject in q.order_by('-has_staff_unread', '-created_at')[start:end]:
            info = get_subject_info(subject, local)
            info['customer_number'] = subject.user.userprofile.customer_number
            results['subjects'].append(info)
            
        
        return results

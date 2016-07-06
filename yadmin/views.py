from django.shortcuts import render
from yunda_commen.decorators import json_response
from userena.decorators import secure_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from yadmin.forms import DespositEntryForm
import hashlib
import re
from yadmin.models import DespositEntry
from datetime import datetime
from userena.models import UserProfile
from django.db.models import Q
import math
import pytz
from django.conf import settings
import logging
logger=logging.getLogger('django')

# Create your views here.

@json_response
@secure_required
def json_check_login(request):
    u_id = request.session.get('_auth_user_id')
    logger.debug(u_id)    
    if not u_id:
        return {'error':u'not loged in'}
    try:
        user = User.objects.get(id=u_id,is_staff=True)
        return {'logined':user.get_full_name()}
    except User.DoesNotExist:
        logger.error('Staff user does not exist')
        return {'error':u'Staff user does not exist'}

@json_response
@secure_required
@staff_member_required
def admin_json_post_deposit_entry(request):
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)
    
    if request.method == 'POST':
        form=DespositEntryForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                customer=UserProfile.objects.get(customer_number=form.cleaned_data['customer_number'],
                                                     user__is_active=True,
                                                     user__is_staff=False)
            except UserProfile.DoesNotExist:
                deposit_entry_errors={
                                      "customer_number":"Does not exist."
                                      }
                
                return dict(state="error",                            
                            deposit_entry_errors=deposit_entry_errors)
            
            
            de=form.save(commit=False)
            de.created_by_id=user_id
            de.save()
            de.yid= hashlib.md5("depositentry%d" % de.id).hexdigest()
            de.save()
            return dict(state="success",
                            yid=de.yid)
        else:
            return dict(state="error",
                            msg="Something wrong when input",
                            deposit_entry_errors=form.errors)

@json_response
@secure_required
@staff_member_required
def admin_json_approve_deposit_entry(request):
    user_id = request.session.get('_auth_user_id')    
    if request.method == 'POST':
        results=[]
        yids=request.POST.get('yids','')
        p = re.compile(u'^[a-zA-Z0-9\+]+$')
        if yids and p.match(yids):
            yids=yids.split('+')
            entries=DespositEntry.objects.filter(yid__in=yids, approved_at__isnull=True)
            for entry in entries:
                entry.approved_at=datetime.now()
                entry.approved_by_id=user_id
                entry.save()
                try:
                    customer=UserProfile.objects.get(customer_number=entry.customer_number,
                                                     user__is_active=True,
                                                     user__is_staff=False,)
                    customer.deposit_increase(entry.amount,entry.origin,entry.ref)
                    results.append(entry.yid)
                except:                    
                    entry.approved_at=None
                    entry.approved_by_id=None
                    entry.save()
        return results

@json_response
@secure_required
@staff_member_required
def admin_json_search_deposit_entry(request):
    user_id = request.session.get('_auth_user_id')
    
    if request.method == 'GET': 
        
        page = int(request.GET.get('page', 1))
        rows = int(request.GET.get('rows', 10))
        
        s = request.GET.get('s', False)
        approved=request.GET.get('approved', 'false')
        
        if approved and approved=="true":
            q=DespositEntry.objects.filter(approved_at__isnull=False)
        else:
            q=DespositEntry.objects.filter(approved_at__isnull=True)
        if s:
            q = q.filter(Q(customer_number__contains=s) | 
                           Q(amount__contains=s) | 
                           Q(origin__contains=s) | 
                           Q(ref__contains=s) 
                           )
        results = {}
        count = q.count()
        results['count'] = count or 0
        results['deposit_entries'] = []
        if count == 0:            
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
        for de in q.order_by('-created_at')[start:end]:
            results['deposit_entries'].append({
                'yid':de.yid,
                'customer_number':de.customer_number,
                'amount':de.amount,
                'origin':de.origin,
                'ref':de.ref,
                'created_at':de.created_at.astimezone(local).strftime("%Y-%m-%d %H:%M"),
                'created_by':de.created_by.get_full_name(),
                'approved_at':de.approved_at and de.approved_at.astimezone(local).strftime("%Y-%m-%d %H:%M") or False,
                'approved_by':de.approved_by and de.approved_by.get_full_name() or '',
                })
        
        return results           

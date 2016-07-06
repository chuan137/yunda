# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response, redirect,\
    get_object_or_404
from userena.decorators import secure_required
from yunda_commen.decorators import json_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from alipay import models, setting
import math
from django.conf import settings
import pytz
from django.db.models import Q
from django.template.context import RequestContext
import hashlib
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
import requests
from alipay.models import AlipayDepositOrder
from datetime import datetime
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from StringIO import StringIO
import logging
logger=logging.getLogger('django')


# Create your views here.

@secure_required
def alipay_return_url(request):
    if request.method == "GET":
        out_trade_no = request.GET.get('out_trade_no', False)
        currency = request.GET.get('currency', False)
        total_fee = request.GET.get('total_fee', False)
        trade_status = request.GET.get('trade_status', False)
        trade_no = request.GET.get('trade_no', False)
        sign = request.GET.get('sign', False)
        sign_type = request.GET.get('sign_type', False)
        
        if trade_status and out_trade_no:
            try:                
                (success,result)=alipay_single_trade_query(out_trade_no)                
                if success:
                    order=AlipayDepositOrder.objects.get(yid=out_trade_no)
                    if order.status=="DRAFT" and result['status']=="TRADE_CLOSED":
                        order.status="TRADE_CLOSED"
                        order.alipay_no=trade_no
                        order.save()
                    elif order.status=="DRAFT" and result['status']=="TRADE_FINISHED":
                        (deposit_success,msg)=order.user.userprofile.deposit_increase(order.amount, 
                                                                          order.yid, 
                                                                          u"支付宝充值. 流水号#: %(yid)s, 支付宝流水号#: %(alipay_no)s" % {'yid':order.yid,'alipay_no':result['alipay_no']})
                        if deposit_success:
                            order.alipay_no=trade_no
                            order.success_at=datetime.now()
                            order.status="TRADE_FINISHED"
                            order.save()
            except Exception as e:
                print e #TODO
        
        if trade_status=="TRADE_FINISHED":
            redirect_to = setting.ALIPAY_URL_AFTER_RETURN+"true"
        else:
            redirect_to = setting.ALIPAY_URL_AFTER_RETURN+"false"
        return redirect(redirect_to)
        

@secure_required
@csrf_exempt
def alipay_notify_url(request):
    if request.method == "POST":
        notify_type = request.POST.get('notify_type', False)
        notify_id = request.POST.get('notify_id', False)
        notify_time = request.POST.get('notify_time', False)
        sign = request.POST.get('sign', False)
        _input_charset = request.POST.get('_input_charset', False)
        sign_type = request.POST.get('sign_type', False)
        out_trade_no = request.POST.get('out_trade_no', False)
        trade_status = request.POST.get('trade_status', False)
        trade_no = request.POST.get('trade_no', False)
        currency = request.POST.get('currency', False)
        total_fee = request.POST.get('total_fee', False)
        
        try:
            order=AlipayDepositOrder.objects.get(yid=out_trade_no)
            r=notify_verify(setting.ALIPAY_PARTNER, notify_id)
            
        except:
            pass
        
        
        return "success"

def get_accounting_checking_file():
    pass

def single_order_refund():
    pass

def cancel_single_oder_refund():
    pass

def get_currency_exchange_rate():
    pass

def alipay_single_trade_query(out_trade_no):
# alipay返回的xml数据：
# <?xml version="1.0" encoding="GBK"?>
# <alipay>
#     <is_success>T</is_success>
#     <request>
#         <param name="_input_charset">UTF-8</param>
#         <param name="service">single_trade_query</param>
#         <param name="partner">2088101122136241</param>
#         <param name="out_trade_no">100091865</param>
#     </request>
#     <response>
#         <trade>
#             <buyer_email>alipaytest20091@gmail.com</buyer_email>
#             <buyer_id>2088102000979107</buyer_id>
#             <discount>0.00</discount>
#             <flag_trade_locked>0</flag_trade_locked>
#             <gmt_create>2015-09-24 06:33:01</gmt_create>
#             <gmt_last_modified_time>2015-09-24 06:33:22</gmt_last_modified_time>
#             <gmt_payment>2015-09-24 06:33:22</gmt_payment>
#             <is_total_fee_adjust>F</is_total_fee_adjust>
#             <operator_role>B</operator_role>
#             <out_trade_no>100091865</out_trade_no>
#             <payment_type>18</payment_type>
#             <price>0.08</price>
#             <quantity>1</quantity>
#             <seller_email>overseas_kgtest@163.com</seller_email>
#             <seller_id>2088101122136241</seller_id>
#             <subject>Parcel fee</subject>
#             <to_buyer_fee>0.00</to_buyer_fee>
#             <to_seller_fee>0.08</to_seller_fee>
#             <total_fee>0.08</total_fee>
#             <trade_no>2015092400001000100080038061</trade_no>
#             <trade_status>TRADE_FINISHED</trade_status>
#             <use_coupon>F</use_coupon>
#         </trade>
#     </response>
#     <sign>7f20766f03ada56c65969a30d860aa1b</sign>
#     <sign_type>MD5</sign_type>
# </alipay>

    to_sign={
             "service":"single_trade_query",
             "partner":setting.ALIPAY_PARTNER,
             "_input_charset":"UTF-8",
             "out_trade_no":out_trade_no
        }
    sign=md5_sign(to_sign, setting.ALIPAY_KEY)
    to_sign['sign']=sign
    to_sign['sign_type']="MD5"
    try:
        r=requests.post(setting.ALIPAY_URL,to_sign)
        text = r.text.encode('ascii', 'xmlcharrefreplace')
        alipay = get_xml_root(r.text)
        
        if alipay.find('is_success').text=='T':
            return(True,{
                "alipay_no":alipay.find('response/trade/trade_no').text,
                "yid":alipay.find('response/trade/out_trade_no').text,
                "status":alipay.find('response/trade/trade_status').text,                
                         })
        else:
            return (False, alipay.find('error').text)
    except Exception as e:
        print e
        return (False,"SYSTEM_ERROR")
    
def get_xml_root(text):
    utf8_parser = ET.XMLParser(encoding='utf-8')
    tree = ET.parse(StringIO(text.encode('utf-8')), parser=utf8_parser)
    return tree.getroot()

def notify_verify(partner,notify_id):
    url=setting.ALIPAY_URL+"service=notify_verify&partner="+partner+"&notify_id="+notify_id
    try:
        r = requests.get(url)
        return r
    except:
        pass

@json_response
@secure_required
@login_required
def json_check_alipay_deposit_order(request):
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)
    if request.method == 'GET': 
        yid=request.GET.get('yid','').strip()
        if yid:
            try:
                (success,result)=alipay_single_trade_query(yid)                
                if success:
                    order=AlipayDepositOrder.objects.get(yid=yid)
                    if order.status=="DRAFT" and result['status']=="TRADE_CLOSED":
                        order.status="TRADE_CLOSED"
                        order.alipay_no=result['alipay_no']
                        order.save()
                        return {'status':'TRADE_CLOSED','alipay_no':result['alipay_no']}
                    elif order.status=="DRAFT" and result['status']=="TRADE_FINISHED":
                        (deposit_success,msg)=order.user.userprofile.deposit_increase(order.amount, 
                                                                          order.yid, 
                                                                          u"支付宝充值. 流水号#: %(yid)s, 支付宝流水号#: %(alipay_no)s" % {'yid':order.yid,'alipay_no':result['alipay_no']})
                        if deposit_success:
                            order.alipay_no=result['alipay_no']
                            order.success_at=datetime.now()
                            order.status="TRADE_FINISHED"
                            order.save()
                            return {'status':'TRADE_FINISHED','alipay_no':result['alipay_no']}
                        else:
                            logger.info(msg)
                            return {'status':'DRAFT','alipay_no':''}
                    else:
                        return {'status':order.status,'alipay_no':order.alipay_no or ''}
                else:
                    if result=="TRADE_NOT_EXIST":
                        return {'status':'TRADE_NOT_EXIST','alipay_no':''}
                    logger.warning('Not dealed alipay result:' + result)    
		    return False
            except Exception as e:
                logger.error(e)
                return False
        else:
            logger.warning('No yid for checking alipay order status')
            return False
    else:
        logger.info('Not get method')
        return False
                    
   
@json_response
@secure_required
@login_required
def json_search_alipay_deposit_order(request):
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)
    if request.method == 'GET': 
        q = models.AlipayDepositOrder.objects.filter(user_id=user_id)       
        page = int(request.GET.get('page', 1))
        rows = int(request.GET.get('rows', 10))
        
        s = request.GET.get('s', False)        
        if s:
            q = q.filter(Q(yid__contains=s)
                         | Q(alipay_no__contains=s)
                         )
        
        
        results = {}
        count = q.count()
        results['count'] = count or 0
        results['orders'] = []
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
        for order in q.order_by('-created_at')[start:end]:
            od = {
                "created_at":order.created_at.astimezone(local).strftime("%Y-%m-%d %H:%M"),
                "amount":"%.2f" % order.amount,
                "yid":order.yid,
                "currency_type":order.currency_type,
                "success_at":order.success_at and order.success_at.astimezone(local).strftime("%Y-%m-%d %H:%M") or "",
                "alipay_no":order.alipay_no,
                "status":order.status,                
                }
            results['orders'].append(od)
        results['currency_type'] = user.userprofile.deposit_currency_type
        return results


@secure_required
@login_required
def json_post_alipay_deposit_order(request):
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)
    if user.userprofile.deposit_currency_type == u"cny":
        return render_to_response('alipay/before_relocation_error.html',
                                   {'error':u'非常抱歉，我司采用国际支付宝进行收款，只能使用欧元进行结算。烦请重新注册扣款类型为欧元的账号。目前人民币结算只接受银行转账。'},
                                   context_instance=RequestContext(request))
    if request.method == 'POST':
        am = request.POST.get('amount')
        try:
            amount = float(am)
            order = models.AlipayDepositOrder.objects.create(
                user_id=user_id,
                amount=amount,
                )
            return_url = reverse('alipay_return_url')
            notify_url = reverse('alipay_notify_url')
            to_sign = dict(
                service="create_forex_trade",
                partner=setting.ALIPAY_PARTNER,
                notify_url=setting.ALIPAY_BASE_URL + notify_url,
                return_url=setting.ALIPAY_BASE_URL + return_url,
                subject="YUNDA express parcel fee",
                _input_charset="UTF-8",
                out_trade_no=order.yid,
                currency="EUR",
                total_fee="%.2f" % order.amount,
                )
            sign = md5_sign(to_sign, setting.ALIPAY_KEY)
            to_sign['sign'] = sign
            to_sign['sign_type'] = "MD5"
            return render_to_response('alipay/before_relocation.html',
                                               {'to_sign':to_sign, 
                                                'gateway_url':setting.ALIPAY_URL,
                                                'amount':order.amount,
                                                },
                                               context_instance=RequestContext(request))

        except ValueError as e:
            a = {'success':False,
                    'msg':u'输入必须为数字'
                    }
            return render_to_response('alipay/before_relocation_error.html',
                                               dict(),
                                               context_instance=RequestContext(request))
    else:
        yid=request.GET.get('yid','').strip()
        if yid:
            order=get_object_or_404(AlipayDepositOrder,yid=yid)
            return_url = reverse('alipay_return_url')
            notify_url = reverse('alipay_notify_url')
            to_sign = dict(
                service="create_forex_trade",
                partner=setting.ALIPAY_PARTNER,
                notify_url=setting.ALIPAY_BASE_URL + notify_url,
                return_url=setting.ALIPAY_BASE_URL + return_url,
                subject="YUNDA express parcel fee",
                _input_charset="UTF-8",
                out_trade_no=order.yid,
                currency="EUR",
                total_fee="%.2f" % order.amount,
                )
            sign = md5_sign(to_sign, setting.ALIPAY_KEY)
            to_sign['sign'] = sign
            to_sign['sign_type'] = "MD5"
            return render_to_response('alipay/before_relocation.html',
                                               {'to_sign':to_sign, 
                                                'gateway_url':setting.ALIPAY_URL,
                                                'amount':order.amount,
                                                },
                                               context_instance=RequestContext(request))
        else:
            return render_to_response('alipay/before_relocation_error.html',
                                               dict(),
                                               context_instance=RequestContext(request))
def md5_sign(to_sign, alipay_key):
    strings=[]
    for key in sorted(to_sign.iterkeys()):
        strings.append("%s=%s" % (key, to_sign[key]))
    to_sign_string="&".join(strings)
    return hashlib.md5(to_sign_string + alipay_key).hexdigest()
        
        

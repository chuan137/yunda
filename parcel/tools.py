# -*- coding: utf-8 -*-
from yunda_parcel.lbl_retoure_label import Dhl_Retoure
from yunda_commen.commen_utils import get_seq_by_code
from datetime import datetime
from parcel.models import Gss
import base64
import requests
import xml.etree.ElementTree as ET
from django.core.mail import send_mail
import math
import hashlib
from django.conf import settings
import logging
from django.utils.datetime_safe import strftime
logger = logging.getLogger('django')

def create_retoure_label(ref, parcel):
    name = (parcel.sender_name or "") + u" " + (parcel.sender_name2 or "") + u" " + (parcel.sender_company or "")
    if len(name) < 51:
        firstname = name
        lastname = ""
    else:
        firstname = name[0:50]
        lastname = name[50:100]
    
    attributes, pdf = Dhl_Retoure.getLabel(firstname, lastname, parcel.sender_street, parcel.sender_hause_number, \
                                          parcel.sender_postcode, parcel.sender_city, ref)
    return attributes, pdf

def get_parcel_numbers(parcel):
    result = {}
    # 韵达 不含回邮单
    if parcel.type.code in ["yd", "yd-nf", "yd-xzx"]:
        result = gss_create_tracking_number(parcel)
        if result:
            result['retoure_tracking_number'] = ''
            result['retoure_routing_code'] = ''
            result['yid'] = parcel.yid
            result['success'] = True
            return result
        else:
            # 未生成追踪号，退款
            result = {}
            result['yid'] = parcel.yid
            result['yde_number'] = parcel.yde_number
            result['success'] = False
            result['msg'] = u"韵达中心出单系统繁忙或者正在维护，请稍候再试"
            return result
            
    # 韵达含回邮单
    elif parcel.type.code in ["yd-retoure", "yd-retoure-nf","yd-retoure-xzx"]:
        attributes, pdf = create_retoure_label(parcel.yde_number, parcel)
        logger.debug(attributes)
        if not attributes:
            logger.debug(pdf)
        if attributes:
            result = gss_create_tracking_number(parcel)
            if result:
                result['retoure_tracking_number'] = attributes['idc']
                result['retoure_routing_code'] = attributes['routingCode']                           
                result['yid'] = parcel.yid
                result['success'] = True
                return result
            else:
                result['yid'] = parcel.yid
                result['yde_number'] = parcel.yde_number
                result['success'] = False
                result['msg'] = u"韵达中心出单系统繁忙或者正在维护，请稍候再试"
                return result                                        
        else:
            result['yid'] = parcel.yid
            result['yde_number'] = parcel.yde_number
            result['success'] = False
            result['msg'] = u"德国邮政回邮单系统繁忙或者正在维护，请稍候再试"
            return result
    # dhl包裹 不含回邮单
    elif parcel.type.code in ['dhl-pre', 'dhl-eco']:
        tn = get_seq_by_code('dhl', True)
        result = {'tracking_number':tn,
                'yid':parcel.yid,
                'success': True,
                'yde_number':parcel.yde_number,
                'retoure_tracking_number':'',
                'retoure_routing_code':'',
                'pdf_info':'',
                }
        return result
    
    # dhl包裹 含回邮单
    elif parcel.type.code in ['dhl-pre-retoure', 'dhl-eco-retoure']:
        attributes, pdf = create_retoure_label(parcel.yde_number, parcel)
        if attributes:
            tn = get_seq_by_code('dhl', True)
            return {
                    'tracking_number':tn,
                    'yid':parcel.yid,
                    'yde_number':parcel.yde_number,
                    'retoure_tracking_number':attributes['idc'],
                    'retoure_routing_code':attributes['routingCode'],
                    'pdf_info':'',
                    'success': True,
                    }
        else:
            return {
                    'success':False,
                    'yid':parcel.yid,
                    'yde_number':parcel.yde_number,
                    'msg':u"德国邮政回邮单系统繁忙或者正在维护，请稍候再试"
                                 }
            
    
    # postnl包裹 不含回邮单
    elif parcel.type.code == 'postnl':
        return {
                    'success':False,
                    'yid':parcel.yid,
                    'yde_number':parcel.yde_number,
                    'msg':u"暂时无法出单，请稍候再试"
                                 }
    
    # postnl包裹 含回邮单
    elif parcel.type.code == 'postnl-retoure':
        return {
                    'success':False,
                    'yid':parcel.yid,
                    'yde_number':parcel.yde_number,
                    'msg':u"暂时无法出单，请稍候再试"
                                 }

def gss_create_tracking_number(parcel):
    results = _gss_create_tracking_number([parcel], parcel.get_cn_customs())
    if results:
        return results[0]
    else:
        return False
    
    

def _gss_create_tracking_number(parcels, cn_customs_code='default'):          
    if not cn_customs_code:cn_customs_code = 'default'
    
    try:
        gss = Gss.objects.get(cn_customs_code=cn_customs_code)
    except:
        gss = Gss.objects.get(cn_customs_code='default')
    
    results = []
    if not parcels:
        return results
    
    if getattr(settings, 'BYPASS_AUTO_YUNDA_MAILNO', False):
        for parcel in parcels:
            results.append({'yde_number':parcel.yde_number, 'pdf_info':"", 'tracking_number':""})
        return results
    
    req_data = u"<beans><req_type>create_order</req_type><hawbs>"
    for parcel in parcels:
        req_data += u"<hawb>"
        req_data += u"<mail_no></mail_no>"
        req_data += u"<hawbno>%s</hawbno>" % parcel.yde_number
        req_data += u"<pre_express></pre_express>"
        req_data += u"<next_express></next_express>"
        req_data += u"<fcountry>%s</fcountry>" % u"DE"  # TODO hawb['sender_country']
        req_data += u"<tcountry>%s</tcountry>" % u"CN"  # TODO hawb['receiver_country']
        req_data += u"<infor_origin>%s</infor_origin>" % gss.qr_traderId
        
        req_data += u"<receiver>"
        req_data += u"<company>%s</company>" % parcel.receiver_company or ""
        req_data += u"<contacts>%s</contacts>" % parcel.receiver_name or ""
        req_data += u"<city>%s%s%s</city>" % (parcel.receiver_province, parcel.receiver_city or '', parcel.receiver_district or '')
        req_data += u"<postal_code>%s</postal_code>" % parcel.receiver_postcode or ""
        ads=u"%s%s%s%s%s" % (parcel.receiver_province or '',
                                                 parcel.receiver_city or '',
                                                 parcel.receiver_district or '',
                                                 parcel.receiver_address or '',
                                                 parcel.receiver_address2 or "")
        req_data += u"<address>%s</address>" % ads[:45]
        req_data += u"<rec_tele>%s</rec_tele>" % parcel.receiver_mobile
        req_data += u"<e_mail>%s</e_mail>" % parcel.receiver_email or ''
        req_data += u"</receiver>"
        
        req_data += u"<sender>"
        req_data += u"<company>%s</company>" % parcel.sender_company or ""
        req_data += u"<city>%s</city>" % u"FRA"  # TODO Sender City
        req_data += u"<contacts>%s %s</contacts>" % (parcel.sender_name, parcel.sender_name2 or '')
        s_address = u"%s %s" % (parcel.sender_street, parcel.sender_hause_number)
        if parcel.sender_add:
            s_address += ", " + parcel.sender_add
        req_data += u"<address>%s</address>" % s_address
        req_data += u"<sender_tele>%s</sender_tele>" % parcel.sender_tel
        req_data += u"<postal_code>%s</postal_code>" % parcel.sender_postcode or ''
        req_data += u"<e_mail></e_mail>"
        req_data += u"</sender>"
        
        req_data += u"<insurance_fee>0</insurance_fee>"
        req_data += u"<goods_money>0</goods_money>"
        req_data += u"<certificate_id></certificate_id>"
        req_data += u"<currency>EUR</currency>"
        req_data += u"<request>%s</request>" % parcel.ref or ''
        req_data += u"<remark>%s</remark>" % parcel.yde_number           
        req_data += u"<vat_service></vat_service>"
        
        req_data += u"<goods_list>"
        req_data += u"<goods>"
        req_data += u"<name>presents</name>"
        req_data += u"<unit_price>1</unit_price>"
        req_data += u"<act_weight>1</act_weight>"
        req_data += u"<dim_weight>1</dim_weight>"
        req_data += u"<quantity>1</quantity>"
        req_data += u"</goods>"
        req_data += u"</goods_list>"
        req_data += u"</hawb>"
    req_data += u"</hawbs></beans>"
    req_data = base64.b64encode(req_data.encode('utf-8'))
    
    all_infor = {
               'traderId':gss.qr_traderId,
               'buz_type':gss.qr_buz_type,
               'version':gss.qr_version,
               'data_style':gss.qr_data_style,
               
               'validation':gss.qr_sign_infor,
               'data':req_data,
               }
    try:
        r = requests.post(gss.qr_api_url, data=all_infor)        
        logger.debug(r)
        logger.debug(r.content)
        text = r.text.encode('ascii', 'xmlcharrefreplace')
        tree = ET.fromstring(text)
           
        for response in tree:
            
            status = response.find('code').text
            msg = response.find('msg').text
            if status == 'E99':
                yde_number = response.find('hawbno').text
                pdf_info = response.find('pdf_info').text
                mailno = response.find('mail_no').text
                results.append({'yde_number':yde_number, 'pdf_info':pdf_info, 'tracking_number':mailno})
            else:
                # send mail
                send_mail(u"Error when create mail no bei GOS",
                  "",
                  u'Kuaidi DE <info@mail.yunda-express.eu>',
                  ['lik.li@yunda-express.eu'],
                  fail_silently=False,
                  html_message=u"%s: %s\nYDE Number: %s" % (status, msg, response.find('hawbno').text))
                results.append({'yde_number':response.find('hawbno').text, 'pdf_info':"", 'tracking_number':""})
                                
        return results
    except Exception as e:  
        logger.error(e)  
        # send mail
        send_mail(u"Connection Error when create mail no bei GOS",
              "",
              u'Kuaidi DE <info@mail.yunda-express.eu>',
              ['lik.li@yunda-express.eu'],
              fail_silently=False,
              html_message=e)
        return []
        

def cancel_parcel(hawbs, cn_customs_code):
    if not cn_customs_code:cn_customs_code = 'default'    
    try:
        gss = Gss.objects.get(cn_customs_code=cn_customs_code)
    except:
        gss = Gss.objects.get(cn_customs_code='default')
    
    results = []
    if not hawbs:
        return results
    req_data = u"<beans><req_type>cancel_order</req_type><hawbs>"
    for hawb in hawbs:
        req_data += u"<hawb>"
        
        if 'mail_no' in hawb:
            req_data += u"<mail_no>%s</mail_no>" % hawb['mail_no']
        if 'hawbno' in hawb:       
            req_data += u"<hawbno>%s</hawbno>" % hawb['hawbno']
        
        req_data += u"</hawb>"
    req_data += u"</hawbs></beans>"
    req_data = base64.b64encode(req_data.encode('utf-8'))
    
    
    all_infor = {
               'traderId':gss.qr_traderId,
               'buz_type':gss.qr_buz_type,
               'version':gss.qr_version,
               'data_style':gss.qr_data_style,
               
               'validation':gss.qr_sign_infor,
               'data':req_data,
               }
    try:
        r = requests.post(gss.qr_api_url, data=all_infor)
        
        text = r.text.encode('ascii', 'xmlcharrefreplace')
        tree = ET.fromstring(text)        
        for response in tree:
            
            status = response.find('code').text
            msg = response.find('msg').text
            if status == 'E99':
                yde_number = response.find('hawbno').text
                mailno = response.find('mail_no').text
                results.append({'yde_number':yde_number, 'tracking_number':mailno})
            else:
                # send mail
                send_mail(u"Error when cancel mail no bei GOS",
                  "",
                  u'Kuaidi DE <info@mail.yunda-express.eu>',
                  ['lik.li@yunda-express.eu'],
                  fail_silently=False,
                  html_message=u"%s: %s\nYDE Number: %s" % (status, msg, response.find('hawbno').text))
                                
        return results
    except Exception as e:    
        # send mail
        send_mail(u"Connection Error when cancel mail no bei GOS",
              "",
              u'Kuaidi DE <info@mail.yunda-express.eu>',
              ['lik.li@yunda-express.eu'],
              fail_silently=False,
              html_message=e)
        return []

def query_parcel_gss(mailno):
    req_data = u"<hawbs><hawb><mailno>%s</mailno></hawb></hawbs>" % mailno
    req_data = base64.b64encode(req_data.encode('utf-8'))
        
        
    all_infor = {
               'user_no':"301782001",
               'password':"thuK6palfPPVz+YFgOcjig==",
               'partner_no':"3017821001",
               'sign_mtd':"SIGN_MD5",
               'req_type':'query',
               'data_style':"xml",
               'version':"v1.0",
               'sign_infor':"e8f2bfc55b223197ba2625eede8b3197",
               'req_data':req_data,
               }
    try:
        results = []
        r = requests.post("http://gss.yundasys.com:11378/ydgss/qrcode/interface.jspx", data=all_infor)
        text = r.text.encode('ascii', 'xmlcharrefreplace')
        tree = ET.fromstring(text)
        for response in tree:
            
            status = response.find('code').text
            msg = response.find('msg').text
            if status == '1':
                results.append({  # 'yde_number':response.find('hawbno').text,
                                'tracking_number':response.find('hawbno').text,
                                'pdf_info':response.find('pdf_info').text,
                                'order_status':response.find('order_status').text,
                                })
            else:
                # send mail
                send_mail(u"Error when query mail no bei GOS",
                  "",
                  u'韵达德国 <info@mail.yunda-express.eu>',
                  ['lik.li@yunda-express.eu'],
                  fail_silently=False,
                  html_message=u"%s: %s\nYDE Number: %s" % (status, msg, response.find('hawbno').text))
                                
        return results
    except Exception as e:
        logger.error(e)
  

def query_parcel(hawbs, cn_customs_code=None):
    if not cn_customs_code:cn_customs_code = 'default'
    
    try:
        gss = Gss.objects.get(cn_customs_code=cn_customs_code)
    except:
        gss = Gss.objects.get(cn_customs_code='default')
    
    results = []
    if not hawbs:
        return results
        
    req_data = u"<beans><req_type>query_order</req_type><hawbs>"
    for hawb in hawbs:
        req_data += u"<hawb>"
        req_data += u"<mail_no>%s</mail_no>" % (hawb['mail_no'] or "")
        req_data += u"<hawbno>%s</hawbno>" % hawb['hawbno']
        
        req_data += u"</hawb>"
    req_data += u"</hawbs></beans>"
    req_data = base64.b64encode(req_data.encode('utf-8'))
    
    
    all_infor = {
               'traderId':gss.qr_traderId,
               'buz_type':gss.qr_buz_type,
               'version':gss.qr_version,
               'data_style':gss.qr_data_style,
               
               'validation':gss.qr_sign_infor,
               'data':req_data,
               }
    try:
        r = requests.post(gss.qr_api_url, data=all_infor)
    
        text = r.text.encode('ascii', 'xmlcharrefreplace')
        tree = ET.fromstring(text)
        for response in tree:
            
            status = response.find('code').text
            msg = response.find('msg').text
            if status == 'E99':
                results.append({  # 'yde_number':response.find('hawbno').text,
                                'tracking_number':response.find('mail_no').text,
                                'pdf_info':response.find('pdf_info').text,
                                'order_status':response.find('order_status').text,
                                })
            else:
                # send mail
                send_mail(u"Error when query mail no bei GOS",
                  "",
                  u'韵达德国 <info@mail.yunda-express.eu>',
                  ['lik.li@yunda-express.eu'],
                  fail_silently=False,
                  html_message=u"%s: %s\nYDE Number: %s" % (status, msg, response.find('hawbno').text))
                                
        return results
    except Exception as e:    
        # send mail
        send_mail(u"Connection Error when query mail no bei GOS",
              "",
              u'韵达德国 <info@mail.yunda-express.eu>',
              ['lik.li@yunda-express.eu'],
              fail_silently=False,
              html_message=e)
        return []

def tracking_push(scan_infos, cn_customs_code=None):
    if not cn_customs_code:cn_customs_code = 'default'    
    try:
        gss = Gss.objects.get(cn_customs_code=cn_customs_code)
    except:
        gss = Gss.objects.get(cn_customs_code='default')
    
    results = []
    if not scan_infos:
        return results
    
    req_data = u"<scan_infos>"
    for scan_info in scan_infos:
        req_data += u"<scan_info>"
        if 'mail_no' in scan_info:
            req_data += u"<mailno>%s</mailno>" % scan_info['mail_no']
        else:
            req_data += u"<mailno>0</mailno>"
        if 'mail_oth_no' in scan_info:       
            req_data += u"<mail_oth_no>%s</mail_oth_no>" % scan_info['mail_oth_no']
        else:
            req_data += u"<mail_oth_no>0</mail_oth_no>"
        req_data += u"<time>%s</time>" % scan_info['time']
        req_data += u"<remark>%s</remark>" % scan_info['remark']
        
        req_data += u"</scan_info>"
    req_data += u"</scan_infos>"
    req_data = base64.b64encode(req_data.encode('utf-8'))
    
    sign_infor = req_data + gss.tracking_passwd
    sign_infor = hashlib.md5(sign_infor).hexdigest()
        
    all_infor = {
               'account':gss.tracking_username,
               'version':gss.tracking_version,
               'validation':sign_infor,
               'data':req_data,
               }
    try:
        r = requests.post(gss.add_tracking_api_url, data=all_infor)
        # need to delete
        logger.debug(r.text)
        # end need to delte

        text = r.text.encode('ascii', 'xmlcharrefreplace')
        tree = ET.fromstring(text)
              
        for response in tree:
            
            status = response.find('status').text
            msg = response.find('msg').text
            if status == '1':
                results.append({
                                'tracking_number':response.find('mail_no').text,
                                })
            else:
                # send mail
                send_mail(u"Error when push tracking records bei GOS",
                  "",
                  u'韵达德国 <info@mail.yunda-express.eu>',
                  ['lik.li@yunda-express.eu'],
                  fail_silently=False,
                  html_message=u"%s: %s\nYDE Number: %s" % (status, msg, response.find('hawbno').text))
        return results
    except Exception as e:    
        # send mail
        send_mail(u"Connection Error when push tracking records bei GOS",
              "",
              u'韵达德国 <info@mail.yunda-express.eu>',
              ['lik.li@yunda-express.eu'],
              fail_silently=False,
              html_message=e)
        return []
        
def tracking_fetch(scan_infos, cn_customs_code=None):
    if not cn_customs_code:cn_customs_code = 'default'    
    try:
        gss = Gss.objects.get(cn_customs_code=cn_customs_code)
    except:
        gss = Gss.objects.get(cn_customs_code='default')
    
    results = []
    if not scan_infos:
        return results
        
    req_data = u"<scan_infos>"
    for scan_info in scan_infos:
        req_data += u"<scan_info>"
        if 'mail_no' in scan_info:
            req_data += u"<mailno>%s</mailno>" % scan_info['mail_no']
            req_data += u"<mailno_type>2</mailno_type>"
        elif 'mail_oth_no' in scan_info:
            req_data += u"<mailno>%s</mailno>" % scan_info['mail_oth_no']
            req_data += u"<mailno_type>1</mailno_type>"
                    
        req_data += u"</scan_info>"
    req_data += u"</scan_infos>"
    req_data = base64.b64encode(req_data.encode('utf-8'))
    
    sign_infor = req_data + gss.tracking_passwd
    sign_infor = hashlib.md5(sign_infor).hexdigest()

    all_infor = {
               'account':gss.tracking_username,
               'version':gss.tracking_version,
               'validation':sign_infor,
               'data':req_data,
               }
    try:
        r = requests.post(gss.get_tracking_api_url, data=all_infor)
        
        text = r.text.encode('ascii', 'xmlcharrefreplace')
        tree = ET.fromstring(text)
           
        for response in tree:
            status = response.find('status').text
            msg = response.find('msg').text
            scan_infos = []
            if status == '1':                    
                for scan_info in response.find('scan_infos'):
                    scan_infos.append({
                        'time':scan_info.find('time').text,
                        'remark':scan_info.find('remark').text,
                                       })
                
            else:
                scan_infos.append({
                        'time': strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'),
                        'remark':msg,
                                       })
            results.append({
                                'tracking_number':response.find('mail_no').text,
                                'scan_infos':scan_infos,
                                })
        return results
    except Exception as e:
        logger.error(e)
        # send mail
        send_mail(u"Error when fetch tracking records bei GOS",
              "",
              u'韵达德国 <info@mail.yunda-express.eu>',
              ['lik.li@yunda-express.eu'],
              fail_silently=False,
              html_message=e)
        return []

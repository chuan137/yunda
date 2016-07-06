# -*- coding: utf-8 -*-
from userena.decorators import secure_required
from userena.views import signin
from yunda_parcel.views import create_intl_parcel
from django.shortcuts import render
from django.core.context_processors import csrf
from yunda_commen.decorators import json_response
from django.contrib.admin.views.decorators import staff_member_required

import logging
logger=logging.getLogger('django')

@secure_required
def index(request):
    if request.user.is_authenticated():
        return create_intl_parcel(request)
    else:
        return signin(request)

    #return render(request,'angulr.index.html')

@secure_required
def error404(request):
    return render(request,'base/error-404.html')

@secure_required
def error400(request):
    return render(request,'base/error-400.html')

@secure_required
def error500(request):
    return render(request,'base/error-500.html')

@secure_required
def help(request):
    return render(request,'help.html')

@secure_required
def imprint(request):
    return render(request,'imprint.html')
@json_response
def json_get_csrf_token(request):

    return {"csrf_token":csrf(request)['csrf_token']}


####
@secure_required
@staff_member_required
def admin_url(request):
    return render(request,'admin_url_list.html')

#version update
from yunda_parcel.models import SenderTemplate, ReceiverTemplate,\
    SenderTemplateTmp, ReceiverTemplateTmp
@secure_required
@staff_member_required
@json_response
def init_template_to_tmp(request):
    templates=SenderTemplate.objects.all()
    for template in templates:
        try:
            tpl=SenderTemplateTmp.objects.create(user_id=template.user_id,
                yde_number=template.yde_number,
                sender_name=template.sender_name,
                sender_name2=template.sender_name2,
                sender_company=template.sender_company,
                sender_state=template.sender_state,
                sender_city=template.sender_city,
                sender_postcode=template.sender_postcode,
                sender_street=template.sender_street,
                sender_add=template.sender_add,
                sender_hause_number=template.sender_hause_number,
                sender_tel=template.sender_tel,
                sender_email=template.sender_email,
                sender_country=template.sender_country)
            tpl.setYid()
        except Exception as e:
            logger.error(e)
        template.delete()

    for template in ReceiverTemplate.objects.all():
        try:
            tpl=ReceiverTemplateTmp.objects.create(
                user_id=template.user_id,
                yde_number=template.yde_number,
                receiver_name=template.receiver_name,
                receiver_company=template.receiver_company,
                receiver_province=template.receiver_province,
                receiver_city=template.receiver_city,
                receiver_district=template.receiver_district,
                receiver_postcode=template.receiver_postcode,
                receiver_address=template.receiver_address,
                receiver_address2=template.receiver_address2,
                receiver_mobile=template.receiver_mobile,
                receiver_email=template.receiver_email,
                receiver_country=template.receiver_country)
            tpl.setYid()
        except Exception as e:
            logger.error(e)
        template.delete()

@json_response
@secure_required
@staff_member_required
def init_tmp_to_template(request):
    result=""
    for template in SenderTemplateTmp.objects.all():
        try:
            tpl=SenderTemplate.objects.create(user_id=template.user_id,
                yde_number=template.yde_number,
                sender_name=template.sender_name,
                sender_name2=template.sender_name2,
                sender_company=template.sender_company,
                sender_state=template.sender_state,
                sender_city=template.sender_city,
                sender_postcode=template.sender_postcode,
                sender_street=template.sender_street,
                sender_add=template.sender_add,
                sender_hause_number=template.sender_hause_number,
                sender_tel=template.sender_tel,
                sender_email=template.sender_email,
                sender_country=template.sender_country)
            tpl.setYid()
            result+=tpl.yid
        except Exception as e:
            logger.debug(e)
        #template.delete()

    for template in ReceiverTemplateTmp.objects.all():
        try:
            tpl=ReceiverTemplate.objects.create(
                user_id=template.user_id,
                yde_number=template.yde_number,
                receiver_name=template.receiver_name,
                receiver_company=template.receiver_company,
                receiver_province=template.receiver_province,
                receiver_city=template.receiver_city,
                receiver_district=template.receiver_district,
                receiver_postcode=template.receiver_postcode,
                receiver_address=template.receiver_address,
                receiver_address2=template.receiver_address2,
                receiver_mobile=template.receiver_mobile,
                receiver_email=template.receiver_email,
                receiver_country=template.receiver_country)
            tpl.setYid()
            result+=tpl.yid
        except Exception as e:
            logger.debug(e)
        #template.delete()
    return result

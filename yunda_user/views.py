# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext
from yunda_user import models
from django.template import RequestContext
from yunda_commen.commen_utils import get_seq_by_code, get_settings
from django.contrib.auth.decorators import  login_required
from userena.decorators import secure_required
# from yunda_user.models import FundTransfer, FundFrozen
from django.views.generic.base import TemplateView
from django.db.models import Q
from yunda_parcel.models import ParcelType, CustomerParcelPrice, DhlRetoureLabel
from django.contrib.auth.models import User
from django.views.generic.list import ListView
from django.utils.decorators import classonlymethod, method_decorator
from django.utils.translation import ugettext, ugettext_lazy as _

from userena.forms import (SignupForm, SignupFormOnlyEmail, AuthenticationForm,
                           ChangeEmailForm, EditProfileForm, identification_field_factory)
from django.contrib.auth import authenticate, login, logout
from userena import settings as userena_settings
from userena import signals as userena_signals
from yunda_commen.decorators import json_response
import math
import pytz
from django.conf import settings
import base64
from parcel.forms import InvoiceAddressForm
from django.contrib.admin.views.decorators import staff_member_required
from parcel.models import Level, IntlParcel
from userena.models import UserProfile
from messenge.models import Subject
from xlwt.Workbook import Workbook
from datetime import datetime
from yunda_user.models import DepositTransferNew
from yunda_commen.commen_tasks import get_old_deposit_transfers_task
import logging
logger=logging.getLogger('django')


# Create your views here.
# Create your views here.
class ExtraContextTemplateView(TemplateView):
    """ Add extra context to a simple template view """
    extra_context = None

    def get_context_data(self, *args, **kwargs):
        context = super(ExtraContextTemplateView, self).get_context_data(*args, **kwargs)
        if self.extra_context:
            context.update(self.extra_context)
        return context

    # this view is used in POST requests, e.g. signup when the form is not valid
    post = TemplateView.get

@secure_required
@login_required
def my_price_and_fund(request):
    u_id = request.session.get('_auth_user_id')
    myprices = []
    for parcel_type in ParcelType.objects.all():
        myprice = CustomerParcelPrice.objects.filter(customer_id=u_id, parcel_type=parcel_type)[0]
        myprices.append(myprice)

    user = User.objects.get(id=u_id)


    extra_context = dict()
    extra_context['myprices'] = myprices
    extra_context['user'] = user
    extra_context['retoure_price'] = get_settings().dhl_retoure_price_eur
    extra_context['eur_to_cny_rate'] = get_settings().eur_to_cny_rate
    extra_context['currency_change_margin'] = str(int(get_settings().currency_change_margin * 100)) + "%"

#     return render_to_response('yunda_parcel/intl_parcel_list.html')
    return ExtraContextTemplateView.as_view(template_name="yunda_user/my_price_and_fund.html",
                                            extra_context=extra_context)(request)

class DepositTransferListView(ListView):
    model = models.DepositTransfer
    paginate_by = 20
    context_object_name = "transfer_list"
    template_name = "yunda_user/deposit_transfer_list.html"

    def get_queryset(self):
        user = self.request.session.get('_auth_user_id')
        queryset = models.DepositTransfer.objects.filter(user_id=user).order_by('-created_at')
        return queryset

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DepositTransferListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DepositTransferListView, self).get_context_data(**kwargs)


        context['sub_sidebar_name'] = 'deposit'
        context['breadcrumbs'] = [{'name':_('User center'), 'url':'#'},
                              {'name':_('Deposit transfer'), 'url':reverse('deposit_transfer_list')}]
        return context


#############FOR angular

@json_response
@secure_required
def signin(request):
    """
    Signin using email or username with password.

    Signs a user in by combining email/username with password. If the
    combination is correct and the user :func:`is_active` the
    :func:`redirect_signin_function` is called with the arguments
    ``REDIRECT_FIELD_NAME`` and an instance of the :class:`User` who is is
    trying the login. The returned value of the function will be the URL that
    is redirected to.


    **Context**

    ``form``
        Form used for authentication supplied by ``auth_form``.

    """
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request.POST, request.FILES)
        if form.is_valid():
            identification, password, remember_me = (form.cleaned_data['identification'],
                                                     form.cleaned_data['password'],
                                                     form.cleaned_data['remember_me'])
            user = authenticate(identification=identification,
                                password=password)
            if user.is_active:
                login(request, user)
                if remember_me:
                    request.session.set_expiry(userena_settings.USERENA_REMEMBER_ME_DAYS[1] * 86400)
                else: request.session.set_expiry(0)

                # send a signal that a user has signed in
                userena_signals.account_signin.send(sender=None, user=user)

                return {'user':{"username":user.get_full_name(), "customer_number":user.userprofile.customer_number}}
            else:
                return {'error':"无效的用户。"}
        else:
            return {'error':"输入数据有误。"}

@json_response
@secure_required
def signup(request):
    """
    Sign up a new user.

    """
    signup_form = SignupFormOnlyEmail
    form = signup_form()

    if request.method == 'POST':
        form = signup_form(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            # Send the signup complete signal
            userena_signals.signup_complete.send(sender=None,
                                                 user=user)

            # A new signed user should logout the old one.
            if request.user.is_authenticated():
                logout(request)

            if (userena_settings.USERENA_SIGNIN_AFTER_SIGNUP and
                not userena_settings.USERENA_ACTIVATION_REQUIRED):
                user = authenticate(identification=user.email, check_password=False)
                login(request, user)

            return {'sucess':u'感谢您的注册！<br>已经发送一封包含激活链接的邮件给您。请登录邮箱激活账号。<br>我们会在服务器上保存账号激活信息7天。'}
        else:
            return {'error':u"无效的用户。"}

@json_response
@secure_required
def json_check_login(request):
    u_id = request.session.get('_auth_user_id')
    if not u_id:
        return {'error':u'未登录'}
    try:
        user = User.objects.get(id=u_id)
        # import pdb; pdb.set_trace()
        if user.is_staff:
            return {'error':u'未登录'}
        else:
            return {'logined':user.userprofile.customer_number,
                'username':user.username,
                'currency_type':user.userprofile.deposit_currency_type,
                'level_name':user.userprofile.level and user.userprofile.level.name or u"普通会员",
                }
    except User.DoesNotExist:
        return {'error':u'账户不存在'}

@json_response
@secure_required
@login_required
def json_search_deposit_transfer(request):
#    logger.debug("###############################################")
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)
    if request.method == 'GET':
        q = models.DepositTransferNew.objects.filter(user_id=user_id)
        page = int(request.GET.get('page', 1))
        rows = int(request.GET.get('rows', 10))

        s = request.GET.get('s', False)
        if s:
            q = q.filter(ref__contains=s)


        results = {}
        count = q.count()
        results['count'] = count or 0
        results['transfers'] = []
        results['currency_type'] = user.userprofile.deposit_currency_type
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
#        logger.debug("######################################")
        for transfer in q.order_by('-created_at')[start:end]:
            tf = {
                "created_at":transfer.created_at.astimezone(local).strftime("%Y-%m-%d %H:%M"),
                "amount":"%.2f" % transfer.amount,
                "ref":transfer.ref or ""
                }
            results['transfers'].append(tf)
#        logger.debug(user.userprofile.deposit_currency_type)
        results['currency_type'] = user.userprofile.deposit_currency_type
        return results

@json_response
@secure_required
@login_required
def json_search_invoice(request):
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)
    if request.method == 'GET':
        q = models.Invoice.objects.filter(user_id=user_id)
        page = int(request.GET.get('page', 1))
        rows = int(request.GET.get('rows', 10))

        s = request.GET.get('s', False)
        if s:
            q = q.filter(number__contains=s)

        results = {}
        count = q.count()
        results['count'] = count or 0
        results['invoices'] = []
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
        for invoice in q.order_by('-created_at')[start:end]:
            inv = {
                "created_at":invoice.created_at.astimezone(local).strftime("%Y-%m-%d %H:%M"),
                "amount":"%.2f" % invoice.amount,
                "number":invoice.number
                }
            results['invoices'].append(inv)
        results['currency_type'] = user.userprofile.deposit_currency_type
        return results

@secure_required
@login_required
def print_invoice(request, number):
    user_id = request.session.get('_auth_user_id')
    invoice = get_object_or_404(models.Invoice, user_id=user_id, number__iexact=number)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % number

    content = invoice.pdf_file or ""
    content = base64.b64decode(content)
    response.write(content)
    return response

@json_response
@secure_required
@login_required
def json_post_invoice_address(request):
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = InvoiceAddressForm(request.POST, request.FILES)

        if form.is_valid():
            if user.userprofile.customer_number == form.cleaned_data['customer_number']:
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.save()
                user.userprofile.company = form.cleaned_data['company']
                user.userprofile.street = form.cleaned_data['street']
                user.userprofile.hause_number = form.cleaned_data['hause_number']
                user.userprofile.street_add = form.cleaned_data['street_add']
                user.userprofile.city = form.cleaned_data['city']
                user.userprofile.state = form.cleaned_data['state']
                user.userprofile.postcode = form.cleaned_data['postcode']
                user.userprofile.tel = form.cleaned_data['tel']
                user.userprofile.vat_id = form.cleaned_data['vat_id']
                user.userprofile.country_code = form.cleaned_data['country_code']
                user.userprofile.save()
                userena_signals.profile_change.send(sender=None,
                                                 user=user)
                return dict(state="success")
            else:
                return {"state":'error-msg',
                        'msg':'请重新登录'}
        else:
            # not valid
            return dict(state='error',
                        errors=form.errors)

            # user = form.save()
    else:
        return {'error':True}

@json_response
@secure_required
@login_required
def json_get_invoice_address(request):
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)

    result = {}
    result['email'] = user.email
    result['customer_number'] = user.userprofile.customer_number
    result['first_name'] = user.first_name or ''
    result['last_name'] = user.last_name or ''
    result['company'] = user.userprofile.company or ''
    result['street'] = user.userprofile.street or ''
    result['hause_number'] = user.userprofile.hause_number or ''
    result['street_add'] = user.userprofile.street_add or ''
    result['city'] = user.userprofile.city or ''
    result['state'] = user.userprofile.state or ''
    result['postcode'] = user.userprofile.postcode or ''
    result['tel'] = user.userprofile.tel or ''
    result['vat_id'] = user.userprofile.vat_id or ''
    result['country_code'] = user.userprofile.country_code or ''
    result['country_name'] = user.userprofile.get_country_code_display() or ''
    return {'user':result, 'state':'success'}

@json_response
@secure_required
@login_required
def json_get_current_deposit(request):
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)
    return {'current_deposit':"%.2f" % user.userprofile.current_deposit,
            'deposit_currency_type': user.userprofile.get_deposit_currency_type_display()
            }

@json_response
@secure_required
@login_required
def json_get_notification_number(request):
    user_id = request.session.get('_auth_user_id')
    subject_unread_number=Subject.objects.filter(user_id=user_id,has_unread_messenge=True).count() or 0

    intl_parcel_todo_number=IntlParcel.objects.filter(user_id=user_id).filter(
                                                                              Q(status__in=['draft','error'])|
                                                                              Q(sfz_status='2')).count() or 0

    retoure_todo_number=DhlRetoureLabel.objects.filter(user_id=user_id,status="draft").count() or 0
    return {
            'subject_unread_number':subject_unread_number,
            'intl_parcel_todo_number':intl_parcel_todo_number,
            'retoure_todo_number':retoure_todo_number,
            }

#####################################################
# admin
#####################################################
def get_customer_info(customer, local=None):
    result = {}

    if not local:
        tz = getattr(settings, 'TIME_ZONE', 'Asia/Shanghai')
        local = pytz.timezone(tz)


    result['date_joined'] = customer.date_joined.astimezone(local).strftime("%Y-%m-%d %H:%M")
    result['name']=customer.get_full_name()
    try:
        userprofile=customer.userprofile
    except:
        #create userprofile
        userprofile=UserProfile.objects.create(user_id=customer.id,deposit_currency_type="eur")
        userena_signals.profile_change.send(sender=None,user=customer)


    if not userprofile.customer_number:
        userena_signals.profile_change.send(sender=None,user=customer)

    result['customer_number']=userprofile.customer_number
    result['company']=userprofile.company  or ''
    result['street']=userprofile.street  or ''
    result['hause_number']=userprofile.hause_number or ''
    result['street_add']=userprofile.street_add or ''
    result['postcode']=userprofile.postcode or ''
    result['city']=userprofile.city or ''
    result['state']=userprofile.state or ''
    result['country_code']=userprofile.country_code or ''
    result['tel']=userprofile.tel or ''
    result['fax']=userprofile.fax or ''
    result['vat_id']=userprofile.vat_id or ''
    result['deposit_currency_type']=userprofile.deposit_currency_type
    result['current_deposit']=userprofile.current_deposit or 0
    result['credit']=userprofile.credit or 0
    try:
        result['level_code']=customer.userprofile.level and customer.userprofile.level.code or ""
    except:
        level_id=Level.objects.get(code="default")
        customer.userprofile.level_id=level_id
        customer.userprofile.save()
        result['level_code']="default"



    return result
@json_response
@secure_required
@staff_member_required
def admin_json_search_customers(request):
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)
    if request.method == 'GET':
        q = User.objects.exclude(is_staff=True).exclude(is_superuser=True).filter(is_active=True)
        page = int(request.GET.get('page', 1))
        rows = int(request.GET.get('rows', 10))

        s = request.GET.get('s', False)
        if s:
            q = q.filter(Q(first_name__contains=s)
                         |Q(last_name__contains=s)
                         |Q(email__contains=s)
                         |Q(userprofile__customer_number__contains=s)
                         |Q(userprofile__postcode__contains=s)
                         |Q(userprofile__city__contains=s)
                         |Q(userprofile__state__contains=s)
                         |Q(userprofile__street__contains=s)
                         |Q(userprofile__street_add__contains=s)
                         |Q(userprofile__tel__contains=s)
                         )

        results = {}
        count = q.count()
        results['count'] = count or 0
        results['customers'] = []
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
        for customer in q.order_by('-date_joined')[start:end]:
            results['customers'].append(get_customer_info(customer, local))
        return results

@json_response
@secure_required
@staff_member_required
def admin_json_get_customer(request, customer_number):
    user_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=user_id)
    try:
        userprofile=UserProfile.objects.get(customer_number=customer_number,is_active=True,is_staff=False,is_superuser=False)
        results=get_customer_info(userprofile.user)
    except UserProfile.DoesNotExist:
        {'state':'error'}
    return {'customer':results, 'state':'success'}

@json_response
@secure_required
@staff_member_required
def admin_json_get_notification_number(request):
    user_id = request.session.get('_auth_user_id')
    subject_unread_number=Subject.objects.filter(has_staff_unread=True).count() or 0

    return {
            'subject_unread_number':subject_unread_number,
            }


@secure_required
@staff_member_required
def admin_excel_users(request):
    book = Workbook()
    sheet = book.add_sheet('users')
    row = 0
    sheet.write(row, 0, u'电子邮件')
    sheet.write(row, 1, u'姓名')
    sheet.write(row, 2, u'历史总单量')
    sheet.write(row, 3, u'1510单量')
    sheet.write(row, 4, u'1511单量')
    sheet.write(row, 5, u'1512单量')
    sheet.write(row, 6, u'1601单量')
    sheet.write(row, 7, u'1602单量')
    sheet.write(row, 8, u'1603单量')
    sheet.write(row, 9, u'1604单量')
    sheet.write(row, 10, u'联系电话')
    sheet.write(row, 11, u'城市')
    sheet.write(row, 12, u'公司')
    sheet.write(row, 13, u'地址')
    row += 1
    try:
        for user in User.objects.all():
            try:
                userprofile=user.userprofile
            except:
                continue
            shipments = IntlParcel.objects.filter(user=user)
            sheet.write(row, 0, user.email)
            sheet.write(row, 1, user.get_full_name() or "")
            sheet.write(row, 2, shipments.exclude(is_deleted=True).count())
            sheet.write(row, 3, shipments.exclude(is_deleted=True).filter(created_at__year="2015").filter(created_at__month="10").count())
            sheet.write(row, 4, shipments.exclude(is_deleted=True).filter(created_at__year="2015").filter(created_at__month="11").count())
            sheet.write(row, 5, shipments.exclude(is_deleted=True).filter(created_at__year="2015").filter(created_at__month="12").count())
            sheet.write(row, 6, shipments.exclude(is_deleted=True).filter(created_at__year="2016").filter(created_at__month="01").count())
            sheet.write(row, 7, shipments.exclude(is_deleted=True).filter(created_at__year="2016").filter(created_at__month="02").count())
            sheet.write(row, 8, shipments.exclude(is_deleted=True).filter(created_at__year="2016").filter(created_at__month="03").count())
            sheet.write(row, 9, shipments.exclude(is_deleted=True).filter(created_at__year="2016").filter(created_at__month="04").count())

            address=""
            tel=""
            city=""
            company=""
            if userprofile and userprofile.street and userprofile.street not in ["-", "_", ]:
                address = user.get_full_name() + ", " + userprofile.street + " " + (userprofile.hause_number or "")
                tel=userprofile.tel or ""
                city=userprofile.city or ""
                company=userprofile.company or ""
            elif shipments.count()>0:
                shipment=shipments.order_by("-created_at")[0]

                address = shipment.sender_name + ", "+(shipment.sender_name2 or "")+", " + shipment.sender_street + " " + (shipment.sender_hause_number or "")
                tel=shipment.sender_tel or ""
                city=shipment.sender_city or ""
                company=shipment.sender_company or ""

            sheet.write(row, 10, tel or "")
            sheet.write(row, 11, city or "")
            sheet.write(row, 12, company or "")
            sheet.write(row, 13, address or "")
            sheet.write(row, 14, userprofile.level and userprofile.level.code or "")
            row += 1
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=users-%s.xls' % datetime.now().strftime('%Y%m%d%H%M%S')
        book.save(response)
        return response

    except Exception as e:
        logger.error(e)
        return HttpResponse(e)
############
# for version change
@secure_required
@login_required
def get_old_deposit_transfers(request):
#    get_old_deposit_transfers_task()
    get_old_deposit_transfers_task.delay()
    return HttpResponse("True")

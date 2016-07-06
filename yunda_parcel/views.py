# -*- coding: utf-8 -*-
from django.shortcuts import  render_to_response, redirect, get_object_or_404
from django.forms.formsets import formset_factory, BaseFormSet
from userena.decorators import secure_required
from yunda_parcel import models, forms, tasks
from django.template.context import RequestContext
from django.http.response import HttpResponse
from django.http import Http404
from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import  login_required, permission_required
from userena.models import User
from yunda_parcel.models import CnCustomsTax, Parcel, \
    SenderTemplate, ReceiverTemplate, DhlRetoureLabel
from datetime import datetime
from yunda_parcel.forms import ParcelBookItForm
from django.views.generic.list import ListView
import json
import base64

from django.utils.decorators import classonlymethod, method_decorator
from django.db.models import Q
from wkhtmltopdf.views import PDFTemplateView

from yunda_commen.commen_utils import get_settings

from django.utils.translation import  ugettext_lazy as _
import math
import pytz
from django.conf import settings
import hashlib
from django.core.context_processors import csrf

import logging
logger = logging.getLogger('django')


def return_error_info(request, title, msg):
    return render_to_response('base/error_info.html', dict(title=title, msg=msg), context_instance=RequestContext(request))
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
def create_intl_parcel_per_excel_upload(request):
    if request.method == "Post":
        pass
    # TODO

@secure_required
@login_required
def create_intl_parcel(request):

    logger.debug("#####################################################")
    logger.debug('ok')
    logger.debug("#####################################################")

    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False
    u_id = request.session.get('_auth_user_id')
    user = User.objects.get(id=u_id)
    if not user.first_name:
        redirect_to = reverse('userena_profile_edit',
                                        kwargs={'username': user.get_username()})
        return redirect(redirect_to)
    DetailFormSet = formset_factory(forms.ParcelDetailForm, max_num=100, formset=RequiredFormSet)
    if request.method == 'POST':
        form_parcel = forms.ParcelForm(request.POST)
        # form_parcel.
        form_detail_formset = DetailFormSet(request.POST, request.FILES)
        if form_parcel.is_valid() and form_detail_formset.is_valid():
            parcel = form_parcel.save()
            # u_id = request.session.get('_auth_user_id')
            # user = User.objects.get(id=u_id)
            parcel.user = user
            parcel.salesman = user.userprofile.salesman
            parcel.branch = user.userprofile.branch
            (parcel.start_price_eur, parcel.start_weight_kg,
                parcel.continuing_price_eur, parcel.continuing_weight_kg, parcel.volume_weight_rate ,
                parcel.branch_start_price_eur, parcel.branch_start_weight_kg,
                parcel.branch_continuing_price_eur, parcel.branch_continuing_weight_kg,
                parcel.branch_volume_weight_rate) = parcel.type.get_price_by_user(user)
            parcel.created_at = datetime.now()
            parcel.eur_to_cny_rate = get_settings().eur_to_cny_rate

            if form_parcel.clean()['cn_customs_pay_by'] == 'sender':
                parcel.sender_pay_cn_customs = True
            else:
                parcel.sender_pay_cn_customs = False
            parcel.yde_number = hashlib.md5("yd%d" % parcel.id).hexdigest()
            parcel.save()
            parcel.save()
            for detail_form in form_detail_formset.forms:
                detail = detail_form.save(commit=False)
                detail.parcel = parcel
                try:
                    cn_tax = CnCustomsTax.objects.get(id=detail_form.clean()['cn_customs_tax'])
                except CnCustomsTax.DoesNotExist:
                    cn_tax = CnCustomsTax.objects.get(cn_name=u"其它", is_active=True)
                detail.cn_customs_tax = cn_tax
                detail.save()

            # create template
            parcel_info = form_parcel.clean()
            if request.POST.get('save_sender_template', False):
                SenderTemplate.objects.create(user=user,
                                            sender_name=parcel_info['sender_name'],
                                            sender_name2=parcel_info['sender_name2'] or "",
                                            sender_company=parcel_info['sender_company'] or "",
                                            # sender_state=parcel_info['sender_state'] or "",
                                            sender_city=parcel_info['sender_city'] or "",
                                            sender_postcode=parcel_info['sender_postcode'] or "",
                                            sender_street=parcel_info['sender_street'] or "",
                                            sender_add=parcel_info['sender_add'] or "",
                                            sender_hause_number=parcel_info['sender_hause_number'] or "",
                                            sender_tel=parcel_info['sender_tel'] or "",
                                            sender_email=parcel_info['sender_email']) or ""
            if request.POST.get('save_receiver_template', False):
                ReceiverTemplate.objects.create(user=user,
                                            receiver_name=parcel_info['receiver_name'],
                                            receiver_company=parcel_info['receiver_company'] or "",
                                            receiver_province=parcel_info['receiver_province'] or "",
                                            receiver_city=parcel_info['receiver_city'] or "",
                                            receiver_district=parcel_info['receiver_district'] or "",
                                            receiver_postcode=parcel_info['receiver_postcode'] or "",
                                            receiver_address=parcel_info['receiver_address'] or "",
                                            receiver_address2=parcel_info['receiver_address2'] or "",
                                            receiver_mobile=parcel_info['receiver_mobile'] or "",
                                            receiver_email=parcel_info['receiver_email'] or "")


            redirect_to = reverse('parcel_intl_detail',
                                        kwargs={'yde_number': parcel.yde_number})
            return redirect(redirect_to)

    else:
        form_detail_formset = DetailFormSet()
        form_parcel = forms.ParcelForm()
    return render_to_response('yunda_parcel/parcel_intl_create_form.html',
                                               dict(form_detail_formset=form_detail_formset, form_parcel=form_parcel),
                                               context_instance=RequestContext(request))

@secure_required
@login_required
def edit_intl_parcel(request, yde_number):

    parcel = get_object_or_404(models.Parcel, yde_number=yde_number)
    u_id = request.session.get('_auth_user_id')
    if u_id != (parcel.user and parcel.user.id):
        raise Http404('Tried to get shipment of other account! user id: %d' % u_id)

    if not(parcel.payment_status == 'pr_pas_unpaid' and parcel.cn_tax_status == 'pr_cts_unpaid'):
        return return_error_info(request, _('Error'), _('Shipment cannot be edited any more!'))

    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False
    DetailFormSet = formset_factory(forms.ParcelDetailForm, max_num=100, formset=RequiredFormSet)
    # DetailFormSet = modelformset_factory(models.ParcelDetail, form = ParcelDetailForm)
    if request.method == 'POST':
        form_parcel = forms.ParcelForm(request.POST)
        # form_parcel.
        form_detail_formset = DetailFormSet(request.POST, request.FILES)
        if form_parcel.is_valid() and form_detail_formset.is_valid():
            parcel = form_parcel.save()

            user = User.objects.get(id=u_id)
            parcel.user = user
            parcel.salesman = user.userprofile.salesman
            parcel.branch = user.userprofile.branch
            (parcel.start_price_eur, parcel.start_weight_kg,
                parcel.continuing_price_eur, parcel.continuing_weight_kg, parcel.volume_weight_rate ,
                parcel.branch_start_price_eur, parcel.branch_start_weight_kg,
                parcel.branch_continuing_price_eur, parcel.branch_continuing_weight_kg,
                parcel.branch_volume_weight_rate) = parcel.type.get_price_by_user(user)
            parcel.created_at = datetime.now()
            parcel.eur_to_cny_rate = get_settings().eur_to_cny_rate

            if form_parcel.clean()['cn_customs_pay_by'] == 'sender':
                parcel.sender_pay_cn_customs = True
            else:
                parcel.sender_pay_cn_customs = False

            for detail_form in form_detail_formset.forms:
                detail = detail_form.save(commit=False)
                detail.parcel = parcel
                try:
                    cn_tax = CnCustomsTax.objects.get(id=detail_form.clean()['cn_customs_tax'])
                except CnCustomsTax.DoesNotExist:
                    cn_tax = CnCustomsTax.objects.get(cn_name=u"其它", is_active=True)
                detail.cn_customs_tax = cn_tax
                detail.save()

            # create template
            parcel_info = form_parcel.clean()
            if request.POST.get('save_sender_template', False):
                SenderTemplate.objects.create(user=user,
                                            sender_name=parcel_info['sender_name'],
                                            sender_name2=parcel_info['sender_name2'] or "",
                                            sender_company=parcel_info['sender_company'] or "",
                                            # sender_state=parcel_info['sender_state'] or "",
                                            sender_city=parcel_info['sender_city'] or "",
                                            sender_postcode=parcel_info['sender_postcode'] or "",
                                            sender_street=parcel_info['sender_street'] or "",
                                            sender_add=parcel_info['sender_add'] or "",
                                            sender_hause_number=parcel_info['sender_hause_number'] or "",
                                            sender_tel=parcel_info['sender_tel'] or "",
                                            sender_email=parcel_info['sender_email']) or ""
            if request.POST.get('save_receiver_template', False):
                ReceiverTemplate.objects.create(user=user,
                                            receiver_name=parcel_info['receiver_name'],
                                            receiver_company=parcel_info['receiver_company'] or "",
                                            receiver_province=parcel_info['receiver_province'] or "",
                                            receiver_city=parcel_info['receiver_city'] or "",
                                            receiver_district=parcel_info['receiver_district'] or "",
                                            receiver_postcode=parcel_info['receiver_postcode'] or "",
                                            receiver_address=parcel_info['receiver_address'] or "",
                                            receiver_address2=parcel_info['receiver_address2'] or "",
                                            receiver_mobile=parcel_info['receiver_mobile'] or "",
                                            receiver_email=parcel_info['receiver_email'] or "")

            old_parcel = get_object_or_404(models.Parcel, yde_number=yde_number)
            old_parcel.is_delete = True
            old_parcel.save()
            redirect_to = reverse('parcel_intl_detail',
                                        kwargs={'yde_number': parcel.yde_number})

            return redirect(redirect_to)

    else:

        form_detail_formset = DetailFormSet()
        # form_detail_formset = DetailFormSet(queryset=parcel.parceldetail_set)
        form_parcel = forms.ParcelForm(instance=parcel)
        if parcel.sender_pay_cn_customs:
            form_parcel.fields["cn_customs_pay_by"].initial = 'sender'
        else:
            form_parcel.fields["cn_customs_pay_by"].initial = 'receiver'
        pass
    return render_to_response('yunda_parcel/parcel_intl_create_form.html',
                                               dict(form_detail_formset=form_detail_formset, form_parcel=form_parcel),
                                               context_instance=RequestContext(request))


@secure_required
@login_required
def intl_parcel_detail(request, yde_number):
    parcel = get_object_or_404(models.Parcel, yde_number__iexact=yde_number)
    u_id = request.session.get('_auth_user_id')
    if u_id != (parcel.user and parcel.user.id):
        raise Http404('Tried to get shipment of other account! user id: %d' % u_id)

    # return HttpResponse('parcel_id:' + str(id))
    extra_context = dict()
    extra_context['parcel'] = parcel
    extra_context['form'] = ParcelBookItForm({'yde_number':yde_number})
    return ExtraContextTemplateView.as_view(template_name="yunda_parcel/parcel_intl_detail.html",
                                            extra_context=extra_context)(request)

@secure_required
@login_required
def intl_parcel_delete(request, yde_number):
    parcel = get_object_or_404(models.Parcel, yde_number__iexact=yde_number)
    u_id = request.session.get('_auth_user_id')
    if u_id != (parcel.user and parcel.user.id):
        raise Http404('Tried to get shipment of other account! user id: %d' % u_id)

    if not(parcel.payment_status == 'pr_pas_unpaid' and parcel.cn_tax_status == 'pr_cts_unpaid'):
        return return_error_info(request, _('Error'), _('Shipment cannot be deleted any more!'))

    # return HttpResponse('parcel_id:' + str(id))
    parcel.is_delete = True
    parcel.save()
    redirect_to = reverse('parcel_intl_list')
    return redirect(redirect_to)

@secure_required
@login_required
def intl_parcel_pay(request, yde_number):
    # if request.method == 'POST': #TODO
    if True:
        parcel = get_object_or_404(models.Parcel, yde_number__iexact=yde_number)
        u_id = request.session.get('_auth_user_id')
        if u_id != (parcel.user and parcel.user.id):
            raise Http404('Tried to get shipment of other account! user id: %d' % u_id)

        # return HttpResponse('parcel_id:' + str(id))
        (can_book, msg) = parcel.can_book_it()
        if can_book:
            parcel.book_it()
            redirect_to = reverse('parcel_intl_detail', kwargs={'yde_number': parcel.yde_number})
            return redirect(redirect_to)
        else:
            # raise Http404(msg)
            return return_error_info(request, _('Error'), msg)
    else:
        # raise Http404('No shipment found!')
        return return_error_info(request, _('Error'), _('No shipment found!'))

class ParcelPdfView(PDFTemplateView):
    filename = "parcel.pdf"
    template_name = 'yunda_parcel/webkit_parcel.html'
    cmd_options = {
        'orientation': 'portrait',
        # 'collate': True,
        # 'quiet': None,
    }
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ParcelPdfView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(ParcelPdfView, self).get_context_data(*args, **kwargs)
        if kwargs.has_key('yde_number'):
            parcel = get_object_or_404(Parcel, yde_number=kwargs['yde_number'])


            u_id = self.request.session.get('_auth_user_id')
            if u_id != (parcel.user and parcel.user.id):
                raise Http404('Tried to print label of other account! User id: %d' % u_id)


            context.update({'shipment':parcel})
            if not parcel.printed_at:
                parcel.printed_at = datetime.now()
                parcel.save()
#         if self.extra_context:
#             context.update(self.extra_context)
        return context

class ParcelListView(ListView):
    model = Parcel
    paginate_by = 20
    context_object_name = "parcel_list"

    def get_queryset(self):
        search = self.request.GET.get('s')
        user = self.request.session.get('_auth_user_id')
        if search:
            search = search.strip()
            if search == 'draft':  # draft
                myfilter = Q(payment_status__in=['pr_pas_unpaid']) | Q(cn_tax_status__in=['pr_cts_unpaid'])
                queryset = Parcel.objects.filter(user=user).filter(myfilter).exclude(is_delete=True).order_by('-created_at')
            elif search == 'paid':  # paid after created
                queryset = Parcel.objects.filter(user=user, cn_tax_status__in=['pr_cts_sender_paid', 'pr_cts_receiver_pay', 'pr_cts_sender_pay_0tax'], \
                                                 payment_status__in=['pr_pas_paid']
                                                 ).exclude(is_delete=True).order_by('-created_at')
            elif search == 'waiting-sender-pay-rest':  # need sender pay the rest
                myfilter = Q(payment_status__in=[ 'pr_pas_need_pay_rest']) | Q(cn_tax_status__in=[ 'pr_cts_sender_pay_need_pay_rest', 'pr_cts_sender_pay_0tax_need_pay_rest'])
                queryset = Parcel.objects.filter(user=user).filter(myfilter).exclude(is_delete=True).order_by('-created_at')
            elif search == 'waiting-receiver-pay':  # need receiver pay
                queryset = Parcel.objects.filter(user=user, cn_tax_status='pr_cts_receiver_pay_need_pay').exclude(is_delete=True).order_by('-created_at')
            elif search == 'all':  # need receiver pay
                queryset = Parcel.objects.filter(user=user).exclude(is_delete=True).order_by('-created_at')
            else:
                myfilter = Q(yde_number__iexact=search) | Q(tracking_number__iexact=search) | Q(ref__iexact=search) | Q(receiver_name__iexact=search)
                queryset = Parcel.objects.filter(user=user).filter(myfilter).exclude(is_delete=True).order_by('-created_at')
        else:
            queryset = Parcel.objects.filter(user=user).exclude(is_delete=True).order_by('-created_at')
        return queryset

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ParcelListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ParcelListView, self).get_context_data(**kwargs)

        search = self.request.GET.get('s')
        if search == 'draft':
            context['sub_sidebar_name'] = 'draft'
            context['breadcrumbs'] = [{'name':_('Intl. shipment'), 'url':'#'},
                                  {'name':_('Draft'), 'url':reverse('parcel_intl_list') + '?s=draft'}]
        elif search == 'paid':  # paid after created
            context['sub_sidebar_name'] = 'paid'
            context['breadcrumbs'] = [{'name':_('Intl. shipment'), 'url':'#'},
                                  {'name':_('Paid'), 'url':reverse('parcel_intl_list') + '?s=paid'}]
        elif search == 'waiting-sender-pay-rest':  # need sender pay the rest
            context['sub_sidebar_name'] = 'waiting-sender-pay-rest'
            context['breadcrumbs'] = [{'name':_('Intl. shipment'), 'url':'#'},
                                  {'name':_('Waiting sender pay rest'), 'url':reverse('parcel_intl_list') + '?s=waiting-sender-pay-rest'}]
        elif search == 'waiting-receiver-pay':  # need receiver pay
            context['sub_sidebar_name'] = 'waiting-receiver-pay'
            context['breadcrumbs'] = [{'name':_('Intl. shipment'), 'url':'#'},
                                  {'name':_('Waiting receiver pay'), 'url':reverse('parcel_intl_list') + '?s=waiting-receiver-pay'}]
        else:
            context['sub_sidebar_name'] = 'all'
            context['breadcrumbs'] = [{'name':_('Intl. shipment'), 'url':'#'},
                                  {'name':_('All'), 'url':reverse('parcel_intl_list') + '?s=all'}]
        return context
#     @classonlymethod
#     def as_view(cls, **initkwargs):
#         self = cls(**initkwargs)
#         view = super(ParcelListView, cls).as_view(**initkwargs)
    @classonlymethod
    def as_view(self, paid=False, unpaid=False, **initkwargs):
        # self = cls(**initkwargs)
        view = super(ParcelListView, self).as_view(**initkwargs)
        return view

@secure_required
@login_required
def intl_parcel_list(request):
    u_id = request.session.get('_auth_user_id')
    ONE_PAGE_OF_DATA = 2
    try:
        curPage = int(request.GET.get('curPage', '1'))
        allPage = int(request.GET.get('allPage', '1'))
        pageType = str(request.GET.get('pageType', ''))
    except ValueError:
        curPage = 1
        allPage = 1
        pageType = ''

    if pageType == 'pageDown':
        curPage += 1
    elif pageType == 'pageUp':
        curPage -= 1

    startPos = (curPage - 1) * ONE_PAGE_OF_DATA
    endPos = startPos + ONE_PAGE_OF_DATA
    parcels = Parcel.objects.filter(user_id=u_id).order_by('-created_at')[startPos:endPos]

    if curPage == 1 and allPage == 1:
        allPostCounts = Parcel.objects.filter(user_id=u_id).count()
        allPage = allPostCounts / ONE_PAGE_OF_DATA
        remainPost = allPostCounts % ONE_PAGE_OF_DATA
        if remainPost > 0:
            allPage += 1

    extra_context = dict()
    extra_context['parcels'] = parcels
    extra_context['allPage'] = allPage
    extra_context['curPage'] = curPage
    extra_context['curPage'] = curPage
    extra_context['breadcrumbs'] = [{'name':_('Intl. shipment'), 'url':'#'},
                                  {'name':_('All'), 'url':reverse('intl_parcel_list')}]

#     return render_to_response('yunda_parcel/intl_parcel_list.html')
    return ExtraContextTemplateView.as_view(template_name="yunda_parcel/intl_parcel_list.html",
                                            extra_context=extra_context)(request)

@secure_required
@login_required
def sender_template_list(request):
    try:
        curPage = int(request.GET.get('curPage', '1'))
        allPage = int(request.GET.get('allPage', '1'))
        pageType = str(request.GET.get('pageType', ''))
    except ValueError:
        curPage = 1
        allPage = 1
        pageType = ''
    if pageType == 'pageDown':
        curPage += 1
    elif pageType == 'pageUp':
        curPage -= 1
    show_qty_per_page = 20
    u_id = request.session.get('_auth_user_id')
    startPos = (curPage - 1) * show_qty_per_page
    endPos = startPos + show_qty_per_page
    templates = SenderTemplate.objects.filter(user_id=u_id)[startPos:endPos]

    if curPage == 1 and allPage == 1:  # 标记1
        allPostCounts = SenderTemplate.objects.filter(user_id=u_id).count()
        allPage = allPostCounts / show_qty_per_page
        remainPost = allPostCounts % show_qty_per_page
        if remainPost > 0:
            allPage += 1

    return render_to_response("yunda_parcel/sender_template_list.html",
                              {'templates':templates, 'allPage':allPage, 'curPage':curPage},
                              context_instance=RequestContext(request))

@secure_required
@login_required
def receiver_template_list(request):
    try:
        curPage = int(request.GET.get('curPage', '1'))
        allPage = int(request.GET.get('allPage', '1'))
        pageType = str(request.GET.get('pageType', ''))
    except ValueError:
        curPage = 1
        allPage = 1
        pageType = ''
    if pageType == 'pageDown':
        curPage += 1
    elif pageType == 'pageUp':
        curPage -= 1
    show_qty_per_page = 20
    u_id = request.session.get('_auth_user_id')
    startPos = (curPage - 1) * show_qty_per_page
    endPos = startPos + show_qty_per_page
    templates = ReceiverTemplate.objects.filter(user_id=u_id)[startPos:endPos]

    if curPage == 1 and allPage == 1:  # 标记1
        allPostCounts = ReceiverTemplate.objects.filter(user_id=u_id).count()
        allPage = allPostCounts / show_qty_per_page
        remainPost = allPostCounts % show_qty_per_page
        if remainPost > 0:
            allPage += 1

    return render_to_response("yunda_parcel/receiver_template_list.html",
                              {'templates':templates, 'allPage':allPage, 'curPage':curPage},
                              context_instance=RequestContext(request))

@secure_required
@login_required
def json_sender_template_count(request):
    u_id = request.session.get('_auth_user_id')
    allCounts = SenderTemplate.objects.filter(user_id=u_id).count()
    result = {'count':allCounts}
    return HttpResponse(json.dumps(result), content_type="application/json")

@secure_required
@login_required
def json_sender_template_onpage(request, start=0, end=0):
    u_id = request.session.get('_auth_user_id')
    templates = SenderTemplate.objects.filter(user_id=u_id)[start:end]
    result = []
    for template in templates:
        result.append({
            "sender_name":template.sender_name or "",
            "sender_name2": template.sender_name2 or "",
            "sender_company":template.sender_company or "",
            "sender_state": template.sender_state or "",
            "sender_city": template.sender_city or "",
            "sender_postcode": template.sender_postcode or "",
            "sender_street": template.sender_street or "",
            "sender_add":template.sender_add or "",
            "sender_hause_number": template.sender_hause_number or "",
            "sender_tel":template.sender_tel or "",
            "sender_email":template.sender_email or "",
                       })
    return HttpResponse(json.dumps(result), content_type="application/json")

@secure_required
@login_required
def json_receiver_template_count(request):
    u_id = request.session.get('_auth_user_id')
    allCounts = ReceiverTemplate.objects.filter(user_id=u_id).count()
    result = {'count':allCounts}
    return HttpResponse(json.dumps(result), content_type="application/json")

@secure_required
@login_required
def json_receiver_template_onpage(request, start=0, end=0):
    u_id = request.session.get('_auth_user_id')
    templates = ReceiverTemplate.objects.filter(user_id=u_id)[start:end]
    result = []
    for template in templates:
        result.append({
            "receiver_name":template.receiver_name or "",
            "receiver_company": template.receiver_company or "",
            "receiver_province":template.receiver_province or "",
            "receiver_city": template.receiver_city or "",
            "receiver_district": template.receiver_district or "",
            "receiver_postcode": template.receiver_postcode or "",
            "receiver_address": template.receiver_address or "",
            "receiver_address2":template.receiver_address2 or "",
            "receiver_mobile": template.receiver_mobile or "",
            "receiver_email":template.receiver_email or "",
                       })
    return HttpResponse(json.dumps(result), content_type="application/json")

@secure_required
@login_required
def create_dhl_retoure_label(request):
    if request.method == 'POST':
        form = forms.DhlRetoureLabelForm(request.POST)
        if form.is_valid():
            retoure_label = form.save(commit=False)
            u_id = request.session.get('_auth_user_id')
            user = User.objects.get(id=u_id)
            retoure_label.user = user
            retoure_label.created_at = datetime.now()
            retoure_label.save()
            redirect_to = reverse('dhl_retoure_label_detail',
                                        kwargs={'yde_number': retoure_label.retoure_yde_number})
            return redirect(redirect_to)

    else:
        form = forms.DhlRetoureLabelForm()
    return render_to_response('yunda_parcel/retoure_label_create_form.html',
                                               dict(form=form),
                                               context_instance=RequestContext(request))

@secure_required
@login_required
def dhl_retoure_label_detail(request, yde_number):
    label = get_object_or_404(models.DhlRetoureLabel, retoure_yde_number__iexact=yde_number)
    u_id = request.session.get('_auth_user_id')
    if u_id != (label.user and label.user.id):
        raise Http404('Tried to get retoure label of other account! user id: %d' % u_id)
        # return return_error_info(request, _('Error'), _('No retoure label found!'))

    # return HttpResponse('parcel_id:' + str(id))
    extra_context = dict()
    extra_context['label'] = label
    extra_context['form'] = forms.DhlRetoureLabelBookItForm({'retoure_yde_number':yde_number})
    return ExtraContextTemplateView.as_view(template_name="yunda_parcel/retoure_label_detail.html",
                                            extra_context=extra_context)(request)

@secure_required
@login_required
def dhl_retoure_label_book_it(request, yde_number):
    u_id = request.session.get('_auth_user_id')
    retoure_label = get_object_or_404(DhlRetoureLabel, retoure_yde_number__iexact=yde_number)
    if u_id != (retoure_label.user and retoure_label.user.id):
        raise Http404('Tried to get retoure label of other account! user id: %d' % u_id)
    (can_book, msg) = retoure_label.can_book_it()
    if not can_book:
        # raise Http404(msg)
        return return_error_info(request, _('Error'), msg)
    else:
        retoure_label.book_it()
        redirect_to = reverse('dhl_retoure_label_detail',
                                    kwargs={'yde_number': retoure_label.retoure_yde_number})
        return redirect(redirect_to)

@secure_required
@login_required
def dhl_retoure_label_delete(request, yde_number):
    u_id = request.session.get('_auth_user_id')
    retoure_label = get_object_or_404(DhlRetoureLabel, retoure_yde_number__iexact=yde_number)
    if u_id != (retoure_label.user and retoure_label.user.id):
        raise Http404('Tried to get retoure label of other account! user id: %d' % u_id)
    if retoure_label.payment_status == "rl_pas_unpaid":
        retoure_label.is_deleted = True
        retoure_label.deleted_at = datetime.now()
        retoure_label.save()
        return redirect(reverse('retoure_label_list') + "?s=draft")
    else:
        # raise Http404("Retoure label can't be deleted!")
        return return_error_info(request, _('Error'), _("Retoure label can't be deleted!"))
@secure_required
@login_required
def dhl_retoure_label_get_pdf(request, yde_number):
    u_id = request.session.get('_auth_user_id')
    label = get_object_or_404(models.DhlRetoureLabel, retoure_yde_number__iexact=yde_number)
    if u_id != (label.user and label.user.id):
        raise Http404('Tried to print retoure label of other account! user id: %d' % u_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="' + label.retoure_yde_number + '.pdf"'

#     # Create the PDF object, using the response object as its "file."
#     p = canvas.Canvas(response)
#
#     # Draw things on the PDF. Here's where the PDF generation happens.
#     # See the ReportLab documentation for the full list of functionality.
#     p.drawString(100, 100, "Hello world.")
#
#     # Close the PDF object cleanly, and we're done.
#     p.showPage()
#     p.save()
    content = label.pdf_file
    content = base64.b64decode(content)
    response.write(content)
    if not label.printed_at:
        label.printed_at = datetime.now()
        label.save()
    return response
    # return HttpResponse(label.pdf_file,mimetype='application/pdf')

@secure_required
@login_required
def unpaid_retoure_label_list(request):
    u_id = request.session.get('_auth_user_id')
    ONE_PAGE_OF_DATA = 20
    try:
        curPage = int(request.GET.get('curPage', '1'))
        allPage = int(request.GET.get('allPage', '1'))
        pageType = str(request.GET.get('pageType', ''))
    except ValueError:
        curPage = 1
        allPage = 1
        pageType = ''

    if pageType == 'pageDown':
        curPage += 1
    elif pageType == 'pageUp':
        curPage -= 1

    startPos = (curPage - 1) * ONE_PAGE_OF_DATA
    endPos = startPos + ONE_PAGE_OF_DATA
    retoure_labels = DhlRetoureLabel.objects.filter(user_id=u_id).filter(is_booked=False).exclude(is_canceled=True)[startPos:endPos]

    if curPage == 1 and allPage == 1:
        allPostCounts = DhlRetoureLabel.objects.filter(user_id=u_id).filter(is_booked=False).exclude(is_canceled=True).count()
        allPage = allPostCounts / ONE_PAGE_OF_DATA
        remainPost = allPostCounts % ONE_PAGE_OF_DATA
        if remainPost > 0:
            allPage += 1

    extra_context = dict()
    extra_context['retoure_labels'] = retoure_labels
    extra_context['allPage'] = allPage
    extra_context['curPage'] = curPage

#     return render_to_response('yunda_parcel/intl_parcel_list.html')
    return ExtraContextTemplateView.as_view(template_name="yunda_parcel/retoure_label_list.html",
                                            extra_context=extra_context)(request)

@secure_required
@login_required
def retoure_label_list(request):
    u_id = request.session.get('_auth_user_id')
    ONE_PAGE_OF_DATA = 20
    try:
        curPage = int(request.GET.get('curPage', '1'))
        allPage = int(request.GET.get('allPage', '1'))
        pageType = str(request.GET.get('pageType', ''))
    except ValueError:
        curPage = 1
        allPage = 1
        pageType = ''

    if pageType == 'pageDown':
        curPage += 1
    elif pageType == 'pageUp':
        curPage -= 1

    startPos = (curPage - 1) * ONE_PAGE_OF_DATA
    endPos = startPos + ONE_PAGE_OF_DATA
    retoure_labels = DhlRetoureLabel.objects.filter(user_id=u_id)[startPos:endPos]

    if curPage == 1 and allPage == 1:
        allPostCounts = DhlRetoureLabel.objects.filter(user_id=u_id).count()
        allPage = allPostCounts / ONE_PAGE_OF_DATA
        remainPost = allPostCounts % ONE_PAGE_OF_DATA
        if remainPost > 0:
            allPage += 1

    extra_context = dict()
    extra_context['retoure_labels'] = retoure_labels
    extra_context['allPage'] = allPage
    extra_context['curPage'] = curPage

#     return render_to_response('yunda_parcel/intl_parcel_list.html')
    return ExtraContextTemplateView.as_view(template_name="yunda_parcel/retoure_label_list.html",
                                            extra_context=extra_context)(request)

@secure_required
@permission_required('is_superuser')
def cn_customs_tax_list(request):
    ONE_PAGE_OF_DATA = 20
    try:
        curPage = int(request.GET.get('curPage', '1'))
        allPage = int(request.GET.get('allPage', '1'))
        pageType = str(request.GET.get('pageType', ''))
    except ValueError:
        curPage = 1
        allPage = 1
        pageType = ''

    if pageType == 'pageDown':
        curPage += 1
    elif pageType == 'pageUp':
        curPage -= 1

    startPos = (curPage - 1) * ONE_PAGE_OF_DATA
    endPos = startPos + ONE_PAGE_OF_DATA
    taxs = CnCustomsTax.objects.filter(is_active=True)[startPos:endPos]

    if curPage == 1 and allPage == 1:
        allPostCounts = CnCustomsTax.objects.filter(is_active=True).count()
        allPage = allPostCounts / ONE_PAGE_OF_DATA
        remainPost = allPostCounts % ONE_PAGE_OF_DATA
        if remainPost > 0:
            allPage += 1

    extra_context = dict()
    extra_context['taxs'] = taxs
    extra_context['allPage'] = allPage
    extra_context['curPage'] = curPage

#     return render_to_response('yunda_parcel/intl_parcel_list.html')
    return ExtraContextTemplateView.as_view(template_name="yunda_parcel/cn_customs_tax_list.html",
                                            extra_context=extra_context)(request)

class DhlRetoureLabelListView(ListView):
    model = DhlRetoureLabel
    paginate_by = 20
    context_object_name = "label_list"
    template_name = "yunda_parcel/retoure_label_list.html"

    def get_queryset(self):
        search = self.request.GET.get('s')
        user = self.request.session.get('_auth_user_id')

        if search == 'draft':  # draft
            queryset = DhlRetoureLabel.objects.filter(user_id=user).filter(payment_status__in=['rl_pas_unpaid']).exclude(is_deleted=True).order_by('-created_at')
        elif search == 'paid':  # paid after created
            queryset = DhlRetoureLabel.objects.filter(user_id=user, payment_status__in=['rl_pas_paid']).exclude(is_deleted=True).order_by('-created_at')
        else:
            queryset = DhlRetoureLabel.objects.filter(user_id=user).exclude(is_deleted=True).order_by('-created_at')
        return queryset

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DhlRetoureLabelListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DhlRetoureLabelListView, self).get_context_data(**kwargs)

        search = self.request.GET.get('s')
        if search == 'draft':
            context['sub_sidebar_name'] = 'draft'
            context['breadcrumbs'] = [{'name':_('Retoure label'), 'url':'#'},
                                  {'name':_('Draft'), 'url':reverse('retoure_label_list') + '?s=draft'}]
        elif search == 'paid':  # paid after created
            context['sub_sidebar_name'] = 'paid'
            context['breadcrumbs'] = [{'name':_('Retoure label'), 'url':'#'},
                                  {'name':_('Paid'), 'url':reverse('retoure_label_list') + '?s=paid'}]
        else:
            context['sub_sidebar_name'] = 'all'
            context['breadcrumbs'] = [{'name':_('Retoure label'), 'url':'#'},
                                  {'name':_('All'), 'url':reverse('retoure_label_list') + '?s=all'}]
        return context
#     @classonlymethod
#     def as_view(cls, **initkwargs):
#         self = cls(**initkwargs)
#         view = super(ParcelListView, cls).as_view(**initkwargs)
    @classonlymethod
    def as_view(self, paid=False, unpaid=False, **initkwargs):
        # self = cls(**initkwargs)
        view = super(DhlRetoureLabelListView, self).as_view(**initkwargs)
        return view

class SenderTemplateListView(ListView):
    model = SenderTemplate
    paginate_by = 20
    context_object_name = "template_list"
    template_name = "yunda_parcel/sender_template_list.html"

    def get_queryset(self):
        user = self.request.session.get('_auth_user_id')
        queryset = SenderTemplate.objects.filter(user_id=user).order_by('sender_name')
        return queryset

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SenderTemplateListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SenderTemplateListView, self).get_context_data(**kwargs)


        context['sub_sidebar_name'] = 'sender'
        context['breadcrumbs'] = [{'name':_('Address book'), 'url':'#'},
                              {'name':_('Sender'), 'url':reverse('sender_template_list')}]
        return context

class ReceiverTemplateListView(ListView):
    model = ReceiverTemplate
    paginate_by = 20
    context_object_name = "template_list"
    template_name = "yunda_parcel/receiver_template_list.html"

    def get_queryset(self):
        user = self.request.session.get('_auth_user_id')
        queryset = ReceiverTemplate.objects.filter(user_id=user).order_by('receiver_name')
        return queryset

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReceiverTemplateListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ReceiverTemplateListView, self).get_context_data(**kwargs)


        context['sub_sidebar_name'] = 'receiver'
        context['breadcrumbs'] = [{'name':_('Address book'), 'url':'#'},
                              {'name':_('Receiver'), 'url':reverse('receiver_template_list')}]
        return context


@secure_required
@login_required
def sender_template_detail(request, yde_number):
    template = get_object_or_404(models.SenderTemplate, yde_number=yde_number)
    u_id = request.session.get('_auth_user_id')
    if u_id != (template.user and template.user.id):
        # raise Http404('No sender address template found!')
        raise Http404('Tried to get sender address template of other account! user id: %d' % u_id)

    # return HttpResponse('parcel_id:' + str(id))
    extra_context = dict()
    extra_context['template'] = template
    return ExtraContextTemplateView.as_view(template_name="yunda_parcel/sender_template_detail.html",
                                            extra_context=extra_context)(request)

@secure_required
@login_required
def receiver_template_detail(request, yde_number):
    template = get_object_or_404(models.ReceiverTemplate, yde_number=yde_number)
    u_id = request.session.get('_auth_user_id')
    if u_id != (template.user and template.user.id):
        raise Http404('Tried to get receiver address template of other account! user id: %d' % u_id)

    # return HttpResponse('parcel_id:' + str(id))
    extra_context = dict()
    extra_context['template'] = template
    return ExtraContextTemplateView.as_view(template_name="yunda_parcel/receiver_template_detail.html",
                                            extra_context=extra_context)(request)

@secure_required
@login_required
def sender_template(request, yde_number=None):
    if yde_number:
        template = get_object_or_404(models.SenderTemplate, yde_number=yde_number)
        u_id = request.session.get('_auth_user_id')
        if u_id != (template.user and template.user.id):
            raise Http404('Tried to get sender address template of other account! user id: %d' % u_id)
        if request.method == 'POST':
            form = forms.SenderTemplateForm(request.POST or None, instance=template)
            if form.is_valid():
                form.save()
                redirect_to = reverse('sender_template_detail',
                                            kwargs={'yde_number': template.yde_number})
                return redirect(redirect_to)
        else:
            form = forms.SenderTemplateForm(instance=template)
    else:
        if request.method == 'POST':
            form = forms.SenderTemplateForm(request.POST)
            if form.is_valid():
                template = form.save(commit=False)
                u_id = request.session.get('_auth_user_id')
                # user = User.objects.get(id=u_id)
                template.user_id = u_id
                template.save()
                redirect_to = reverse('sender_template_detail',
                                            kwargs={'yde_number': template.yde_number})
                return redirect(redirect_to)
        else:
            form = forms.SenderTemplateForm()
    return render_to_response('yunda_parcel/sender_template_form.html',
                                               dict(form=form),
                                               context_instance=RequestContext(request))

@secure_required
@login_required
def receiver_template(request, yde_number=None):
    if yde_number:
        template = get_object_or_404(models.ReceiverTemplate, yde_number=yde_number)
        u_id = request.session.get('_auth_user_id')
        if u_id != (template.user and template.user.id):
            raise Http404('Tried to get receiver address template of other account! user id: %d' % u_id)
        if request.method == 'POST':
            form = forms.ReceiverTemplateForm(request.POST or None, instance=template)
            if form.is_valid():
                form.save()
                redirect_to = reverse('receiver_template_detail',
                                            kwargs={'yde_number': template.yde_number})
                return redirect(redirect_to)
        else:
            form = forms.ReceiverTemplateForm(instance=template)
    else:
        if request.method == 'POST':
            form = forms.ReceiverTemplateForm(request.POST)
            if form.is_valid():
                template = form.save(commit=False)
                u_id = request.session.get('_auth_user_id')
                # user = User.objects.get(id=u_id)
                template.user_id = u_id
                template.save()
                redirect_to = reverse('receiver_template_detail',
                                            kwargs={'yde_number': template.yde_number})
                return redirect(redirect_to)
        else:
            form = forms.ReceiverTemplateForm()
    return render_to_response('yunda_parcel/receiver_template_form.html',
                                               dict(form=form),
                                               context_instance=RequestContext(request))


@secure_required
@login_required
def json_list_receiver_template(request):
    u_id = int(request.session.get('_auth_user_id'))
    page = int(request.GET.get('page')) or 1
    limit = int(request.GET.get('rows')) or 1
    sidx = request.GET.get('sidx') or 'yde_number'
    sord = request.GET.get('sord') or 'desc'
#     sidx = 'yde_number'
#     sord = 'desc'

    receiver_name = request.GET.get('receiver_name') or False
    receiver_company = request.GET.get('receiver_company') or False
    receiver_province = request.GET.get('receiver_province') or False
    receiver_city = request.GET.get('receiver_city') or False
    receiver_district = request.GET.get('receiver_district') or False
    receiver_postcode = request.GET.get('receiver_postcode') or False
    receiver_mobile = request.GET.get('receiver_mobile') or False
    receiver_email = request.GET.get('receiver_email') or False
    receiver_address = request.GET.get('receiver_address') or False
    receiver_address2 = request.GET.get('receiver_address2') or False



    q = ReceiverTemplate.objects.filter(user_id=u_id)
    if receiver_name:
        q = q.filter(receiver_name__contains=receiver_name)
    if receiver_company:
        q = q.filter(receiver_company__contains=receiver_company)
    if receiver_province:
        q = q.filter(receiver_province__contains=receiver_province)
    if receiver_city:
        q = q.filter(receiver_city__contains=receiver_city)
    if receiver_district:
        q = q.filter(receiver_district__contains=receiver_district)
    if receiver_postcode:
        q = q.filter(receiver_postcode__contains=receiver_postcode)
    if receiver_mobile:
        q = q.filter(receiver_mobile__contains=receiver_mobile)
    if receiver_email:
        q = q.filter(receiver_email__contains=receiver_email)
    if receiver_address:
        q = q.filter(receiver_address__contains=receiver_address)
    if receiver_address2:
        q = q.filter(receiver_address2__contains=receiver_address2)

    result = {}
    count = q.count()
    if count > 0:
        result['total'] = int(math.ceil(float(count) / float(limit)))
    else:
        result['total'] = 0

    if page > result['total']:
        page = result['total']

    end = limit * page
    start = end - limit
    if start < 0:
        start = 0

    result['page'] = page
    result['records'] = count

    if sord == 'desc':
        templates = q.order_by('-' + sidx)[start:end]
    else:
        templates = q.order_by(sidx)[start:end]
    rows = []
    for template in templates:

        rows.append({
#                      'incame_at':parcel.incame_at,
#                      'code':parcel.code,
#                      'local_tracking_number':parcel.local_tracking_number,
#                      'warehause':parcel.warehause,
            'id':template.yde_number,
            'receiver_name':template.receiver_name,
            'receiver_company':template.receiver_company,
            'receiver_province':template.receiver_province,
            'receiver_city':template.receiver_city,
            'receiver_district':template.receiver_district,
            'receiver_address':template.receiver_address,
            'receiver_address2':template.receiver_address2,
            'receiver_postcode':template.receiver_postcode,
            'receiver_mobile':template.receiver_mobile,
            'receiver_email':template.receiver_email,
#             'cell':[
#                     template.receiver_name,
#                     template.receiver_company,
#                     template.receiver_province,
#                     template.receiver_city,
#                     template.receiver_district,
#                     template.receiver_postcode,
#                     template.receiver_mobile,
#                     template.receiver_email,
#                     ]
                       })

    result['rows'] = rows
    return HttpResponse(json.dumps(result), content_type="application/json")

@secure_required
@login_required
def json_list_sender_template(request):
    u_id = int(request.session.get('_auth_user_id'))
    page = int(request.GET.get('page')) or 1
    limit = int(request.GET.get('rows')) or 1
    sidx = request.GET.get('sidx') or 'yde_number'
    sord = request.GET.get('sord') or 'desc'
#     sidx = 'yde_number'
#     sord = 'desc'

    sender_name = request.GET.get('sender_name') or False
    sender_name2 = request.GET.get('sender_name2') or False
    sender_company = request.GET.get('sender_company') or False
    sender_city = request.GET.get('sender_city') or False
    sender_postcode = request.GET.get('sender_postcode') or False
    sender_street = request.GET.get('sender_street') or False
    sender_tel = request.GET.get('sender_tel') or False



    q = SenderTemplate.objects.filter(user_id=u_id)
    if sender_name:
        q = q.filter(sender_name__contains=sender_name)
    if sender_name2:
        q = q.filter(sender_name2__contains=sender_name2)
    if sender_company:
        q = q.filter(sender_company__contains=sender_company)
    if sender_city:
        q = q.filter(sender_city__contains=sender_city)
    if sender_postcode:
        q = q.filter(sender_postcode__contains=sender_postcode)
    if sender_street:
        q = q.filter(sender_street__contains=sender_street)
    if sender_tel:
        q = q.filter(sender_tel__contains=sender_tel)

    result = {}
    count = q.count()
    if count > 0:
        result['total'] = int(math.ceil(float(count) / float(limit)))
    else:
        result['total'] = 0

    if page > result['total']:
        page = result['total']

    end = limit * page
    start = end - limit
    if start < 0:
        start = 0

    result['page'] = page
    result['records'] = count

    if sord == 'desc':
        templates = q.order_by('-' + sidx)[start:end]
    else:
        templates = q.order_by(sidx)[start:end]
    rows = []
    for template in templates:

        rows.append({
#                      'incame_at':parcel.incame_at,
#                      'code':parcel.code,
#                      'local_tracking_number':parcel.local_tracking_number,
#                      'warehause':parcel.warehause,
            'id':template.yde_number,
            'sender_name':template.sender_name,
            'sender_name2':template.sender_name2,
            'sender_company':template.sender_company,
            'sender_state':template.sender_state,
            'sender_city':template.sender_city,
            'sender_postcode':template.sender_postcode,
            'sender_street':template.sender_street,
            'sender_add':template.sender_add,
            'sender_hause_number':template.sender_hause_number,
            'sender_tel':template.sender_tel,
            'sender_email':template.sender_email,
#             'cell':[
#                     template.receiver_name,
#                     template.receiver_company,
#                     template.receiver_province,
#                     template.receiver_city,
#                     template.receiver_district,
#                     template.receiver_postcode,
#                     template.receiver_mobile,
#                     template.receiver_email,
#                     ]
                       })

    result['rows'] = rows
    return HttpResponse(json.dumps(result), content_type="application/json")

@secure_required
@login_required
def json_intl_parcel_list(request):
    u_id = int(request.session.get('_auth_user_id'))
    page = int(request.GET.get('page')) or 1
    limit = int(request.GET.get('rows')) or 1
#     sidx = request.GET.get('sidx') or 'incame_at'
#     sord = request.GET.get('sord') or 'desc'
    sidx = 'created_at'
    sord = 'desc'

    yde_number = (request.GET.get('yde_number') or "").strip()
    tracking_number = (request.GET.get('tracking_number') or "").strip()
    ref = (request.GET.get('ref') or "").strip()
    sender_name = (request.GET.get('sender_name') or "").strip()
    receiver_name = (request.GET.get('receiver_name') or "").strip()
    receiver_province = (request.GET.get('receiver_province') or "").strip()
    receiver_mobile = (request.GET.get('receiver_mobile') or "").strip()
    type = (request.GET.get('type') or "").strip()
    is_printed = (request.GET.get('is_printed') or "").strip()
    has_cn_id = (request.GET.get('has_cn_id') or "").strip()


    q = models.Parcel.objects.filter(user_id=u_id).exclude(is_delete=True)
    if yde_number:
        if yde_number == 'draft' or yde_number == u'草稿' or yde_number == u'草'or yde_number == u'稿':
            q = q.filter(payment_status='pr_pas_unpaid')
        else:
            q = q.filter(yde_number__contains=yde_number)
    if tracking_number:
        q = q.filter(tracking_number__contains=tracking_number)
    if ref:
        q = q.filter(ref__contains=ref)
    if sender_name:
        q = q.filter(sender_name__contains=sender_name)
    if receiver_name:
        q = q.filter(receiver_name__contains=receiver_name)
    if receiver_province:
        q = q.filter(receiver_province__contains=receiver_province)
    if receiver_mobile:
        q = q.filter(receiver_mobile__contains=receiver_mobile)
    if type:
        parcel_type = get_object_or_404(models.ParcelType, code=type)
        q = q.filter(type=parcel_type)
    if is_printed:
        if is_printed == 'true':
            q = q.filter(printed_at__isnull=False)
        else:
            q = q.filter(printed_at__isnull=True)
    if has_cn_id:
        if has_cn_id == "true":
            q = q.filter(has_cn_id=True)
        else:
            q = q.filter(has_cn_id=False)

    result = {}
    count = q.count()
    if count > 0:
        result['total'] = int(math.ceil(float(count) / float(limit)))
    else:
        result['total'] = 0

    if page > result['total']:
        page = result['total']

    end = limit * page
    start = end - limit
    if start < 0:
        start = 0

    result['page'] = page
    result['records'] = count

    if sord == 'desc':
        parcels = q.order_by('-' + sidx)[start:end]
    else:
        parcels = q.order_by(sidx)[start:end]
    rows = []
    tz = getattr(settings, 'TIME_ZONE', 'Asia/Shanghai')
    local = pytz.timezone(tz)
    for parcel in parcels:
        local_dt = parcel.created_at.astimezone(local)
        if parcel.payment_status == "pr_pas_unpaid":
            y_number = u'草稿'
            is_draft = True
        else:
            y_number = parcel.yde_number
            is_draft = False
        rows.append({
            'id':parcel.yde_number,
            'yde_number': y_number,
            'tracking_number': parcel.tracking_number,
            'ref': parcel.ref,
            'sender_name': parcel.sender_name,
            'receiver_name': parcel.receiver_name,
            'receiver_province': parcel.receiver_province,
            'receiver_mobile': parcel.receiver_mobile,
            'type':parcel.type.code,
            'is_printed':parcel.is_print(),
            'has_cn_id':parcel.get_has_cn_id(),
            'is_draft':is_draft,
                       })

    result['rows'] = rows
    return HttpResponse(json.dumps(result), content_type="application/json")
@secure_required
@login_required
def list_intl_parcel(request):
    chose_list = u":所有;true:是;false:否"
    c = dict(chose_list=chose_list)
    c.update(csrf(request))
    return render_to_response('yunda_parcel/parcel_list.html', c, context_instance=RequestContext(request))

@secure_required
@login_required
def json_intl_parcel_delete(request):
    u_id = int(request.session.get('_auth_user_id'))
    if request.method == 'POST':
        yde_numbers = request.POST.get('yde_numbers', False)
        result = []
        if yde_numbers:
            for yde_number in yde_numbers.split(','):
                try:
                    parcel = models.Parcel.objects.get(yde_number=yde_number, user=u_id, payment_status="pr_pas_unpaid")
                    parcel.is_delete = True
                    parcel.save()
                    result.append(yde_number)
                except models.Parcel.DoesNotExist:
                    continue
                except models.Parcel.MultipleObjectsReturned:
                    pass
                # TODO

        return HttpResponse(json.dumps(result or False), content_type="application/json")

@secure_required
@login_required
def json_intl_parcel_confirm(request):
    u_id = int(request.session.get('_auth_user_id'))
    if request.method == 'POST':
        yde_numbers = request.POST.get('yde_numbers', False)
        result = []
        if yde_numbers:
            for yde_number in yde_numbers.split(','):
                try:
                    parcel = models.Parcel.objects.get(yde_number=yde_number, user=u_id, payment_status="pr_pas_unpaid", is_delete=False)
                    parcel.payment_status = "pr_pas_paid"
                    parcel.yde_number = parcel.type.get_next_yde_number()
                    parcel.save()
                    models.ParcelStatusHistory.objects.create(type="payment_status",
                                           status="pr_pas_paid",
                                           create_at=datetime.now(),
                                           parcel=parcel)
                    tasks.intl_parcel_sync_to_erp(parcel)#delay
                    result.append(yde_number)
                except models.Parcel.DoesNotExist:
                    continue
                except models.Parcel.MultipleObjectsReturned:
                    pass
                # TODO

        return HttpResponse(json.dumps(result or False), content_type="application/json")

# new version
@secure_required
@login_required
def json_list_receiver_templates(request):
    u_id = request.session.get('_auth_user_id')
    rows = []
    for template in ReceiverTemplate.objects.filter(user_id=u_id).all():

        rows.append({
            'id':template.yde_number,
            'receiver_name':template.receiver_name,
            'receiver_company':template.receiver_company,
            'receiver_province':template.receiver_province,
            'receiver_city':template.receiver_city,
            'receiver_district':template.receiver_district,
            'receiver_address':template.receiver_address,
            'receiver_address2':template.receiver_address2,
            'receiver_postcode':template.receiver_postcode,
            'receiver_mobile':template.receiver_mobile,
            'receiver_email':template.receiver_email,
                       })

    return HttpResponse(json.dumps(rows), content_type="application/json")

# new version
@secure_required
@login_required
def json_list_sender_templates(request):
    u_id = request.session.get('_auth_user_id')
    rows = []
    for template in SenderTemplate.objects.filter(user_id=u_id).all():

        rows.append({
            'id':template.yde_number,
            'sender_name':template.sender_name,
            'sender_name2':template.sender_name2,
            'sender_company':template.sender_company,
            'sender_email':template.sender_email,
            'sender_city':template.sender_city,
            'sender_postcode':template.sender_postcode,
            'sender_street':template.sender_street,
            'sender_add':template.sender_add,
            'sender_hause_number':template.sender_hause_number,
            'sender_tel':template.sender_tel,
                       })

    return HttpResponse(json.dumps(rows), content_type="application/json")

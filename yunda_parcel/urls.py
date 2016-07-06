from django.conf.urls import *
from django.contrib.auth import views as auth_views

from yunda_parcel import views
from yunda_parcel.views import ParcelListView


urlpatterns = patterns('',
    url(r'^intl/$', views.list_intl_parcel, name='parcel_intl_list'),
    url(r'^intl/create/$', views.create_intl_parcel, name='parcel_intl_create'),
    # url(r'^intl/list/$', views.ParcelListView.as_view(), name='parcel_intl_list'),
    url(r'^intl/json/$', views.json_intl_parcel_list, name='json_intl_parcel_list'), 
    url(r'^intl/(?P<yde_number>[\@\.\w-]+)/delete/$', views.intl_parcel_delete, name='parcel_intl_delete'),
    url(r'^intl/(?P<yde_number>[\@\.\w-]+)/pay/$', views.intl_parcel_pay, name='parcel_intl_pay'),
    url(r'^intl/(?P<yde_number>[\@\.\w-]+)/print/$', views.ParcelPdfView.as_view(), name='parcel_intl_print'),
    url(r'^intl/(?P<yde_number>[\@\.\w-]+)/edit/$', views.edit_intl_parcel, name='parcel_intl_edit'),
    url(r'^intl/(?P<yde_number>(?!pay|edit|delete\print)[\@\.\w-]+)/$', views.intl_parcel_detail, name='parcel_intl_detail'),
    
    url(r'^retoure-label/$', views.DhlRetoureLabelListView.as_view(), name='retoure_label_list'),
    url(r'^retoure-label/create/$', views.create_dhl_retoure_label, name='create_dhl_retoure_label'),
    url(r'^retoure-label/(?P<yde_number>[\@\.\w-]+)/pay/$', views.dhl_retoure_label_book_it, name='dhl_retoure_label_book_it'),
    url(r'^retoure-label/(?P<yde_number>[\@\.\w-]+)/delete/$', views.dhl_retoure_label_delete, name='dhl_retoure_label_delete'),
    #url(r'^retoure-label/(?P<yde_number>[\@\.\w-]+)/edit/$', views.dhl_retoure_label_book_it, name='dhl_retoure_label_book_it'),
    url(r'^retoure-label/(?P<yde_number>[\@\.\w-]+)/print/$', views.dhl_retoure_label_get_pdf, name='dhl_retoure_label_get_pdf'),
    url(r'^retoure-label/(?P<yde_number>(?!edit|delete|pay|print)[\@\.\w-]+)/$', views.dhl_retoure_label_detail, name='dhl_retoure_label_detail'),
                       
    url(r'^sender-template/$', views.SenderTemplateListView.as_view(), name='sender_template_list'),
    url(r'^sender-template/(?P<yde_number>[\@\.\w-]+)/edit/$', views.sender_template, name='sender_template_edit'),
    url(r'^sender-template/(?P<yde_number>(?!edit|delete)[\@\.\w-]+)/$', views.sender_template_detail, name='sender_template_detail'),
    
    url(r'^receiver-template/$', views.ReceiverTemplateListView.as_view(), name='receiver_template_list'),
    url(r'^receiver-template/(?P<yde_number>[\@\.\w-]+)/edit/$', views.receiver_template, name='receiver_template_edit'),
    url(r'^receiver-template/(?P<yde_number>(?!edit|delete)[\@\.\w-]+)/$', views.receiver_template_detail, name='receiver_template_detail'),
    
    
    # #json sender template
    url(r'^json/sender-template/count/$', views.json_sender_template_count, name='json_sender_template_count'),
    url(r'^json/sender-template/(?P<start>\d+)/(?P<end>\d+)/$', views.json_sender_template_onpage, name='json_sender_template_onpage'),
    url(r'^json/sender-template/$', views.json_sender_template_onpage, name='json_sender_template'),
    # #json sender template
                       
    # #json receiver template
    url(r'^json/receiver-template/count/$', views.json_receiver_template_count, name='json_receiver_template_count'),
    url(r'^json/receiver-template/(?P<start>\d+)/(?P<end>\d+)/$', views.json_receiver_template_onpage, name='json_receiver_template_onpage'),
    url(r'^json/receiver-template/$', views.json_receiver_template_onpage, name='json_receiver_template'),
    
    url(r'^json-list-receiver-templates/$', views.json_list_receiver_templates, name='json_list_receiver_templates'),
    url(r'^json-list-sender-templates/$', views.json_list_sender_templates, name='json_list_sender_templates'),
    
    
    # #end json receiver template

        
    #url(r'^dhl-retoure-label-list/$', views.retoure_label_list, name='retoure_label_list'),
    #url(r'^unpaid-dhl-retoure-label-list/$', views.unpaid_retoure_label_list, name='unpaid_retoure_label_list'),
    #url(r'^dhl-retoure-label/bookit/$', views.dhl_retoure_label_book_it, name='dhl_retoure_label_book_it'),
    #url(r'^dhl-retoure-label/pdf/(?P<yde_number>(?!edit|delete\bookit)[\@\.\w-]+).pdf$', views.dhl_retoure_label_get_pdf, name='dhl_retoure_label_get_pdf'),
    
   # url(r'^cn-customs-tax-list/$', views.cn_customs_tax_list, name='cn_customs_tax_list'),
    #url(r'^cn-customs-tax-upload/$', views.cn_customs_tax_upload, name='cn_customs_tax_upload'),
    

)

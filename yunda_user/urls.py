from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from yunda_user import views


urlpatterns = patterns('',
    url(r'^my-price-and-deposit/$', views.my_price_and_fund, name='my_price_and_fund'),
    url(r'^deposit-transfers/$', views.DepositTransferListView.as_view(), name='deposit_transfer_list'),
    url(r'^json-login/$', views.signin, name='json_login'),
    url(r'^json-signup/$', views.signup, name='json_signup'),
    url(r'^json-check-login/$', views.json_check_login, name='json_check_login'),
    url(r'^json-search-deposit-transfer/$', views.json_search_deposit_transfer, name='json_search_deposit_transfer'),
    url(r'^json-search-invoice/$', views.json_search_invoice, name='json_search_invoice'),
    url(r'^print/invoice/(?P<number>(?!pay|edit|delete\print)[\@\.\w-]+)$', views.print_invoice, name='print_invoice'),
    url(r'^json-post-invoice-address/$', views.json_post_invoice_address, name='json_post_invoice_address'),
    url(r'^json-get-invoice-address/$', views.json_get_invoice_address, name='json_get_invoice_address'),
    url(r'^json-get-current-deposit/$', views.json_get_current_deposit, name='json_get_current_deposit'),
    url(r'^json-get-notification-number/$', views.json_get_notification_number, name='json_get_notification_number'),
    url(r'^admin_json_get_notification_number/$', views.admin_json_get_notification_number, name='admin_json_get_notification_number'),
    url(r'^admin_excel_users/$', views.admin_excel_users, name='admin_excel_users'),    
    url(r'^get_old_deposit_transfers/$', views.get_old_deposit_transfers, name='get_old_deposit_transfers'),

)

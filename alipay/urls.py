from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from alipay import views


urlpatterns = patterns('',
    url(r'^success/$', views.alipay_return_url, name='alipay_return_url'),
    url(r'^notify/$', views.alipay_notify_url, name='alipay_notify_url'),
    url(r'^pay/$', views.json_post_alipay_deposit_order, name='json_post_alipay_deposit_order'),
    url(r'^json-search-alipay-deposit-order/$', views.json_search_alipay_deposit_order, name='json_search_alipay_deposit_order'),
    url(r'^json-check-alipay-deposit-order/$', views.json_check_alipay_deposit_order, name='json_check_alipay_deposit_order'),
)

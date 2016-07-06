from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from yunda_user import views
from django.views.generic.base import TemplateView


urlpatterns = patterns('',
#     url(r'^fund-transfer/$', views.fund_transfer_list, name='fund_transfer_list'),
#     url(r'^fund-entry/$', views.fund_entry_list, name='fund_entry_list'),
#     url(r'^fund-frozen/$', views.fund_frozen_list, name='fund_frozen_list'),
    
    url(r'^test/$', TemplateView.as_view(template_name="admin/test.html"), name='admin_test'),
)

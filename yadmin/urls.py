from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from yunda_user import views as yunda_user_views
from yadmin import views as yadmin_views


urlpatterns = patterns('',    
    url(r'^admin-json-search-customers/$', yunda_user_views.admin_json_search_customers, name='admin_json_search_customers'),
    
    url(r'^json-check-login/$', yadmin_views.json_check_login, name='json_check_login'),
    url(r'^admin-json-post-deposit-entry/$', yadmin_views.admin_json_post_deposit_entry, name='admin_json_post_deposit_entry'),
    url(r'^admin-json-approve-deposit-entry/$', yadmin_views.admin_json_approve_deposit_entry, name='admin_json_approve_deposit_entry'),
    url(r'^admin-json-search-deposit-entry/$', yadmin_views.admin_json_search_deposit_entry, name='admin_json_search_deposit_entry'),
)

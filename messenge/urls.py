from django.conf.urls import *
from django.contrib.auth import views as auth_views

from messenge import views

urlpatterns = patterns('',    
    url(r'^json-post-subject/$', views.json_post_subject, name='json_post_subject'),
    url(r'^json-post-messenge/$', views.json_post_messenge, name='json_post_messenge'),   
    url(r'^json-get-subject/(?P<yid>(?!pay|edit|delete\print)[\@\.\w-]+)/$', views.json_get_subject, name='json_get_subject'),
    url(r'^json-search-subject/$', views.json_search_subject, name='json_search_subject'),
    
    url(r'^admin_json_post_subject/$', views.admin_json_post_subject, name='admin_json_post_subject'),
    url(r'^admin_json_post_messenge/$', views.admin_json_post_messenge, name='admin_json_post_messenge'),   
    url(r'^admin_json_get_subject/(?P<yid>(?!pay|edit|delete\print)[\@\.\w-]+)/$', views.admin_json_get_subject, name='admin_json_get_subject'),
    url(r'^admin_json_search_subject/$', views.admin_json_search_subject, name='admin_json_search_subject'),
        
)

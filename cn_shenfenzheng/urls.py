from django.conf.urls import *
from django.contrib.auth import views as auth_views

from cn_shenfenzheng import views


urlpatterns = patterns('',
    url(r'^$', views.upload, name='cn_shenfenzheng_upload'),
    url(r'^ajax-upload$', views.ajax_upload, name='cn_shenfenzheng_ajax_upload'),
    url(r'^ajax-upload-image$', views.ajax_upload_image, name='cn_shenfenzheng_ajax_upload_image'),
    url(r'^success$', views.upload_success, name='cn_shenfenzheng_upload_success'),
    url(r'^fail$', views.upload_fail, name='cn_shenfenzheng_upload_fail'),
        
)

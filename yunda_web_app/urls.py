from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from yunda_web_app import views
from rest_framework import routers
import yunda_rest_api
import cn_shenfenzheng
#import yadmin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'yunda_web_app.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    # url(r'^commen/', include('yunda_commen.urls')),
    # url(r'^$', 'yunda_web_app.views.index', name='index'),
    url(r'^app/de/error-500/', views.error500, name='error500'),
    url(r'^app/de/error-404/', views.error404, name='error404'),
    url(r'^app/de/error-400/', views.error400, name='error400'),
    url(r'^app/de/help/', views.help, name='help'),
    url(r'^app/de/impressum/', views.imprint, name='imprint'),
    url(r'^app/de/admin_url/', views.admin_url, name='admin_url'),
    url(r'^app/de/$', views.help, name='home'),
    # url(r'^$', "yunda_parcel.views.ParcelListView.as_view", name='home'),
    url(r'^app/de/i18n/', include('django.conf.urls.i18n')),
    url(r'^app/de/accounts/', include('userena.urls')),
    url(r'^app/de/parcels/', include('yunda_parcel.urls')),
    url(r'^app/de/parcel/', include('parcel.urls')),  # new version
    url(r'^app/de/ticket/', include('messenge.urls')),  # new version
    url(r'^app/de/alipay/', include('alipay.urls')),  # new version
    url(r'^app/de/user/', include('yunda_user.urls')),
    # url(r'^account/', include('yunda_user.urls', namespace="account")),
    url(r'^app/de/uksqhtp18inv/', include(admin.site.urls)),
    url(r'^app/de/ydeadmin/', include("yadmin.urls")),
    url(r'^app/de/api/', include('yunda_rest_api.urls')),
    url(r'^app/de/shenfenzheng/', include(cn_shenfenzheng.urls)),
    url(r'^app/de/customer-service/', include('messenge.urls')),
    url(r'^app/de/json-get-csrf-token/', views.json_get_csrf_token, name='json_get_csrf_token'),
    url(r'^app/de/jiankong/', include("jiankong.urls")),
    url(r'^app/de/captcha/', include('captcha.urls')),
    ######################
    #for version update
    url(r'^app/de/init_template_to_tmp/', views.init_template_to_tmp, name='init_template_to_tmp'),
    url(r'^app/de/init_tmp_to_template/', views.init_tmp_to_template, name='init_tmp_to_template'),

)

handler404 = 'yunda_web_app.views.error404'
handler400 = 'yunda_web_app.views.error400'
handler500 = 'yunda_web_app.views.error500'

# urlpatterns+=i18n_patterns('',
#     url(r'^commen/', include('yunda_commen.urls')),
#     url(r'^login/$', 'yunda_user.views.login'),
# )

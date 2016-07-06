from django.conf.urls import *
from django.contrib.auth import views as auth_views
from yunda_rest_api import views
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = patterns('',
    url(r'^$', views.api_root),
    url(r'^parcels/$', views.ParcelList.as_view(), name='parcels_list'),
    url(r'^parcels/(?P<pk>[0-9]+)/$', views.ParcelDetail.as_view(), name='parcel_detail'),
    url(r'^customers/$', views.CustomerList.as_view(), name='customers_list'),
    url(r'^set-customers-as-synced/$', views.api_set_customers_as_synced, name='set_customers_synced'),
    url(r'^set-parcels-as-synced/$', views.api_set_parcels_as_synced, name='set_parcels_synced'),
    url(r'^update-tracking-number/$', views.api_update_tracking_number, name='update_tracking_number'),
)

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]

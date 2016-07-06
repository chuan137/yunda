from django.conf.urls import patterns, url
from jiankong import views

urlpatterns = patterns('',
    url(r'^add_to_jiankong/$', views.add_to_jiankong, name='add_to_jiankong'),
    url(r'^jiankong/$', views.jiankong, name='jiankong'),  
    url(r'^set_mawb/$', views.set_mawb, name='set_mawb'),
    url(r'^excel_need_check/$', views.excel_need_check, name='excel_need_check'),
    url(r'^json_search_jiankong/$', views.json_search_jiankong, name='json_search_jiankong'),
    url(r'^json_edit_jiankong/$', views.json_edit_jiankong, name='json_edit_jiankong'),
    url(r'^json_get_jiankong/$', views.json_get_jiankong, name='json_get_jiankong'),
    url(r'^set_mawb_intl_parcel/$', views.set_mawb_intl_parcel, name='set_mawb_intl_parcel'),
    url(r'^excel_mawb_report/$', views.excel_mawb_report, name='excel_mawb_report'),
)

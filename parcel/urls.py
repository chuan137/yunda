from django.conf.urls import patterns, include, url
from parcel import views

urlpatterns = patterns('',
#     url(r'^fund-transfer/$', views.fund_transfer_list, name='fund_transfer_list'),
#     url(r'^fund-entry/$', views.fund_entry_list, name='fund_entry_list'),
#     url(r'^fund-frozen/$', views.fund_frozen_list, name='fund_frozen_list'),
    url(r'^json-parcel-types/$', views.json_parcel_types, name='json_parcel_types'),
    url(r'^json-post-intl-parcel/$', views.json_post_intl_parcel, name='json_post_intl_parcel'),
    url(r'^json-get-intl-parcel/(?P<yid>(?!pay|edit|delete\print)[\@\.\w-]+)/$', views.json_get_intl_parcel, name='json_get_intl_parcel'),
    url(r'^json-confirm-intl-parcel/$', views.json_confirm_intl_parcel, name='json_confirm_intl_parcel'),
    url(r'^json-remove-intl-parcel/$', views.json_remove_intl_parcel, name='json_remove_intl_parcel'),
    url(r'^json-search-intl-parcel/$', views.json_search_intl_parcel, name='json_search_intl_parcel'),
    url(r'^json-import-intl-parcel/$', views.json_import_intl_parcel, name='json_import_intl_parcel'),
    
    
    url(r'^json-post-retoure/$', views.json_post_retoure, name='json_post_retoure'),
    url(r'^json-get-retoure/(?P<yid>(?!pay|edit|delete\print)[\@\.\w-]+)/$', views.json_get_retoure, name='json_get_retoure'),
    url(r'^json-confirm-retoure/$', views.json_confirm_retoure, name='json_confirm_retoure'),
    url(r'^json-remove-retoure/$', views.json_remove_retoure, name='json_remove_retoure'),
    url(r'^json-search-retoure/$', views.json_search_retoure, name='json_search_retoure'),  
    
    #print
    url(r'^print/retoure/$', views.RetourePdfView.as_view(), name='print_retoure_pdf'), 
    url(r'^print/intl-parcel/$', views.IntlParcelPdfView.as_view(), name='print_intl_parcel_pdf'),
    url(r'^print/intl-parcel-customs/$', views.IntlParcelCustomsPdfView.as_view(), name='print_intl_parcel_customs_pdf'), 
    url(r'^print/intl-parcel-export-proof/$', views.IntlParcelAusfuhrbescheinigungPdfView.as_view(), name='print_intl_parcel_export_proof_pdf'),
    
    
    #admin
    url(r'^admin/panel-json-after-scan-parcel-retoure/$', views.admin_panel_json_after_scan_parcel_retoure, name='admin_panel_json_after_scan_parcel_retoure'), 
    url(r'^admin/panel-available-mawbs/$', views.admin_panel_available_mawbs, name='admin_panel_available_mawbs'),
    url(r'^admin/panel-post-mawbs/$', views.admin_panel_post_mawbs, name='admin_panel_post_mawbs'),
    url(r'^admin/panel-json-submit-parcel/$', views.admin_panel_json_submit_parcel, name='admin_panel_json_submit_parcel'),
    url(r'^admin/panel-json-submit-retoure-second-time/$', views.admin_panel_json_submit_retoure_second_time, name='admin_panel_json_submit_retoure_second_time'),   
    url(r'^admin/panel-search-mawbs/$', views.admin_panel_search_mawbs, name='admin_panel_search_mawbs'),    
    url(r'^admin/json-get-mawb/(?P<id>(?!pay|edit|delete\print)[\@\.\w-]+)/$', views.json_get_mawb, name='json_get_mawb'),
    url(r'^admin/mawb-haiguan-excel/(?P<id>(?!pay|edit|delete\print)[\@\.\w-]+)/$', views.get_mawb_haiguan_excel, name='get_mawb_haiguan_excel'),
    url(r'^admin/batch-manifest-excel/(?P<id>(?!pay|edit|delete\print)[\@\.\w-]+)/$', views.get_batch_manifest_excel, name='get_batch_manifest_excel'),
    url(r'^admin/json-mawb-change-status/$', views.json_mawb_change_status, name='json_mawb_change_status'),
    url(r'^admin/json-remove-mawb/$', views.json_remove_mawb, name='json_remove_mawb'),
    url(r'^admin/json-batch-change-status/$', views.json_batch_change_status, name='json_batch_change_status'),
    url(r'^admin_delete_from_mawb/$', views.admin_delete_from_mawb, name='admin_delete_from_mawb'),
    
    url(r'^admin/json_search_intl_parcel/$', views.admin_json_search_intl_parcel, name='admin_json_search_intl_parcel'),  
    url(r'^admin/upload-gss-excel/$', views.admin_upload_gss_excel, name='admin_upload_gss_excel'),
    url(r'^admin/get-gss-excel/$', views.admin_get_gss_excel, name='admin_get_gss_excel'),
    url(r'^admin/print/intl-parcel4zoll/$', views.AdminIntlParcelPdf4ZollamtView.as_view(), name='admin_print_intl_parcel4zoll_pdf'),
    
    url(r'^json-parcel-tracking/$', views.json_parcel_trackingv_simple, name='json_parcel_tracking'),  
    
    url(r'^json_search_sender_template/$', views.json_search_sender_template, name='json_search_sender_template'),
    url(r'^json_remove_sender_template/$', views.json_remove_sender_template, name='json_remove_sender_template'),
    url(r'^json_post_sender_template/$', views.json_post_sender_template, name='json_post_sender_template'),
    
    url(r'^json_search_receiver_template/$', views.json_search_receiver_template, name='json_search_receiver_template'),
    url(r'^json_remove_receiver_template/$', views.json_remove_receiver_template, name='json_remove_receiver_template'),
    url(r'^json_post_receiver_template/$', views.json_post_receiver_template, name='json_post_receiver_template'),

    url(r'^tracking_push_to_gss/$', views.tracking_push_to_gss, name='tracking_push_to_gss'),
    url(r'^json_get_tracking_from_gss/$', views.json_get_tracking_from_gss, name='json_get_tracking_from_gss'),       
    url(r'^get_yd_print_data/$', views.get_yd_print_data, name='get_yd_print_data'),
    
    url(r'^mail_mawb_report/$', views.mail_mawb_report, name='mail_mawb_report'),
    url(r'^get_sfz_images/$', views.get_sfz_images, name='get_sfz_images'),
    ##20151214
    url(r'^edit_product_main_category/$', views.edit_product_main_category, name='edit_product_main_category'),
    url(r'^edit_product_category/$', views.edit_product_category, name='edit_product_category'),
    url(r'^edit_product_brand/$', views.edit_product_brand, name='edit_product_brand'),
    url(r'^edit_product/$', views.edit_product, name='edit_product'),
    url(r'^get_product/$', views.get_product, name='get_product'),
    url(r'^get_product_by_category/$', views.get_product_by_category, name='get_product_by_category'),
    url(r'^get_product_by_brand/$', views.get_product_by_brand, name='get_product_by_brand'),
    url(r'^admin_get_intl_parcel/$', views.admin_get_intl_parcel, name='admin_get_intl_parcel'),
    url(r'^admin_get_brands/$', views.admin_get_brands, name='admin_get_brands'),
    url(r'^admin_get_main_categories/$', views.admin_get_main_categories, name='admin_get_main_categories'),
    url(r'^admin_get_categories_by_main_category/$', views.admin_get_categories_by_main_category, name='admin_get_categories_by_main_category'),
    url(r'^admin_edit_detail/$', views.admin_edit_detail, name='admin_edit_detail'),
    url(r'^admin_get_cn_customs/$', views.admin_get_cn_customs, name='admin_get_cn_customs'),
    url(r'^admin_set_parcel_cn_customs/$', views.admin_set_parcel_cn_customs, name='admin_set_parcel_cn_customs'),
    url(r'^admin_edit_parcel_processing_msg/$', views.admin_edit_parcel_processing_msg, name='admin_edit_parcel_processing_msg'),
    url(r'^admin_add_new_msg_to_customer/$', views.admin_add_new_msg_to_customer, name='admin_add_new_msg_to_customer'),
    url(r'^admin_get_price_images/$', views.admin_get_price_images, name='admin_get_price_images'),        
    url(r'^admin_get_label_image/$', views.admin_get_label_image, name='admin_get_label_image'),    
    url(r'^admin_upload_third_party_tracking_number_excel/$', views.admin_upload_third_party_tracking_number_excel, name='admin_upload_third_party_tracking_number_excel'),
    url(r'^admin_customer_number_excel/$', views.admin_customer_number_excel, name='admin_customer_number_excel'),

    url(r'^get_duizhangdan_excel/$', views.get_duizhangdan_excel, name='get_duizhangdan_excel'),

)

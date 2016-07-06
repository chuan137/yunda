# -*- coding: utf-8 -*-
from django.conf import settings

STATUSES = getattr(settings,
                          'STATUSES',
                          {
                            'created':3,
                            'opc_arrived':2,
                            'opc_export_ready':1,
                            'opc_export_customs_finished':1,
                            'opc_flied':2,
                            'destination_country_arrived':3,
                            'import_customs_finished':1,
                            'local_opc_received':2,
                            'delivery_staff_asigned':1,
                            'deliveried_at':0,
                           })



CREATED_AFTER_DAYS = getattr(settings,
                          'CREATED_AFTER_DAYS', 3)

OPC_ARRIVED_AFTER_DAYS = getattr(settings,
                          'OPC_ARRIVED_AFTER_DAYS', 1)

OPC_EXPORT_READY_AFTER_DAYS = getattr(settings,
                          'OPC_EXPORT_READY_AFTER_DAYS', 1)

OPC_EXPORT_CUSTOMS_FINISHED_AFTER_DAYS = getattr(settings,
                          'OPC_EXPORT_CUSTOMS_FINISHED_AFTER_DAYS', 1)

OPC_FLIED_AFTER_DAYS = getattr(settings,
                          'OPC_FLIED_AFTER_DAYS', 3)

DESTINATION_COUNTRY_ARRIVED_AFTER_DAYS = getattr(settings,
                          'DESTINATION_COUNTRY_ARRIVED_AFTER_DAYS', 3)

IMPORT_CUSTOMS_FINISHED_AFTER_DAYS = getattr(settings,
                          'IMPORT_CUSTOMS_FINISHED_AFTER_DAYS', 1)

LOCAL_AFTER_DAYS = getattr(settings,
                          'LOCAL_AFTER_DAYS', 2)


EU_CENTERS = getattr(settings,
                          'EU_CENTERS',
                          [u"德国法兰克福处理中心"])
OPC_ARRIVED_MARKS = getattr(settings,
                          'OPC_ARRIVED_MARKS',
                          [u"到达：德国法兰克福处理中心 已扫描", u"到达：韵达法兰克福处理中心 已扫描", u"韵达法兰克福处理中心已扫描", ])

OPC_EXPORT_READY_MARKS = getattr(settings,
                          'OPC_EXPORT_READY_MARKS',
                          [u"下一步：出口清关",u"下一步，出口清关" ])

OPC_EXPORT_CUSTOMS_FINISHED_MARKS = getattr(settings,
                          'OPC_EXPORT_CUSTOMS_FINISHED_MARKS',
                          [u"离岸清关完成", u"出口清关完成"])

OPC_FLIED_MARKS= getattr(settings,
                          'OPC_FLIED_MARKS',
                          [u"飞往目的国家"])

DESTINATION_COUNTRY_ARRIVED_MARKS = getattr(settings,
                          'DESTINATION_COUNTRY_ARRIVED_MARKS',
                          [u"抵达目的国", u"到达目的国", u"目的国到达"])

IMPORT_CUSTOMS_FINISHED_MARKS = getattr(settings,
                          'IMPORT_CUSTOMS_FINISHED_MARKS',
                          [u"进口清关完成", u"目的国进口清关完成"])

LOCAL_OPC_RECEIVED_MARKS = getattr(settings,
                          'IMPORT_CUSTOMS_FINISHED_MARKS',
                          [u'到达：四川',u'到达：重庆',u'到达：广东',u'到达：浙江',u'到达：天津',u'到达：河南',u'到达：上海',])

DELIVERY_STAFF_ASIGNED_MARKS = getattr(settings,
                          'DELIVERY_STAFF_ASIGNED_MARKS',
                          [u"指定：", u"派送", ])  # 只能，必须两个

DELIVERIED_MARKS = getattr(settings,
                          'DELIVERIED_MARKS',
                          [u"签收"])

ADD_TRACKING_URL = getattr(settings,
                         'ADD_TRACKING_URL',
                         'http://222.72.45.34:16120/ydgos/other/addlist.jspx')

GET_TRACKING_URL = getattr(settings,
                         'GET_TRACKING_URL',
                         'http://222.72.45.34:16120/ydgos/other/showlist.jspx')

TRACKING_USERNAME = getattr(settings,
                         'TRACKING_USERNAME',
                         'st0001')

TRACKING_PASSWORD = getattr(settings,
                         'TRACKING_PASSWORD',
                         'E42990F26CCB2D7F')
JIANKONG_TIME_INTERVAL=getattr(settings,
                         'JIANKONG_TIME_INTERVAL',
                         '2H') #D-per day, H-per hour, 2H-2 hours 10M-10min, 30M-30m, others- 30 minute


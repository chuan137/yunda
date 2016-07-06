# -*- coding: utf-8 -*-
from django.conf import settings

ALIPAY_URL = getattr(settings,
                          'ALIPAY_URL',
                          "https://mapi.alipay.net/gateway.do?")

ALIPAY_PARTNER = getattr(settings,
                          'ALIPAY_PARTNER',
                          "2088101122136241")

ALIPAY_KEY = getattr(settings,
                          'ALIPAY_KEY',
                          "760bdzec6y9goq7ctyx96ezkz78287de")

ALIPAY_BASE_URL = getattr(settings,
                          'ALIPAY_BASE_URL',
                          "http://yunda-express.eu")

ALIPAY_URL_AFTER_RETURN = getattr(settings,
                          'ALIPAY_URL_AFTER_RETURN',
                          "http://localhost/static/de/index.html#/accounting/deposit_alipay?success=")


# -*- coding: utf-8 -*-
"""
Django settings for yunda_web_app project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'odv#g#p5**^+9t#am=%dylj(giz5ti$@r3wt66e+)yechbg6&t'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS =['localhost',]

MAIN_ROOT_URL="/" #用于身份证上传二维码

WKHTMLTOPDF_CMD = '/bin/wkhtmltopdf'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_forms_bootstrap',
    'django_extensions',
    'bootstrap3',
    'django.contrib.sites',
    'import_export',
    'djcelery',
    'parcel',
    'userena',
    'guardian',
    'easy_thumbnails',
    'yunda_user',
    'yadmin',
    'yunda_commen',
    'yunda_parcel',
    'yunda_admin',
    'rest_framework',
    'yunda_rest_api',
    'messenge',
    'alipay',
    'cn_shenfenzheng',
    'wkhtmltopdf',
    'jiankong',
    'captcha',
)

# PREFIX_DEFAULT_LOCALE = False
# LOCALEURL_USE_ACCEPT_LANGUAGE = True

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
AUTHENTICATION_BACKENDS = (
    'userena.backends.UserenaAuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'chuan137@gmail.com'
EMAIL_HOST_PASSWORD = 'lele&doudou1249'


ANONYMOUS_USER_ID = -1
AUTH_PROFILE_MODULE = 'userena.UserProfile'

USERENA_SIGNIN_REDIRECT_URL = '/de/index.html'
USERENA_DEFAULT_PRIVACY = 'closed'
USERENA_WITHOUT_USERNAMES = True
USERENA_MUGSHOT_GRAVATAR = False
USERENA_ACTIVATION_RETRY = True
USERENA_KEHU_NUMBER_SEQ_CODE = "c_id"  # 用rmb支付的客户，账单统一到国内公司
USERENA_KEHU_NUMBER_PREFIX = "Y"
USERENA_CUSTOMER_NUMBER_SEQ_CODE = "c_id"  # 欧元支付的客户，账单到其本人或公司
USERENA_CUSTOMER_NUMBER_PREFIX="K"
USERENA_DEFAULT_BRANCH_ID = 1
USERENA_ACTIVATED_REDIRECT_URL="/app/de/accounts/signin/"
LOGIN_URL = '/app/de/accounts/signin/'
LOGOUT_URL = '/app/de/accounts/signout/'
SITE_ID = 1

ROOT_URLCONF = 'yunda_web_app.urls'

WSGI_APPLICATION = 'yunda_web_app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

#DATABASES = {
#        'default': {
#            'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql',$
#            'NAME': 'db_name',                      # Or path to database file if using sqlite3.
#            # The following settings are not used with sqlite3:
#            'USER': 'db_user',
#            'PASSWORD': 'db_password',
#            'HOST': 'localhost',                      # Empty for localhost through domain sockets or$
#            'PORT': '',                      # Set to empty string for default.
#        }
#    }


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'zh-CN'

#LANGUAGES = {('en', u'English'), ('zh-cn', u'Chinese'), ('de', u'Deutsch')}
LANGUAGES = {('zh-cn', u'Chinese')}

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/de-static/'
STATICFILES_DIRS = (
    "/opt/static_site/de-static/",
#os.path.join(BASE_DIR, "static"),
)
#STATIC_ROOT = os.path.join(BASE_DIR, "static/")
STATIC_ROOT = "/opt/static_site/de-static/"
MEDIA_ROOT = "/media/"
MEDIA_URL = '/media/'
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "templates"),
)
LOCALE_PATHS=(os.path.join(BASE_DIR, "locale"),)
BOOTSTRAP3 = {
    'set_required': False,
    'error_css_class': 'bootstrap3-error',
    'required_css_class': 'bootstrap3-required',
    'javascript_in_head': True,
}

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as DEFAULT_TEMPLATE_CONTEXT_PROCESSORS

TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
    'django.core.context_processors.i18n'
)
DHL_RETOURE_NUMBER_SEQ_CODE = "drn_seq"

ADRDRESS_TEMPLATE_NUMBER_SEQ_CODE = "atn_seq"

REST_FRAMEWORK = {
        'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
        'PAGINATE_BY': 100,
    }

SFZ_ROOT_DIR = "/var/sfz/"
SFZ_TMP_DIR_AT_MEDIA_ROOT = "idtmp/"

# CELERY SETTINGS
import djcelery
from datetime import timedelta
djcelery.setup_loader()
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST = "/"
# CELERY_ALWAYS_EAGER = True # set it to True

# 以上为基本配置，以下为周期性任务定义，以celerybeat_开头的

CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

#CELERYBEAT_SCHEDULE = {
#                       'get-accounts-history': {
#        'task': 'accounts.tasks.get_history_from_erp',
#        'schedule': timedelta(minutes=1)  # crontab(minute=1)
#    },
#                       'get-messenge': {
#        'task': 'messenge.tasks.get_subject_from_erp',
#        'schedule': timedelta(minutes=1)  # crontab(minute=1)
#    },
#                       'get-yuanxiangshanyun-history': {
#        'task': 'yuanxiangshanyun.tasks.get_history_from_erp',
#        'schedule': timedelta(minutes=1)  # crontab(minute=1)
#    },
#}

# Odoo Settings used for sfz management
ODOO_URL = "http://localhost"
ODOO_UID = 1
ODOO_USERNAME = "chuan137@gmail.com"
ODOO_PASSWORD = "qweasd"
ODOO_DB = "yunda_db"
ODOO_COMPANY_CODE="yunda_company_code"

############
# logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
       'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s'}  #日志格式
    },
    'filters': {
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'default': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/de/all.log',     #日志输出文件
            'maxBytes': 1024*1024*5,                  #文件大小
            'backupCount': 5,                         #备份份数
            'formatter':'standard',                   #使用哪种formatters日志格式
        },
        'error': {
            'level':'ERROR',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/de/error.log',
            'maxBytes':1024*1024*5,
            'backupCount': 5,
            'formatter':'standard',
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'request_handler': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/de/script.log',
            'maxBytes': 1024*1024*5,
            'backupCount': 5,
            'formatter':'standard',
        },
        'scprits_handler': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename':'/var/log/django/de/script.log',
            'maxBytes': 1024*1024*5,
            'backupCount': 5,
            'formatter':'standard',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['default', 'console','error'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'scripts': {
            'handlers': ['scprits_handler'],
            'level': 'DEBUG',
            'propagate': True
        },
    }
}
#############
TEMPLATE_STRING_IF_INVALID = "invalid string '%s'"
BYPASS_AUTO_YUNDA_MAILNO=False # 不立即自动生成单号。需要手工生成

#alipay
ALIPAY_URL="https://mapi.alipay.net/gateway.do?" #debug
ALIPAY_PARTNER="2088101122136241" #debug
ALIPAY_KEY="760bdzec6y9goq7ctyx96ezkz78287de" #debug
ALIPAY_BASE_URL="http://website_root_url"

ALIPAY_URL_AFTER_RETURN="http://website_root_url/de/index.html#/accounting/deposit_alipay?success="

STATISTICS_SEND_TO_EMAILS=["Mr. Abc <abc@abc.com>"]

WEB_APP_ROOT_URL="http://website_root_url/de/index.html#"


PRODUCT_SMALL_IMAGE_ROOT="/opt/static_site/de/media/standardproduct/small_pic"
PRODUCT_PRICE_IMAGE_ROOT="/opt/static_site/de/media/standardproduct/price_pic"

CAPTCHA_NOISE_FUNCTIONS=('captcha.helpers.noise_dots',)

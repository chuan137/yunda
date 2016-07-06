"""
WSGI config for yunda_web_app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yunda_web_app.settings")

import logging
logger = logging.getLogger('django')

from django.conf import settings
from django.core.wsgi import get_wsgi_application

if settings.DEBUG:
    from werkzeug.debug import DebuggedApplication
    application = DebuggedApplication(get_wsgi_application(), True)
    logger.info('Debug app with Werkzeug.debug')
else:
    application = get_wsgi_application()

# reload under uwsgi
try:
    import uwsgi
    from uwsgidecorators import timer
    from django.utils import autoreload
    logger.info('App under uWSGI, graceful reload on code-changed')

    @timer(3)
    def change_code_graceful_reload(sig):
        if settings.DEBUG and autoreload.code_changed():
            uwsgi.reload()
            logger.info('UWSGI app reloaded')
except ImportError:
    logger.info('App NOT under uWSGI server')


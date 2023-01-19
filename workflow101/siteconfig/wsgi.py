"""
WSGI config for psmprj project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.contrib.staticfiles.handlers import StaticFilesHandler
# from whitenoise import WhiteNoise
from django.core.wsgi import get_wsgi_application
from siteconfig import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "siteconfig.settings")

# if settings.STATIC_ENABLE_WSGI_HANDLER:
#     application = StaticFilesHandler(get_wsgi_application())
# else:
#     application = get_wsgi_application()

application = get_wsgi_application()

# Production only, if NGINX not used...
# if not settings.DEBUG and not settings.NGINX_USE:
#     application = WhiteNoise(application, root=settings.STATIC_ROOT)


"""
WSGI config for django_template project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_template.settings")

from django.core.wsgi import get_wsgi_application

path = os.path.join(os.path.dirname(__file__), "../")
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'django_template.settings'

application = get_wsgi_application()

import os
import sys
from django.core.wsgi import get_wsgi_application

path = os.path.join(os.path.dirname(__file__), "../")
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'django_template.settings'

application = get_wsgi_application()

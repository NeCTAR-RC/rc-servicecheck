"""
WSGI config for nectar_monitor_rest project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

# path of where django app sits eg: /var/www/nectar-monitoring-rest/
root_path = '/var/www/nectar-monitoring-rest/'
if root_path not in sys.path:
    sys.path.append(root_path)
os.environ["DJANGO_SETTINGS_MODULE"] = 'nectar_monitor_rest.settings'

application = get_wsgi_application()

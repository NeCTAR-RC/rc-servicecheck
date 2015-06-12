"""
WSGI config for nectar_monitor_rest project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

# root path of where the django app is
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.append(root_path)
os.environ["DJANGO_SETTINGS_MODULE"] = 'nectar_monitor_rest.settings'

application = get_wsgi_application()

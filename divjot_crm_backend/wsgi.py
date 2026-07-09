import os
import sys

# CRITICAL PRODUCTION PATCH: Force mock psycopg2 for Gunicorn runtime
try:
    import psycopg
    sys.modules['psycopg2'] = psycopg
except ImportError:
    pass

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'divjot_crm_backend.settings')

application = get_wsgi_application()
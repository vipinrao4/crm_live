import os
from pathlib import Path
import sys

# Python 3.14 ke liye naye psycopg3 driver ko psycopg2 ke roop me register karne ka logic
try:
    import psycopg
    sys.modules['psycopg2'] = psycopg
except ImportError:
    pass

# Project ka Base Directory path configuration
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET KEY (Live deployment ke liye secure environment settings)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-divjot-crm-master-key-777-vipindrao')

# DEBUG MODE (Render par live chalane ke liye False rahega, local par True)
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ALLOWED HOSTS (Aapka Render link aur local host dono allowed hain)
ALLOWED_HOSTS = ['crm-live-pyzh.onrender.com', 'localhost', '127.0.0.1', '.onrender.com']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crm_core',  # Main functional application app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files ko Render par smooth chalane ke liye
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'divjot_crm_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI Application binding
WSGI_APPLICATION = 'divjot_crm_backend.wsgi.application'


# =====================================================================
# FINAL: EXPLICIT DIRECT VARIABLE MAPPING WITH FALLBACK
# =====================================================================
if os.environ.get('DB_NAME'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation architecture
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# Internationalization System Rules
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'  
USE_I18N = True
USE_TZ = True


# URL redirects logic
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'


# Static files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
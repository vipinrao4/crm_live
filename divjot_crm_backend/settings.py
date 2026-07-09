import os
from pathlib import Path

# Project ka Base Directory path configuration
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET KEY
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-divjot-crm-master-key-777-vipindrao')

# DEBUG MODE
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ALLOWED HOSTS
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
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.messages.MessageMiddleware',
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

WSGI_APPLICATION = 'divjot_crm_backend.wsgi.application'


# =====================================================================
# HAND-PARSING LIVE_DATABASE_URL / DATABASE_URL WITHOUT LIBRARIES
# =====================================================================
# Aapke screenshot ke mutabik jo url hai use hum manually break karenge
raw_url = os.environ.get('LIVE_DATABASE_URL', os.environ.get('DATABASE_URL', '')).strip()

if raw_url and ('://' in raw_url):
    try:
        # postgresql://divjot_db_user:pass@host/divjot_db ko split kar rahe hain
        trimmed_url = raw_url.split('://')[1]
        user_pass, host_db = trimmed_url.split('@')
        user, password = user_pass.split(':')
        
        if '/' in host_db:
            host_port, db_name = host_db.split('/')
        else:
            host_port, db_name = host_db, 'divjot_db'
            
        if ':' in host_port:
            host, port = host_port.split(':')
        else:
            host, port = host_port, '5432'
            
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': db_name,
                'USER': user,
                'PASSWORD': password,
                'HOST': host,
                'PORT': port,
            }
        }
    except Exception:
        # Kuch galat hua toh crash hone ke bajaye hardcoded fallback
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'divjot_db',
                'USER': 'divjot_db_user',
                'PASSWORD': 'VR9Uoc7Xl4CrOPuhCOIHXykEuACOscoi',
                'HOST': 'dpg-d97mpd3eo5us73a7tbb0-a',
                'PORT': '5432',
            }
        }
else:
    # Direct hardcoded fallback taaki koi error na aaye
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'divjot_db',
            'USER': 'divjot_db_user',
            'PASSWORD': 'VR9Uoc7Xl4CrOPuhCOIHXykEuACOscoi',
            'HOST': 'dpg-d97mpd3eo5us73a7tbb0-a',
            'PORT': '5432',
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
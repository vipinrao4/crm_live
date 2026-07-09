import os
from pathlib import Path
import dj_database_url

# Project ka Base Directory path configuration
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET KEY (Live deployment ke liye ekdum secure environment settings)
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
    'crm_core',  # Aapki main functional application app
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

ROOT_URLCONF = 'divjot_crm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Core templates path binding
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

WSGI_APPLICATION = 'divjot_crm.wsgi.application'


# =====================================================================
# FIXED: MASTER SQL (POSTGRESQL) CLOUD DATABASE SETUP
# =====================================================================
DATABASES = {
    'default': dj_database_url.config(
        # Render variable se URL uthayega, backup me aapka purana local SQLite chalega
        default=os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "db.sqlite3")}'),
        conn_max_age=600
    )
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
TIME_ZONE = 'Asia/Kolkata'  # India Standard Time configuration
USE_I18N = True
USE_TZ = True


# URL redirects logic for employee logs
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'


# Static files configuration rules (CSS, Images, JavaScript layout)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Storage engines for production deployments
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
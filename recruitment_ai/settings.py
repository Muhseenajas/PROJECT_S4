# settings.py

from decouple import Config, RepositoryEnv
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Correctly define env_path
env_path = os.path.join(BASE_DIR, '.env')

# Load .env explicitly
config = Config(RepositoryEnv(env_path))

# SECURITY
SECRET_KEY = 'django-insecure-recruitment-ai-secret-key-change-in-production'
DEBUG = True
ALLOWED_HOSTS = ['*']

# INSTALLED APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ROOT_URLCONF
ROOT_URLCONF = 'recruitment_ai.urls'

# TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
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

# WSGI
WSGI_APPLICATION = 'recruitment_ai.wsgi.application'

# DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# AUTH PASSWORD VALIDATORS
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# INTERNATIONALIZATION
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# STATIC FILES
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# MEDIA
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# LOGIN REDIRECTS
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# DEFAULT AUTO FIELD
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')                  # e.g., smtp.gmail.com
EMAIL_PORT = config('EMAIL_PORT', cast=int)        # e.g., 587
EMAIL_HOST_USER = config('EMAIL_HOST_USER')        # your Gmail
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')# your 16-char App Password
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool) # True
"""
Django settings for cryptoService project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0n#@y-#*rgd_mih%i233+vp#+bl6)&4vjbd0dm2xo87^#eh+2f'

# Development settings
DEBUG = True
ALLOWED_HOSTS = []

# Production settings
#DEBUG = False
#ALLOWED_HOSTS = ['*']

# Unlimited peristent db connections. I doubt this impacts our mongoengin connections though.
#CONN_MAX_AGE = None

# Application definition
INSTALLED_APPS = ('pythiaPrfService',  'django.contrib.sessions')
# )
#    'django.contrib.admin',
#    'django.contrib.auth',
#    'django.contrib.contenttypes',
#    'django.contrib.sessions',
#    'django.contrib.messages',
#    'django.contrib.staticfiles',

MIDDLEWARE_CLASSES = ()
ROOT_URLCONF = 'cryptoService.urls'
WSGI_APPLICATION = 'cryptoService.wsgi.application'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

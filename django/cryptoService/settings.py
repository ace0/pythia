"""
Django settings for cryptoService project.
"""

# Django requires that this be set, but Pythia uses it's own server secret key
# distinct from this one.
SECRET_KEY = '0n#@y-#*rgd_mih%i233+vp#+bl6)&4vjbd0dm2xo87^#eh+2f'

# Development settings
#DEBUG = True

# Production settings
DEBUG = False

INSTALLED_APPS = ('pythiaPrfService',)
MIDDLEWARE_CLASSES = ()
ROOT_URLCONF = 'cryptoService.urls'
WSGI_APPLICATION = 'cryptoService.wsgi.application'

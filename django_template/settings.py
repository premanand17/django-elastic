"""
Django settings for django_template project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

from django_template.settings_secret import *
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

sys.path.insert(0, os.path.join(BASE_DIR, 'django_template/local_apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

# fixtures used in defining db data for tests
FIXTURE_DIRS = os.path.join(BASE_DIR, 'django_template/local_apps/db/fixtures')

# 
# test runner for unmanaged db models and postgres schema to load
# when tests are run
TEST_RUNNER = 'db.scripts.testrunner.ManagedModelTestRunner'
TEST_DB_UNMANAGED_TABLES_SCHEMA_FILE = os.path.join(BASE_DIR, 'django_template/local_apps/db/scripts/public_schema.pgdump')

# Application definition
INSTALLED_APPS = (
#    'django.contrib.admin',
#    'django.contrib.auth',
#    'django.contrib.contenttypes',
#    'django.contrib.sessions',
#    'django.contrib.messages',
    'django.contrib.staticfiles',
    'db',
    'bands',
    'es',
    'genes',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
#    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'django_template.urls'

WSGI_APPLICATION = 'django_template.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "django_template/static"),
)


TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'django_template/templates/'),
)

# writes all request logging from the django.request logger to a local file
LOG_FILE = os.path.join(BASE_DIR, 'tmp/debug.log')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_FILE,
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

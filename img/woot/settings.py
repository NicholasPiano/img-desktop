# img.settings

# django

# util
import os
from datetime import timedelta
from os import mkdir
from os.path import abspath, basename, dirname, join, normpath, exists
from sys import path
import string
import json
import sys

########## TEST CONFIGURATION
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
########## END TEST CONFIGURATION


########## AUTH CONFIGURATION
AUTH_USER_MODEL = 'users.User'
########## END AUTH CONFIGURATION


########## ALLOWED HOSTS CONFIGURATION
ALLOWED_HOSTS = (
  'localhost',
)
########## END ALLOWED HOSTS CONFIGURATION


########## PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = dirname(abspath(__file__))

# Absolute filesystem path to the top-level project folder:
SITE_ROOT = dirname(DJANGO_ROOT)

# Site name:
SITE_NAME = basename(dirname(DJANGO_ROOT))

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)

DATA_ROOT = '/Volumes/transport/data/puzzle/'
########## END PATH CONFIGURATION


########## PASSWORD CONFIGURATION
ACCESS_ROOT = '/.djaccess/'
DB_ACCESS = 'img_db.json'
########## END PASSWORD CONFIGURATION


########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION


########## MANAGER CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
  ('Your name', 'youremail@domain.com'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
########## END MANAGER CONFIGURATION


########## GENERAL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = 'Europe/London'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
########## END GENERAL CONFIGURATION


########## MEDIA CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = normpath(join(DJANGO_ROOT, 'media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'
########## END MEDIA CONFIGURATION


########## STATIC FILE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = normpath(join(DJANGO_ROOT, 'assets'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
  normpath(join(DJANGO_ROOT, 'assets')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
  'django.contrib.staticfiles.finders.FileSystemFinder',
  'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
########## END STATIC FILE CONFIGURATION


########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = '7cj+(7x3%*2paowk2ks3581@cc9a=!q@$_3&y#j_a%5w7hau#6'
########## END SECRET CONFIGURATION


########## FIXTURE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
  normpath(join(DJANGO_ROOT, 'fixtures')),
)
########## END FIXTURE CONFIGURATION


########## TEMPLATE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
TEMPLATE_CONTEXT_PROCESSORS = (
  'django.contrib.auth.context_processors.auth',
  'django.core.context_processors.debug',
  'django.core.context_processors.i18n',
  'django.core.context_processors.media',
  'django.core.context_processors.static',
  'django.core.context_processors.tz',
  'django.contrib.messages.context_processors.messages',
  'django.core.context_processors.request',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
TEMPLATE_LOADERS = (
  'django.template.loaders.filesystem.Loader',
  'django.template.loaders.app_directories.Loader',
  'django.template.loaders.eggs.Loader',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
TEMPLATE_DIRS = (
  normpath(join(DJANGO_ROOT, 'templates')),
)
########## END TEMPLATE CONFIGURATION


########## MIDDLEWARE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
MIDDLEWARE_CLASSES = (
  # Use GZip compression to reduce bandwidth.
  'django.middleware.gzip.GZipMiddleware',

  # Django debug toolbar
  'debug_toolbar.middleware.DebugToolbarMiddleware',

  # Default Django middleware.
  'django.middleware.common.CommonMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
)
########## END MIDDLEWARE CONFIGURATION


########## URL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = '%s.urls' % SITE_NAME
########## END URL CONFIGURATION


########## APP CONFIGURATION
DJANGO_APPS = (
  # Default Django apps:
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.sites',
  'django.contrib.messages',
  'django.contrib.staticfiles',

  # Useful template tags:
  # 'django.contrib.humanize',

  # Admin panel and documentation:
  # 'django.contrib.admin',
  # 'django.contrib.admindocs',

  # flatpages for static pages
  # 'django.contrib.flatpages',
)

THIRD_PARTY_APPS = (
  # Asynchronous task scheduling
  # 'djcelery',

  # Static file management:
  # 'compressor',
)

LOCAL_APPS = (
  'apps.cell',
  'apps.expt',
  'apps.img',
  'apps.users',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
########## END APP CONFIGURATION


########## LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'filters': {
    'require_debug_false': {
      '()': 'django.utils.log.RequireDebugFalse'
    }
  },
  'handlers': {
    'mail_admins': {
      'level': 'ERROR',
      'filters': ['require_debug_false'],
      'class': 'django.utils.log.AdminEmailHandler'
    },
    'console': {
      'level': 'DEBUG',
      'class': 'logging.StreamHandler'
    }
  },
  'loggers': {
    'django.request': {
      'handlers': ['mail_admins', 'console'],
      'level': 'ERROR',
      'propagate': True,
    },
  }
}
########## END LOGGING CONFIGURATION


########## WSGI CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'wsgi.application'
########## END WSGI CONFIGURATION


########## COMPRESSION CONFIGURATION
# See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_ENABLED
COMPRESS_ENABLED = True

# See: http://django-compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_CSS_HASHING_METHOD
COMPRESS_CSS_HASHING_METHOD = 'content'

# See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_CSS_FILTERS
COMPRESS_CSS_FILTERS = [
    'compressor.filters.template.TemplateFilter',
]

# See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_JS_FILTERS
COMPRESS_JS_FILTERS = [
    'compressor.filters.template.TemplateFilter',
]

STATICFILES_FINDERS += (
  'compressor.finders.CompressorFinder',
)
########## END COMPRESSION CONFIGURATION


########## CELERY CONFIGURATION
from djcelery import setup_loader

CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend'

# : Only add pickle to this list if your broker is secured
# : from unwanted access (see userguide/security.html)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# See: http://celery.readthedocs.org/en/latest/configuration.html#celery-task-result-expires
CELERY_TASK_RESULT_EXPIRES = timedelta(minutes=30)

# See: http://docs.celeryproject.org/en/master/configuration.html#std:setting-CELERY_CHORD_PROPAGATES
CELERY_CHORD_PROPAGATES = True

# See: http://celery.github.com/celery/django/
setup_loader()

# rabbitmq: https://www.rabbitmq.com/man/rabbitmqctl.1.man.html
# celery: https://zapier.com/blog/async-celery-example-why-and-how/
########## END CELERY CONFIGURATION


########## FILE UPLOAD CONFIGURATION
FILE_UPLOAD_HANDLERS = (
  'django.core.files.uploadhandler.MemoryFileUploadHandler',
  'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)
########## END FILE UPLOAD CONFIGURATION


########## DATABASE CONFIGURATION
# load database details from database config file
db = {}
if os.path.exists(os.path.join(ACCESS_ROOT, DB_ACCESS)):
  with open(os.path.join(ACCESS_ROOT, DB_ACCESS)) as db_json:
    db = json.load(db_json)
else:
  print('Database access not defined. Please check {}'.format(os.path.join(ACCESS_ROOT, DB_ACCESS)))
  sys.exit()

# 1. start database server: ~$ pg_ctl start -D /usr/local/var/postgres/
# 2. connect to database: ~$ psql -U nicholaspiano postgres
# 3. check database server: ~$ pg_ctl status -D /usr/local/var/postgres/

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': db['name'],
    'USER': db['user'],
    'PASSWORD': db['pwd'],
    'HOST': db['host'], # Set to empty string for localhost.
    'PORT': db['port'], # Set to empty string for default.
  }
}
########## END DATABASE CONFIGURATION

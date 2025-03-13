"""
Django settings for elixirapp project.

Generated by 'django-admin startproject' using Django 1.8.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import datetime
import json
# import djcelery


# Prefix for environment variables settings.
ENV_NAMESPACE = "BIOTOOLS"


def getenv(key, default=None, castf=str, ns=ENV_NAMESPACE):
    """Helper function to retrieve namespaced environment variables."""
    value = os.environ.get('{ns}_{key}'.format(ns=ns, key=key), None)
    return castf(value) if value is not None else default


# CELERY SETTINGS
# REDIS_HOST = getenv('REDIS_HOST', 'localhost')
# REDIS_PORT = getenv('REDIS_PORT', '6379')
# REDIS_DB = getenv('REDIS_DB', '0')
# BROKER_URL = 'redis://{host}:{port}/{db}'.format(
#     host=REDIS_HOST,
#     port=REDIS_PORT,
#     db=REDIS_DB,
# )
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'

# CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
# CELERY_ALWAYS_EAGER = getenv('CELERY_ALWAYS_EAGER', True, castf=bool)

# djcelery.setup_loader()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "media_cdn")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# NOTE: This setting is currently overwritten by deployment_settings import
SECRET_KEY = getenv(
    'SECRET_KEY',
    '$a$$kkc_q040nqu&c9k=zshyc+x)%3-k3g7^ik8g$+lgx9#6!w'
)

# SECURITY WARNING: don't run with debug turned on in production!
# NOTE: This setting is currently overwritten by deployment_settings import
DEBUG = getenv('DEBUG', True, castf=bool)

ALLOWED_HOSTS = ['*']

# Separator character for setting multiple Elasticsearch RFC-1738 URLs.
ELASTIC_SEARCH_SEP = ';'

ELASTIC_SEARCH_URLS = getenv(
    'ELASTIC_SEARCH_URLS',
    ['http://localhost:9200'],
    castf=lambda v: v.split(ELASTIC_SEARCH_SEP)
)

ELASTIC_SEARCH_INDEX = 'elixir'
# Application definition

INSTALLED_APPS = (
    # 'super_inlines',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'elixir',
    'rest_framework',
    'rest_framework.authtoken',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'django_extensions',
    'rest_framework_simplejwt',
    # 'djcelery',
    # 'kombu.transport.django',
    'background_task'
)


MIDDLEWARE_CLASSES = (
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
#     'django.middleware.security.SecurityMiddleware',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'allauth.account.middleware.AccountMiddleware',
)

ROOT_URLCONF = 'elixirapp.urls'

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
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = getenv('WSGI_APPLICATION', 'elixirapp.wsgi.application')

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

SITE_ID = getenv('SITE_ID', 1, castf=int)

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
       'default':{
                'ENGINE':'django.db.backends.mysql',
                'HOST': getenv('MYSQL_HOST', '127.0.0.1'),
                'PORT': getenv('MYSQL_PORT', '3306'),
                'NAME': getenv('MYSQL_DB', 'elixir'),
                'USER': getenv('MYSQL_USER', 'elixir'),
                'PASSWORD': getenv('MYSQL_PASSWORD', '123'),
                # 'TEST': {
                #     'CHARSET': 'utf8'
                # },
                'OPTIONS': {
                    'charset': 'utf8mb4' 
                }
       }
}

# We change the collation in the first migration file '0001_initial'
# this allows for text differences like 'o' != 'ø', by default these are not differente they are treated as the same character and 'o' == 'ø' 
# we also define the wrong collation which is used by default so we can reverse migrations in case we need it for any reason
# this applies to MySQL, don't know if it applies to PostgreSQL which we should eventually use
DB_COLLATION = {
    'DEFAULT_BUT_WRONG': 'utf8mb4_0900_ai_ci',
    'CORRECT': 'utf8mb4_unicode_ci'
}

# Gmail Mail settings (don't usually work because Gmail requires extra security)
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = ''
# EMAIL_HOST_PASSWORD = ''
# EMAIL_USE_TLS = True
# DEFAULT_FROM_EMAIL = 'no-reply@local-bio.tools'

# Zoho Mail works (create an account)
# EMAIL_HOST = 'smtp.zoho.com'
# EMAIL_PORT = 465
# EMAIL_USE_SSL = True
# EMAIL_HOST_USER =  'zoho_email_here'
# EMAIL_HOST_PASSWORD = ''
# DEFAULT_FROM_EMAIL = 'no-reply@local-bio.tools'

EMAIL_HOST = getenv('EMAIL_HOST', 'smtp.zoho.com')
EMAIL_PORT = getenv('EMAIL_PORT', 465, castf=int)
EMAIL_USE_SSL = getenv('EMAIL_USE_SSL', True, castf=bool)
EMAIL_HOST_USER = getenv('EMAIL_HOST_USER', 'support@bio.tools')
DEFAULT_FROM_EMAIL = getenv('DEFAULT_FROM_EMAIL', 'support@bio.tools')

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = getenv('LANGUAGE_CODE', 'en-us')

TIME_ZONE = getenv('TIME_ZONE', 'UTC')

USE_I18N = getenv('USE_I18N', True, castf=bool)

USE_L10N = getenv('USE_L10N', True, castf=bool)

USE_TZ = getenv('USE_TZ', True, castf=bool)


STATIC_ROOT = getenv('STATIC_ROOT', '/elixir/application/frontend/static/')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = getenv('STATIC_URL', '/static/')

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        #'rest_frameworkework_xml.parsers.XMLParser',
        'rest_framework_yaml.parsers.YAMLParser',
         'elixir.parsers.XMLSchemaParser'
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        # 'rest_framework.renderers.AdminRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_xml.renderers.XMLRenderer',
        'rest_framework_yaml.renderers.YAMLRenderer',
        #'elixir.renderers.XMLSchemaRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': getenv('PAGE_SIZE', 50, castf=int),
    'NON_FIELD_ERRORS_KEY': 'general_errors'
}

# REST Auth
REST_AUTH = {
    'USER_DETAILS_SERIALIZER': 'elixir.serializers.UserSerializer',
    'PASSWORD_RESET_SERIALIZER': 'elixir.serializers.CustomPasswordResetSerializer',
}

# necessary for custom user validation
REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'elixir.serializers.UserRegisterSerializer'
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
ACCOUNT_ADAPTER = 'elixir.adapters.CustomDefaultAccountAdapter'
ACCOUNT_EMAIL_REQUIRED = getenv('ACCOUNT_EMAIL_REQUIRED', True, castf=bool)
ACCOUNT_USERNAME_REQUIRED = getenv(
    'ACCOUNT_USERNAME_REQUIRED',
    True,
    castf=bool,
)
ACCOUNT_AUTHENTICATION_METHOD = getenv(
    'ACCOUNT_AUTHENTICATION_METHOD',
    'username_email'
)
ACCOUNT_CONFIRM_EMAIL_ON_GET = getenv(
    'ACCOUNT_CONFIRM_EMAIL_ON_GET',
    True,
    castf=bool,
)
# NOTE: This setting is currently overwritten by deployment_settings import
URL_FRONT = getenv('URL_FRONT', 'http://localhost:8000/')
# NOTE: This setting is currently overwritten by deployment_settings import
DEPLOYMENT = getenv('DEPLOYMENT', 'dev')

RESERVED_URL_KEYWORDS = ['t', 'tool', 'user-list', 'edit-permissions', 'validate', 'f', 'function', 'o', 'ontology', 'used-terms', 'stats', 'env', 'sitemap.xml', 'd', 'domain', 'request', 'tool-list', 'w', 'register', 'edit-subdomain', 'subdomain', 'login', 'signup', 'reset-password', 'profile', 'requests', 'workflows', '404', 'documentation', 'about', 'schema', 'governance', 'roadmap', 'events', 'mail', 'faq', 'apidoc', 'changelog', 'helpdesk', 'projects']


# Settings for Github Ecosystem
# Ecosystem is off by default
GITHUB_ECOSYSTEM_ON = getenv('GITHUB_ECOSYSTEM_ON', False, castf=bool)
ADMIN_EMAIL_LIST = getenv('ADMIN_EMAIL_LIST', [], castf=json.loads)

# settings specific to deployment
try:
    from elixirapp.deployment_settings import *
except ImportError:
    print ("Could not import deployment settings")



# settings for blacklisted domains
BLACKLISTED_DOMAINS_LIST = getenv('BLACKLISTED_DOMAINS_LIST', [], castf=json.loads)

# settings blacklisting
try:
    from elixir.blacklisted_domains import *
except ImportError:
    print ("Could not import deployment settings")


DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

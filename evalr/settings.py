import os
import re
import sys

from django.utils.translation import gettext_lazy as _

environment_variables = {
    # SECURITY WARNING: don't run with debug turned on in production!
    'DEBUG': {'required': True, 'parser': bool},
    'SECRET_KEY': {'required': True, },
    'MEDIA_ROOT': {'default': 'uploads'},
    'COMPRESS_ROOT': {'default': 'static/production'},
    # set it to None = no limit to be able to send huge amount of data:
    'DATA_UPLOAD_MAX_NUMBER_FIELDS': {'required': True, 'parser': eval},
    # for uploads
    'UPLOAD_FOLDER_DOCUMENTS': {'default': 'documents'},

    # DATABASE_ENGINE = 'django.db.backends.postgresql_psycopg2' :
    'DATABASE_ENGINE': {'required': True, },
    'DATABASE_NAME': {'required': True, },
    'DATABASE_HOST': {'required': True, },
    'DATABASE_CLIENT_ENCODING': {'required': True, },
    'DATABASE_DATABASE': {'required': True, },
    'DATABASE_USER': {'required': True, },
    'DATABASE_PASSWORD': {'required': True, },
    'SOCIAL_AUTH_GITHUB_KEY': {'required': True, },
    'SOCIAL_AUTH_GITHUB_SECRET': {'required': True, },
    'SOCIAL_AUTH_TWITTER_KEY': {'required': True, },
    'SOCIAL_AUTH_TWITTER_SECRET': {'required': True, },
    'SOCIAL_AUTH_FACEBOOK_KEY': {'required': True, },
    'SOCIAL_AUTH_FACEBOOK_SECRET': {'required': True, },
    'SOCIAL_AUTH_FACEBOOK_SCOPE': {'required': True, 'parser': eval},
    'SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS': {'required': True,
                                                  'parser': eval},
    'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY': {'required': True, },
    'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET': {'required': True, },
}
settings = {}
errors = []
for var, infos in environment_variables.items():
    if var in os.environ:
        settings[var] = os.environ[var]
    elif 'default' in infos:
        settings[var] = infos['default']
    elif 'required' in infos:
        errors.append(var)
        continue
    if 'parser' in infos:
        settings[var] = infos['parser'](settings[var])

if len(errors):
    raise Exception("Please set the environment variables: "
                    "{}.".format(', '.join(errors)))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# make Windows-compatible
if sys.platform.lower().startswith('win'):
    os.environ["PATH"] = os.environ["PATH"] + os.pathsep + os.sep.join([
        '.', 'windows_binaries', 'libav-x86_64-w64-mingw32-20160507',
        'usr', 'bin'])

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

ADMINS = (('Olivier Pons', 'olivier.pons@hqf.fr'), )
DEFAULT_FROM_EMAIL = 'contact@hqf.fr'

WEBSITE_NAME = 'evalr'
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', f'{WEBSITE_NAME}', ]
# add everything on port 8000 and on my (own) company HQF:
ALLOWED_HOSTS = ALLOWED_HOSTS + \
                [f'{a}:8000' for a in ALLOWED_HOSTS] + \
                [f'{a}.hqf.fr' for a in ALLOWED_HOSTS] + \
                [f'{a}.hqf.fr:8000' for a in ALLOWED_HOSTS] + \
                [f'{a}.hqf.com:8000' for a in ALLOWED_HOSTS]

SECRET_KEY = settings['SECRET_KEY']
DEBUG = settings['DEBUG']

IGNORABLE_404_URLS = (
    re.compile(r'\.(php|cgi)$'),
    re.compile(r'.*phpmyadmin.*'),
    re.compile(r'^/apple-touch-icon.*\.png$'),
    re.compile(r'^/favicon\.ico$'),
    re.compile(r'^/robots\.txt$'),
)

if os.getcwd().startswith('/web/htdocs'):
    print("==> Production mode")
    SECURE_HSTS_SECONDS = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = True
    # ! offline => "manage.py compress" after "manage.py collectstatic"!!:
    COMPRESS_OFFLINE = True
    STATIC_ROOT = os.path.join(os.getcwd(), 'production')
else:
    print("http://evalr.hqf.fr:8000/fr/assistant/")
    print("http://evalr.hqf.fr:8000/fr/sessions/")
    # sendmail console backend
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_USE_LOCALTIME = True
    # fake email here:
    # https://docs.djangoproject.com/en/2.2/
    # topics/email/#s-configuring-email-for-development
    # python3 -m smtpd -n -c DebuggingServer localhost:1025
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
    'compressor',
    'app',
    'wizard',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
)

# https://docs.djangoproject.com/fr/2.2/ref/contrib/messages/
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

ROOT_URLCONF = 'evalr.urls'


# to pass a constant to any html template:
def context_processor_website_name(request):
    return {'website_name': WEBSITE_NAME}


TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR, 'templates')],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'social_django.context_processors.backends',
            'social_django.context_processors.login_redirect',
            'evalr.settings.context_processor_website_name'
        ],
    },
}, ]

WSGI_APPLICATION = 'evalr.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
    'default': {
        'ENGINE': settings['DATABASE_ENGINE'],
        'NAME': settings['DATABASE_NAME'],
        'HOST': settings['DATABASE_HOST'],
        'OPTIONS': {
            'client_encoding': 'UTF8',
            'database': settings['DATABASE_DATABASE'],
            'user': settings['DATABASE_USER'],
            'password': settings['DATABASE_PASSWORD'],
        },
    }
}

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.github.GithubOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# https://simpleisbetterthancomplex.com/
# tutorial/2016/10/24/how-to-add-social-login-to-django.html
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
  'fields': 'name, email, age_range'
}

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '120033307782-epmpr28telvcolh8osqp9l7' \
                                'pf33ij2vd.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'Pr7jEpyPT9TRt-sOGieXrd0s'

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/
LANGUAGE_CODE = 'en'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)

# base = 2621440 = 2.5MB of data in memory, I accept 25MB:
DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440*10
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440*10

# Aahahaha -> merci stackoverflow !
# https://docs.djangoproject.com/en/2.2/ref/settings/#append-slash
APPEND_SLASH = True

# Le truc de malade qu'il fallait trouver pour que la traduction soit
# prise en compte :
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)
# Uploaded files destination:
MEDIA_ROOT = settings['MEDIA_ROOT']
COMPRESS_ROOT = settings['COMPRESS_ROOT']
DATA_UPLOAD_MAX_NUMBER_FIELDS = settings['DATA_UPLOAD_MAX_NUMBER_FIELDS']
UPLOAD_FOLDER_DOCUMENTS = settings['UPLOAD_FOLDER_DOCUMENTS']

SITE_ID = 1
LOGIN_URL = 'auth_login'
LOGOUT_URL = 'auth_logout'
LOGIN_REDIRECT_URL = 'app_index'

# where to redirect after logout (ignored because I've made my own Logout view):
LOGOUT_REDIRECT_URL = '/'


# -----------------------------------------------------------------------------
# internationalization
LANGUAGES = (
    ('en', _('English')),
    ('fr', _('French')),
)

# region SOCIAL_AUTH_PIPELINE


# # Used to redirect the user once the auth process ended successfully.
# # The value of ?next=/foo is used if it was present:
# SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/oauth/login/github/'  # '/logged-in/'
# # URL where the user will be redirected in case of an error:
# SOCIAL_AUTH_LOGIN_ERROR_URL = '/login-error/'
# # Is used as a fallback for LOGIN_ERROR_URL:
# SOCIAL_AUTH_LOGIN_URL = '/login-url/'
# # Used to redirect new registered users, will be used in place of
# # SOCIAL_AUTH_LOGIN_REDIRECT_URL if defined.
# # Note that ?next=/foo is appended if present, if you want new users
# # to go to next, you’ll need to do it yourself:
# SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/new-users-redirect-url/'
# # Like SOCIAL_AUTH_NEW_USER_REDIRECT_URL but for new associated accounts
# # (user is already logged in). Used instead of SOCIAL_AUTH_LOGIN_REDIRECT_URL:
# SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = '/new-association-redirect-url/'
# # User is redirected to this URL when a social account is disconnected:
# SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/account-disconnected-redirect-url/'
# # Inactive users can be redirected to this URL when trying to authenticate:
# SOCIAL_AUTH_INACTIVE_USER_URL = '/inactive-user/'

# https://python-social-auth.readthedocs.io/en/latest/pipeline.html
SOCIAL_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social_core.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authoring thru. The uid is
    # the unique identifier of the given user in the provider.
    'social_core.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    'social_core.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    'social_core.pipeline.social_auth.social_user',

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    'social_core.pipeline.user.get_username',

    # Send a validation email to the user to verify its email address.
    # Disabled by default.
    # 'social_core.pipeline.mail.mail_validation',

    # Associates the current social details with another user account with
    # a similar email address. Disabled by default.
    # (!) I've enabled it -> when a user with same email exists he's merged (!)
    'social_core.pipeline.social_auth.associate_by_email',

    # Create a user account if we haven't found one yet.
    'social_core.pipeline.user.create_user',

    # Create the record that associates the social account with the user.
    'social_core.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the vales
    # specified by settings (and the default ones like access_token, etc).
    'social_core.pipeline.social_auth.load_extra_data',

    # Update the user record with any changed info from the auth service.
    'social_core.pipeline.user.user_details',
)
# endregion

# -----------------------------------------------------------------------------
# after trying "manage.py check --deploy" I've added those suggestions:
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
# When I set this I cant login:
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True

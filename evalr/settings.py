import ipaddress
import os
import re
import sys
from pathlib import Path
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from socket import gethostname, gethostbyname, gethostbyname_ex

from collections.abc import Mapping

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# region -- phones constants --
PHONE_ACCEPTED_FORMAT = "FR"
# endregion


# region - custom settings (to put in environment settings) -
class LazyDict(Mapping):
    def __init__(self, *args, **kw):
        self._raw_dict = dict(*args, **kw)

    def __getitem__(self, key):
        if key.startswith('#'):
            func, arg = self._raw_dict.__getitem__(key)
            return func(arg)
        return self._raw_dict.__getitem__(key)

    def __iter__(self):
        return iter(self._raw_dict)

    def __len__(self):
        return len(self._raw_dict)


settings = {}
errors = []


def parsers_str(error_message_if_doesnt_exist):
    return [str, lambda v: (settings['DEBUG'] is True) or Path(v).is_dir(),
            error_message_if_doesnt_exist]


def parsers_array_of_str(error_message):
    return [eval,
            lambda tab: isinstance(tab, list) and all([
                isinstance(x, str) for x in tab]),
            error_message]  # ! array of str


def conf_ignore_if_sqlite():
    return {
        'default': 'None',
        'parsers': [
            str,
            lambda v:
            (isinstance(v, str) and v != '') or
            (v is None and 'sqlite' in settings['DATABASE_ENGINE']),
            _("Your database isn't sqlite, this var must be configured")
        ]
    }


environment_variables = LazyDict({
    # SECURITY WARNING: don't run with debug turned on in production!
    'DEBUG': {'required': True,
              'parsers': [eval, lambda v: isinstance(v, bool)]},
    'SECRET_KEY': {'required': True, },
    'MEDIA_ROOT': {'default': 'uploads'},
    'STATIC_ROOT': {
        'default': './production_static_files',
        'parsers': parsers_str("Production folder doesn't exist.")},
    'COMPRESS_ROOT': {
        'default': './production_static_files/compress',
        'parsers': parsers_str("Compress production folder doesn't exist.")},
    # when set to None = no limit to be able to send huge amount of data:
    'DATA_UPLOAD_MAX_NUMBER_FIELDS': {
        'required': True,
        'parsers': [eval, lambda v: v is None or isinstance(v, int)]},
    # for uploads
    'UPLOAD_FOLDER_DOCUMENTS': {'default': 'documents'},
    'UPLOAD_FOLDER_CHATS_DOCUMENT': {'default': 'chats/documents'},
    'UPLOAD_FOLDER_IMAGES': {'default': 'images'},
    'THUMBNAIL_SUBDIRECTORY': {'default': 'th'},
    'THUMBNAIL_DIMENSIONS': {
        'default': '(1125, 2436)',  # iPhone X resolution
        'parsers': [eval, lambda v: (type(v) is tuple) and len(v) == 2]},

    # https://docs.djangoproject.com/en/dev/ref/settings/
    'ALLOWED_HOSTS': {
        'default': '[]', 'required': True,  # default = no hosts
        'parsers': parsers_array_of_str(_("ALLOWED_HOSTS = list of str only!"))},
    'INTERNAL_IPS': {
        'default': '["127.0.0.1", ]', 'required': True,
        'parsers': parsers_array_of_str(_("INTERNAL_IPS = list of str only!"))},

    # DATABASE_ENGINE = 'django.db.backends.postgresql_psycopg2' :
    'DATABASE_ENGINE': {'default': 'django.db.backends.sqlite3', },
    'DATABASE_NAME': {'default': os.path.join(BASE_DIR, 'db.sqlite3'), },
    'DATABASE_HOST': conf_ignore_if_sqlite(),
    'DATABASE_CLIENT_ENCODING': conf_ignore_if_sqlite(),
    'DATABASE_DATABASE': conf_ignore_if_sqlite(),
    'DATABASE_USER': conf_ignore_if_sqlite(),
    'DATABASE_PASSWORD': conf_ignore_if_sqlite(),

    'SOCIAL_AUTH_GITHUB_KEY': {'required': True, },
    'SOCIAL_AUTH_GITHUB_SECRET': {'required': True, },
    'SOCIAL_AUTH_TWITTER_KEY': {'required': True, },
    'SOCIAL_AUTH_TWITTER_SECRET': {'required': True, },
    'SOCIAL_AUTH_FACEBOOK_KEY': {'required': True, },
    'SOCIAL_AUTH_FACEBOOK_SECRET': {'required': True, },
    'SOCIAL_AUTH_FACEBOOK_SCOPE': {
        'required': True,
        'parsers': parsers_array_of_str(
            _("SOCIAL_AUTH_FACEBOOK_SCOPE = list of str only!"))},
    'SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS': {'required': True,
                                                  'parsers': [str, eval]},
    'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY': {'required': True, },
    'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET': {'required': True, },
})


def parse_var(var, infos):
    global settings
    if var in os.environ:
        settings[var] = os.environ[var]
    elif 'default' in infos:
        settings[var] = infos['default']
    elif 'required' in infos:
        errors.append(var)
        return
    if 'parsers' in infos:
        parsers = infos['parsers']
        if var not in settings:
            raise Exception(f"{var}: variable not set in environment, and "
                            "has not 'default' or 'required' value")
        # ! parsers functions: 0 = convert, 1 = validate conversion, 2 = error:
        try:
            settings[var] = parsers[0](settings[var])
        except TypeError:
            raise Exception(f"{var}: conversion error using {parsers[0]}")

        if len(parsers) > 1:
            if not parsers[1](settings[var]):  # should not continue:
                if len(parsers) > 2:
                    raise Exception(f'{var=} : {parsers[2]}')
                raise Exception(f'Unexpected conversion for variable {var}')


# first parse debug then *AFTER* parse all other variables
for var_name, var_infos in environment_variables.items():
    if var_name == 'DEBUG':
        parse_var(var_name, var_infos)

for var_name, var_infos in environment_variables.items():
    if var_name != 'DEBUG':
        parse_var(var_name, var_infos)

if len(errors):
    raise Exception("Please set the environment variables: "
                    "{}.".format(', '.join(errors)))

MEDIA_ROOT = settings['MEDIA_ROOT']
COMPRESS_ROOT = settings['COMPRESS_ROOT']
SECRET_KEY = settings['SECRET_KEY']
DEBUG = settings['DEBUG']
DATA_UPLOAD_MAX_NUMBER_FIELDS = settings['DATA_UPLOAD_MAX_NUMBER_FIELDS']
UPLOAD_FOLDER_DOCUMENTS = settings['UPLOAD_FOLDER_DOCUMENTS']
UPLOAD_FOLDER_CHATS_DOCUMENT = settings['UPLOAD_FOLDER_CHATS_DOCUMENT']
UPLOAD_FOLDER_IMAGES = settings['UPLOAD_FOLDER_IMAGES']
THUMBNAIL_SUBDIRECTORY = settings['THUMBNAIL_SUBDIRECTORY']
THUMBNAIL_DIMENSIONS = settings['THUMBNAIL_DIMENSIONS']
ALLOWED_HOSTS = settings['ALLOWED_HOSTS']
INTERNAL_IPS = settings['INTERNAL_IPS']
STATIC_ROOT = settings['STATIC_ROOT']
# endregion - custom settings (to put in environment settings) -

# make Windows-compatible
if sys.platform.lower().startswith('win'):
    os.environ["PATH"] = os.environ["PATH"] + os.pathsep + os.sep.join([
        '.', 'windows_binaries', 'libav-x86_64-w64-mingw32-20160507',
        'usr', 'bin'])

# https://stackoverflow.com/a/40665906/106140
ALLOWED_HOSTS += [gethostname(), '127.0.0.1', 'localhost', ] + \
                 gethostbyname_ex(gethostname())[2]
ADMINS = (
    ('Olivier Pons', 'olivier.pons@hqf.fr'),
)
if DEBUG:
    WEBSITE_NAME = 'evalr'
    ALLOWED_HOSTS += [WEBSITE_NAME]
    # add my (own) company HQF for debugging purposes:
    to_add = []
    for e in ['com', 'fr']:
        for h in ALLOWED_HOSTS:
            try:
                ipaddress.ip_address(h)
            except ValueError:  # add only *not* IP's like '':
                without_ext = '.'.join(h.split('.')[:-1])
                if without_ext and '.hqf' not in without_ext:
                    to_add.append('{}.hqf.{}'.format(without_ext, e))
    if len(to_add):
        ALLOWED_HOSTS += to_add
    # add everything on port 8000:
    for i in range(8000, 8003):
        ALLOWED_HOSTS += [f'{a}:{i}' for a in ALLOWED_HOSTS]
        INTERNAL_IPS += [f'{a}:{i}' for a in INTERNAL_IPS]

    # sendmail console backend
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_USE_LOCALTIME = True
    # fake email here:
    # https://docs.djangoproject.com/en/2.2/
    # topics/email/#s-configuring-email-for-development
    # python3 -m smtpd -n -c DebuggingServer localhost:1025
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025

    print("http://evalr.hqf.fr:8000/fr/assistant/")
    print("http://evalr.hqf.fr:8000/fr/sessions/")
else:
    WEBSITE_NAME = 'evalr.com'
    # specific to mc-media
    ALLOWED_HOSTS = ALLOWED_HOSTS + ['.mc-media.com', ]
    SECURE_HSTS_SECONDS = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = True
    # ! offline => "manage.py compress" after "manage.py collectstatic"!!:
    COMPRESS_OFFLINE = True
    STATIC_ROOT = os.path.join(os.getcwd(), 'production')
    print("==> Production mode")

SERVER_EMAIL = f'root@{WEBSITE_NAME}'
DEFAULT_FROM_EMAIL = f'contact@{WEBSITE_NAME}'

ALLOWED_HOSTS = tuple(set(ALLOWED_HOSTS))
IGNORABLE_404_URLS = (
    re.compile(r'\.(php|cgi)$'),
    re.compile(r'.*phpmyadmin.*'),
    re.compile(r'^/apple-touch-icon.*\.png$'),
    re.compile(r'^/favicon\.ico$'),
    re.compile(r'^/robots\.txt$'),
)

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
    'core',
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
DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440 * 10
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440 * 10

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

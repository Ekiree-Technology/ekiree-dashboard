"""
Django settings for poetfolio project.

Generated by 'django-admin startproject' using Django 2.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

from dotenv import find_dotenv, load_dotenv

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "poetfolio", "templates")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
import getpass

username = getpass.getuser()
etcpath = "/home/" + username + "/etc"

SECRET_KEY = os.environ.get("POETFOLIO_SECRET_KEY") or (
    "yN5i8gTkby3KiljNK82UTJ0Pd9Znek6TZqhhclZz9E3TCZaJKz"
)

# SECURITY WARNING: don't run with debug turned on in production!
if os.environ.get("POETFOLIO_PRODUCTION"):
    DEBUG = False
else:
    DEBUG = True

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")


# Application definition

INSTALLED_APPS = [
    "ed.apps.EdConfig",
    "vita.apps.VitaConfig",
    "reports.apps.ReportsConfig",
    "siteconfig.apps.SiteconfigConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    #'django.static.jquery',
    "phonenumber_field",
    "bootstrap4",
    "django_ckeditor_5",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "poetfolio.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            "ed/templates",
            "vita/templates",
            "poetfolio/templates",
            "reports/templates",
            TEMPLATE_DIR,
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "poetfolio.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

# DATABASES = {
# 'default': {
#    	'ENGINE': 'django.db.backends.sqlite3',
#    	'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
# }
# }

DB_NAME = os.environ.get("POETFOLIO_DB_NAME") or "poetfolio_dev"
DB_USER = os.environ.get("POETFOLIO_DB_USER") or "poetfolio"
DB_PASSWORD = os.environ.get("POETFOLIO_DB_PASSWORD") or "devdevdev"
DB_HOST = os.environ.get("POETFOLIO_DB_HOST") or "localhost"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": "3306",
        "TEST": {
            "NAME": "test_poetfolio",
        },
        "OPTIONS": {"charset": "utf8"},
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/Los_Angeles"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static and Media Files
USE_S3 = os.environ.get("USE_S3") == "TRUE"

if USE_S3:
    MEDIA_CONFIG = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": os.environ.get("S3_BUCKET_NAME"),
            "default_acl": "private",
            "signature_version": "s3v4",
            "endpoint_url": os.environ.get("S3_BUCKET_ENDPOINT"),
            "access_key": os.environ.get("S3_ACCESS_KEY"),
            "secret_key": os.environ.get("S3_SECRET_KEY"),
        },
    }
else:
    MEDIA_CONFIG = {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    }
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
# https://https://whitenoise.readthedocs.io/en/latest/django.html
import getpass

username = getpass.getuser()
# Location of static files within applications in Django source code
STATIC_URL = "/static/"
# Location of static files the server should pull from while running
STATIC_ROOT = os.environ.get("POETFOLIO_STATIC") or "/app/static"
WHITENOISE_INDEX_FILE = "True"

# Default Media Files
# Location of media files within appllications  in Django source Code
MEDIA_URL = "/media/"
# Location of media files the server should pull from while running
MEDIA_ROOT = os.environ.get("POETFOLIO_MEDIA") or ("/home/" + username + "/media")

STORAGES = {
    "default": MEDIA_CONFIG,
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# login/logout
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Emails
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("POETFOLIO_EMAIL_HOST") or ""
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("POETFOLIO_EMAIL_USER") or ""
EMAIL_HOST_PASSWORD = os.environ.get("POETFOLIO_EMAIL_PASSWORD") or ""
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = "scholars@whittier.edu"
SECURITY_EMAIL_SENDER = DEFAULT_FROM_EMAIL
EMAIL_SUBJECT_PREFIX = "[Dashboard] "
SERVER_EMAIL = "scholars@whittier.edu"
LOGIN_URL = "/login/"

# PhoneNumber
PHONENUMBER_DEFAULT_REGION = "US"

# Forces django to use temporary files for uploads
FILE_UPLOAD_HANDLERS = ["django.core.files.uploadhandler.TemporaryFileUploadHandler"]

# Set default Values when creating objects
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Load environment definition file
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# CKeditor 5 settings
customColorPalette = [
    {"color": "hsl(4, 90%, 58%)", "label": "Red"},
    {"color": "hsl(340, 82%, 52%)", "label": "Pink"},
    {"color": "hsl(291, 64%, 42%)", "label": "Purple"},
    {"color": "hsl(262, 52%, 47%)", "label": "Deep Purple"},
    {"color": "hsl(231, 48%, 48%)", "label": "Indigo"},
    {"color": "hsl(207, 90%, 54%)", "label": "Blue"},
]

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
            "imageUpload",
        ],
    },
    "extends": {
        "blockToolbar": [
            "paragraph",
            "heading1",
            "heading2",
            "heading3",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "blockQuote",
        ],
        "toolbar": [
            "heading",
            "|",
            "outdent",
            "indent",
            "|",
            "bold",
            "italic",
            "link",
            "underline",
            "strikethrough",
            "code",
            "subscript",
            "superscript",
            "highlight",
            "|",
            "codeBlock",
            "sourceEditing",
            "insertImage",
            "bulletedList",
            "numberedList",
            "todoList",
            "|",
            "blockQuote",
            "imageUpload",
            "|",
            "fontSize",
            "fontFamily",
            "fontColor",
            "fontBackgroundColor",
            "mediaEmbed",
            "removeFormat",
            "insertTable",
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "|",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
                "imageStyle:alignCenter",
                "imageStyle:side",
                "|",
            ],
            "styles": [
                "full",
                "side",
                "alignLeft",
                "alignRight",
                "alignCenter",
            ],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties",
            ],
            "tableProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
            "tableCellProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
            ]
        },
    },
    "list": {
        "properties": {
            "styles": "true",
            "startIndex": "true",
            "reversed": "true",
        }
    },
}

# Define a constant in settings.py to specify file upload permissions
CKEDITOR_5_FILE_UPLOAD_PERMISSION = (
    "staff"  # Possible values: "staff", "authenticated", "any"
)

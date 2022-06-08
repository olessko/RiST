"""
Django settings for rstt project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
# import environ


# env = environ.Env(
#     # set casting, default value
#     DEBUG=(bool, False)
# )

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
DATASETS_IN = BASE_DIR / 'datasets_in'
STATIC_URL = '/static/'
STATICFILES_DIRS = (BASE_DIR / 'static',)
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/data_sets/'
MEDIA_ROOT = BASE_DIR / 'data_sets'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-k2$n2pnd9^3d%14pxn)#4-#u9g&&e%fh39k(cq!9yl1+_6zy)r'

# reading .env file
# environ.Env.read_env(BASE_DIR / '.env')

# SECRET_KEY = env.str('SECRET_KEY')

# DEBUG = env.bool('DEBUG', True)
# PRODACTION_MODE = env.bool('PRODACTION_MODE', False)
DEBUG = True
PRODACTION_MODE = False


ALLOWED_HOSTS = ['127.0.0.1',
                 'risk-stress-test-tools.herokuapp.com']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'baseapp',
    'accounts'
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rstt.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'staticfiles': 'django.templatetags.static',
            }
        },
    },
]

WSGI_APPLICATION = 'rstt.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

if PRODACTION_MODE == 'heroku':
    import dj_database_url

    DATABASES = {
        'default': dj_database_url.config()
    }

elif PRODACTION_MODE == 'aws':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            # 'NAME': env.str('DB_NAME'),
            # 'USER': env.str('DB_USER'),
            # 'PASSWORD': env.str('DB_PASSWORD'),
            # 'HOST': env.str('DB_HOST'),
            # 'PORT': env.int('DB_PORT'),
            # 'MAX_CONN_AGE': 600,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'accounts:login'
BASE_URL = "baseapp:home"

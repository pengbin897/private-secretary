from datetime import timedelta
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

ALLOWED_HOSTS = ['*']

ROOT_URLCONF = 'system.urls'

SECRET_KEY = 'pengbin119'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',

    'system',      # 处理应用请求的后端
    'superadmin',  # 后台管理控制台
    'assistant',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}

STATIC_URL = '/admin-static/'

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    # 'system.middleware.FormatResponseMiddleware'
]

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    'OPTIONS': {
        'context_processors':[
            'django.contrib.messages.context_processors.messages',
            'django.contrib.auth.context_processors.auth',
            'django.template.context_processors.request',
        ],
        'loaders': [
            'django.template.loaders.app_directories.Loader',
        ],
    }
}]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'system.auth.CustomJWTAuthentication',
        'system.auth.WexinTokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60*6),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'UPDATE_LAST_LOGIN': True,  # 更新最后登录时间
    'TOKEN_OBTAIN_SERIALIZER': 'system.auth.CustomTokenObtainSerializer',
    'TOKEN_REFRESH_SERIALIZER': 'system.auth.CookieTokenRefreshSerializer'
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': os.environ.get('FILE_LOG_LEVEL'),
            'class': 'logging.FileHandler',
            'filename': os.environ.get('LOG_FILE'),
            'formatter': 'simple',
        }
    },
    'formatters': {
        "simple": {
            "format": "{asctime} {name}:{lineno} [{levelname}] - {message}",
            "style": "{",
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if os.environ.get('DEV_MODE') else 'INFO',
        },
        'ninetype': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if os.environ.get('DEV_MODE') else 'INFO',
        },
        'digishow': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if os.environ.get('DEV_MODE') else 'INFO',
        },
        'superadmin': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if os.environ.get('DEV_MODE') else 'INFO',
        },
        'system': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if os.environ.get('DEV_MODE') else 'INFO',
        },
        'lgtools': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if os.environ.get('DEV_MODE') else 'INFO',
        },
    },
}


import os

from .base import *

DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

db_using = os.getenv("DB_USING", "postgres").lower()

if db_using == "postgres":
    # ------------------- PostgreSQL Database Configuration ------------------->
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", ""),
            "USER": os.environ.get("DB_USER", ""),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", ""),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }
    # ------------------- PostgreSQL Database Configuration ------------------->

elif db_using == "mysql":
    # ------------------- MySQL Configuration ------------------->

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get("DB_NAME", ""),
            "USER": os.environ.get("DB_USER", ""),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", ""),
            "PORT": os.environ.get("DB_PORT", "3306"),
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
        }
    }

    # ------------------- MySQL Configuration ------------------->

else:
    # ------------------ Default Database Configuration ------------------->
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
    # ------------------ Default Database Configuration ------------------->


# ------------------- Static and Media Files Configuration ------------------->


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ------======= CORS settings =======------
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")


# ------------------- Security  ------------------->
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# ------------------- Logging Configuration Override ------------------->
if 'LOGGING' in globals():
    LOGGING['handlers']['console']['level'] = 'WARNING'

    try:
        LOGS_PATH.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    LOGGING['handlers']['production_file'] = {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': LOGS_PATH / 'production.log',
        'maxBytes': 1024*1024*50,  # 50 MB
        'backupCount': 10,
        'formatter': 'detailed',
    }
    LOGGING['loggers']['django']['handlers'] = ['production_file', 'file_error']
    LOGGING['loggers']['apps']['handlers'] = ['production_file']


# ------------------- Monitoring Configuration ------------------->
MONITOR_SLOW_QUERIES = True
SLOW_QUERY_THRESHOLD = 0.5

# ------------------- Email Configuration Override ------------------->
# *******  IN  FUTURE ********

# ------------------- Database Backup Configuration ------------------->
# *******  IN  FUTURE ********







# ------------------- Caching Configuration ------------------->
# REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": REDIS_URL,
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#             "CONNECTION_POOL_KWARGS": {
#                 "max_connections": 20,
#                 "retry_on_timeout": True,
#             }
#         },
#         "KEY_PREFIX": "core_cache",
#         # 5 minutes default
#         "TIMEOUT": int(os.getenv("CACHE_TTL", "300")),
#     }
# }




# ------------------- Production Validation ------------------->
# Always required
required_env_vars = ['SECRET_KEY', 'ALLOWED_HOSTS']

if db_using in ('postgres', 'mysql'):
    required_env_vars.extend(['DB_NAME', 'DB_USER', 'DB_PASSWORD'])

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

if len(os.getenv('SECRET_KEY', '')) < 50:
    raise ValueError("SECRET_KEY must be at least 50 characters long in production")


# ------------------------------------------------------------------
# Production-specific API responses are JSON only
# ------------------------------------------------------------------
try:
    from .configurations.restapi import REST_FRAMEWORK as _REST_CONFIG
    _rf = dict(_REST_CONFIG)
    _rf['DEFAULT_RENDERER_CLASSES'] = [
        'rest_framework.renderers.JSONRenderer',
    ]
    REST_FRAMEWORK = _rf
except Exception:
    # Fallback:
    REST_FRAMEWORK = {
        'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer',
        ]
    }
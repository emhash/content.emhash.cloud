from .base import *

DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
SECRET_KEY = os.getenv("SECRET_KEY", "INSECURE-DEFAULT-LOCAL")


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




# ------------------- Static and Media Files ------------------->
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Static files 
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]


# ------------------- Development Tools ------------------->
if 'django_extensions' in INSTALLED_APPS:
    SHELL_PLUS_PRINT_SQL = os.getenv("SHELL_PLUS_PRINT_SQL", "False").lower() in ("true", "1", "t")
    SHELL_PLUS_PRINT_SQL_TRUNCATE = 1000

# ------------------- Email Configuration Override ------------------->

# ------------------- Security Relaxation for Development ------------------->
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CORS_ALLOW_ALL_ORIGINS = True

print("##"*20)
print("Using DB: ", db_using)
print("Envoinrment: LOCAL")
print("##"*20)

# ------------------- Development Logging Override ------------------->
# Enhanced logging for development
if 'LOGGING' in globals():
    # Enable more verbose console logging in development
    LOGGING['handlers']['console']['level'] = 'DEBUG'
    LOGGING['handlers']['console']['formatter'] = 'detailed'
    
    # Enable SQL logging if requested
    if os.getenv("ENABLE_DB_LOGGING", "False").lower() in ("true", "1", "t"):
        LOGGING['loggers']['django.db.backends']['handlers'] = ['console', 'file_db']
        LOGGING['loggers']['django.db.backends']['level'] = 'DEBUG'

# ------------------- Development Environment Validation ------------------->
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

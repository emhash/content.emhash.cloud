import os
from pathlib import Path

# Get log settings from environment
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "True").lower() in ("true", "1", "t")
LOG_DIR = os.getenv("LOG_DIR", "logs")
DISABLE_SERVER_LOGS = os.getenv("DISABLE_SERVER_LOGS", "False").lower() in ("true", "1", "t")

# Create logs directory if it doesn't exist
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
LOGS_PATH = BASE_DIR / LOG_DIR
LOGS_PATH.mkdir(exist_ok=True)

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
        'server': {
            'format': '{message}',
            'style': '{',
        },
        'detailed': {
            'format': '{asctime} | {levelname:8} | {name:20} | {module:15} | {funcName:15} | {lineno:4} | {message}',
            'style': '{',
        },
        'json': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "module": "%(module)s", "message": "%(message)s"}',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'console_clean': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'server',
        },
        'console_detailed': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
            'filters': ['require_debug_true'],
        },
        'file_general': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_PATH / 'django.log',
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 5,
            'formatter': 'detailed',
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_PATH / 'error.log',
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 5,
            'formatter': 'detailed',
        },
        'file_security': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_PATH / 'security.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'detailed',
        },
        'file_db': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_PATH / 'database.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 3,
            'formatter': 'detailed',
        },
        'file_api': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_PATH / 'api.log',
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 5,
            'formatter': 'detailed',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'verbose',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_general'] if LOG_TO_FILE else ['console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file_error', 'mail_admins'] if LOG_TO_FILE else ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.server': {
            'handlers': [] if DISABLE_SERVER_LOGS else (['console_clean'] if LOG_TO_FILE else ['console_clean']),
            'level': 'WARNING' if DISABLE_SERVER_LOGS else 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['file_security'] if LOG_TO_FILE else ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['file_db'] if (LOG_TO_FILE and os.getenv("ENABLE_DB_LOGGING", "False").lower() in ("true", "1", "t")) else [],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console_detailed', 'file_general'] if LOG_TO_FILE else ['console_detailed'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'api': {
            'handlers': ['console', 'file_api'] if LOG_TO_FILE else ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'payment': {
            'handlers': ['console', 'file_general', 'file_error'] if LOG_TO_FILE else ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'authentication': {
            'handlers': ['console', 'file_security'] if LOG_TO_FILE else ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Additional logging configuration for production
if os.getenv("DJANGO_ENV") == "production":
    # In production, reduce console logging and focus on file logging
    LOGGING['loggers']['django']['handlers'] = ['file_general', 'file_error']
    LOGGING['loggers']['apps']['handlers'] = ['file_general']
    LOGGING['loggers']['api']['handlers'] = ['file_api']
    
    LOGGING['handlers']['file_json'] = {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': LOGS_PATH / 'application.json',
        # 20 MB
        'maxBytes': 1024*1024*20,
        'backupCount': 10,
        'formatter': 'json',
    } 
import os
DJANGO_ENV = os.getenv("DJANGO_ENV", "local")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

# SECURITY HEADERS
if DJANGO_ENV == "production":
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
else:
    SECURE_SSL_REDIRECT = False
    SECURE_PROXY_SSL_HEADER = None

# HSTS (HTTP Strict Transport Security)
if DJANGO_ENV == "production":
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    SECURE_HSTS_SECONDS = 0

# Content Security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Frame Options
X_FRAME_OPTIONS = "DENY"

# SESSION SECURITY
SESSION_COOKIE_SECURE = DJANGO_ENV == "production"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True

# Session engine (consider using cache-based sessions for better performance)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# CSRF PROTECTION
CSRF_COOKIE_SECURE = DJANGO_ENV == "production"
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False
CSRF_COOKIE_AGE = 31449600  # 1 year

if DJANGO_ENV == "production":
    CSRF_TRUSTED_ORIGINS = [
        origin.strip() for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()
    ]


else:
    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

# CORS CONFIGURATION
CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in os.getenv("CORS_ALLOWED_ORIGINS", 
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080").split(",") 
    if origin.strip()
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False 

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# DATA UPLOAD LIMITS
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000
FILE_UPLOAD_PERMISSIONS = 0o644

ADMIN_URL = os.getenv("ADMIN_URL", "admin/")
ALLOWED_HOSTS = [
    host.strip() for host in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") 
    if host.strip()
]

# ============================================================================
# SECURITY MIDDLEWARE SETTINGS
# ============================================================================

# CSP_DEFAULT_SRC = ("'self'",)
# CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com")
# CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com")
# CSP_IMG_SRC = ("'self'", "data:", "https:")
# CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")

# # Security logging
# SECURITY_LOG_FAILED_LOGINS = True
# SECURITY_LOG_SUCCESSFUL_LOGINS = DJANGO_ENV == "production"

# ============================================================================
# RATE LIMITING (if using django-ratelimit or similar)
# ============================================================================

# RATELIMIT_ENABLE = os.getenv("RATE_LIMIT_ENABLE", "True").lower() in ("true", "1", "t")
# RATELIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

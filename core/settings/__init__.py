import os

ENVIRONMENT = os.environ.get("DJANGO_ENV", "local")

if ENVIRONMENT == "production":
    from .production import *
else:
    from .local import *

import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv(override=False)
except Exception:
    pass

settings_module = (
    os.getenv("DJANGO_SETTINGS_MODULE")
    or os.getenv("SETTINGS_MODULE")
    or "core.settings.production"
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
print(f"#####>> MODULE: {settings_module} <<#####")

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    execute_from_command_line(sys.argv)

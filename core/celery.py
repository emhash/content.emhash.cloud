import os
from celery import Celery
from celery.schedules import crontab

# ---------------------------------
# ======== configuration =========
# ---------------------------------
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.production')

app = Celery('patchping')

# ---------------------------------
# ======== configuration =========
# ---------------------------------
app.config_from_object('django.conf:settings', namespace='CELERY')

# ---------------------------------
# ======== Load task modules =========
# ---------------------------------
app.autodiscover_tasks()

# ---------------------------------
# ======== periodic tasks =========
# ---------------------------------
app.conf.beat_schedule = {
    # periodic tasks if needed
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
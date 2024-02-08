import os

from celery import Celery

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "first_test.django.settings"
)

app = Celery("first-test")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

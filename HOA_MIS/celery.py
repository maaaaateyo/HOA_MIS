import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HOA_MIS.settings')  # Adjust as necessary
app = Celery('HOA_MIS')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
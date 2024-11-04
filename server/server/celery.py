from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

app = Celery('server')


app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


app.conf.beat_schedule = {
    'transfer-funds-daily': {
        'task': 'api.tasks.transfer_to_financial_goals',
        'schedule': crontab(hour=0, minute=0), 
    },
}


app.conf.timezone = 'Asia/Kolkata' 
USE_TZ = True 



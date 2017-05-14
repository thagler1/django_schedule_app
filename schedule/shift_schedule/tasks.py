# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery import Celery
from datetime import timedelta

celery = Celery(__name__)
celery.config_from_object(__name__)

@celery.task
def say_hello():
    print('Hello, World!')

CELERYBEAT_SCHEDULE = {
    'every-second': {
        'task': 'example.say_hello',
        'schedule': timedelta(seconds=5),
    },
}
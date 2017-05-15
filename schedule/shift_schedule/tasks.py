# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery import Celery
from datetime import timedelta
from .functions import increase_my_pto
from celery.task.schedules import crontab

celery = Celery(__name__)
celery.config_from_object(__name__)

@periodic_task(run_every=(crontab(hour="*", minute="*", day_of_week="*")))
def scraper_example():
    result = increase_my_pto()

from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery import Celery
from celery.schedules import crontab

app = Celery()
@app.task
def add_schedule_record():
    from .functions import build_schedule_record
    build_schedule_record()
    return


@shared_task
def celery_is_awful():
    print("hello")
    return True

@shared_task
def this_might_work():
    print("hello")
    return True

@app.task
def run_schedule_service():
    from .functions import scheduleing_service
    scheduleing_service()
    return 0
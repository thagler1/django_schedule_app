from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery import Celery
from celery.schedules import crontab


@shared_task
def add_schedule_record():
    from .functions import build_schedule_record
    build_schedule_record()
    return


@shared_task
def does_it_change():
    print("hello")
    return True

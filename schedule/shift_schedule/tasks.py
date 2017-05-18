from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery import Celery
from celery.schedules import crontab


@shared_task
def add_schedule_record(dateitem):
    from .models import UserProfile, PTO_table,Console_oq,Console
    from.schedule_calculations import project_schedule
    from.functions import find_oq_controllers
    from django.contrib.auth.models import User  # used fro user profiles


    return up.pto

    return 3

@shared_task
def celery_is_awful():
    print("hello")
    return True

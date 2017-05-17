from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery import Celery
from celery.schedules import crontab


@shared_task
def add():
    print("It made it here")

    from .models import UserProfile
    from django.contrib.auth.models import User  # used fro user profiles
    user = User.objects.get(first_name = 'Todd')
    up = UserProfile.objects.get(id = user.id)
    print(up)
    up.pto += 10
    up.save()
    print(up)
    return up.pto

    return 3

@shared_task
def celery_is_awful():
    print("hello")
    return True

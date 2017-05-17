from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery import Celery
from celery.schedules import crontab

@app.on_after_configure.connect


@shared_task
def add():
    print("It made it here")
    from .models import UserProfile
    from django.contrib.auth.models import User  # used fro user profiles
    user = User.objects.get(first_name = 'Todd')
    up = UserProfile.objects.get(id = user.id)
    up.pto += 10
    up.save()
    return up.pto

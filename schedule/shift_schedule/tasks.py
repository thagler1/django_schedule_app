from __future__ import absolute_import, unicode_literals
from celery import Celery
from shift_schedule import UserProfile
from django.contrib.auth.models import User #used fro user profiles
CELERY_IMPORTS = ('shift_schedule.models', )

app = Celery()
@app.task(ignore_result=True)
def addpto():
    user = User.objects.get(first_name = 'Todd')
    up = UserProfile.objects.get(id = user.id)

    up.pto +=10
    up.save()

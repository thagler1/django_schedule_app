from __future__ import absolute_import, unicode_literals
CELERY_IMPORTS = ('shift_schedule.models', )
import os
from celery import Celery
from schedule.shift_schedule.models import UserProfile
from django.contrib.auth.models import User #used fro user profiles


app = Celery()
@app.task(ignore_result=True)
def addpto():
    user = User.objects.get(first_name = 'Todd')
    up = UserProfile.objects.get(id = user.id)

    up.pto +=10
    up.save()

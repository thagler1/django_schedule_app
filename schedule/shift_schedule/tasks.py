# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery import Celery
from celery.schedules import crontab
from .models import UserProfile
from django.contrib.auth.models import User #used fro user profiles

app = Celery()
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

@app.task
def test(arg):
    user = User.objects.get(first_name = 'Todd')
    userprofile = UserProfile.objects.get(user)
    userprofile.pto += 10
    userprofile.save()
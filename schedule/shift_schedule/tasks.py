from celery import Celery
from celery.schedules import crontab
from .models import UserProfile
from django.contrib.auth.models import User #used fro user profiles
from schedule.shift_schedule.functions import increase_my_pto

app = Celery()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

    # Calls test('world') every 30 seconds
    sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        test.s('Happy Mondays!'),
    )

@app.task
def test(arg):
    print(arg)

@app.task
def add_pto():
    user = User.objects.get(first_name="Todd")
    userprofile = UserProfile.objects.get(id = user.id)

    userprofile.pto += 10
    userprofile.save()
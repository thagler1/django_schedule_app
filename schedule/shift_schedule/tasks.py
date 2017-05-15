# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery import Celery
from datetime import timedelta
from .functions import increase_my_pto
from celery.schedules import crontab

celery = Celery(__name__)
celery.config_from_object(__name__)


@app.on_after_configure.connect
def setup_periodic_tasks(sender,**kawrgs):
    # Calls test('hello') every 10 seconds.
    increase_my_pto.add_periodic_task(10.0, test(), name='add every 10')

@app.task
def test():
    increase_my_pto()

# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery import Celery
from celery.schedules import crontab

app = Celery()
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

@app.task
def test(arg):
    print(arg)
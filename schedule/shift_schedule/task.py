# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery import Celery

app = Celery('tasks', broker='pyamqp://guest@localhost//')


@app.task
def add(x, y):
    return x + y

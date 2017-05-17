from __future__ import absolute_import, unicode_literals
from celery import Celery

app = Celery()
@app.task(ignore_result=True)
def add():
    print("Hi")
    return True
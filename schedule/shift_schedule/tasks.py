# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import Celery
from .functions import increase_my_pto

from celery import shared_task
celery = Celery(__name__)
celery.config_from_object(__name__)

app = Celery()
@shared_task
def add_pto():
    increase_my_pto()
    increase_my_pto()
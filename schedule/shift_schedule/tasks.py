from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery import Celery
from celery.schedules import crontab
from twilio.rest import Client

app = Celery()
@app.task
def add_schedule_record():
    from .functions import build_schedule_record
    build_schedule_record()
    return


@shared_task
def celery_is_awful():
    print("hello")
    return True

@shared_task
def this_might_work():
    print("hello")
    return True

@app.task
def run_schedule_service():
    from .functions import scheduleing_service
    scheduleing_service()
    return 0


@app.task
def send_txt_message(to, body):
    if to.phone is not None:
        sendto = to.phone
        sendfrom = '+19724498463'
        TWILIO_ACCOUNT_SID = 'ACd5b0e9b482445382c76c5d3c004dd8d6'
        TWILIO_AUTH_TOKEN = 'dcde93c2e645e76d3bc4fa9e3dae2c2c'
        client = Client(TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN)

        message = client.messages.create(
            body = body,
            to = sendto,
            from_ = sendfrom
    )

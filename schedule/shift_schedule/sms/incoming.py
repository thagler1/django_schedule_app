from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from ..models import PTO_table, CommsLog, OT_offer,UserProfile

@csrf_exempt
def receive_response(request):
    import datetime
    from ..schedule_calculations import project_schedule
    from ..tasks import send_txt_message
    txtin = (request.POST)

    from_= txtin["From"]
    userprofile =UserProfile.objects.get(phone=from_)
    next = ['Next', 'Nxt', 'next']
    if txtin['Body'] in next:
        today = datetime.date.today() + datetime.timedelta(days=3)
        found = False
        nextshift = project_schedule(today, today, userprofile)
        while type(nextshift) is list:
            today = today + datetime.timedelta(days=1)
            nextshift = project_schedule(today, today, userprofile)
        print(nextshift)
        print(nextshift.shift_start_time)
        send_txt_message(userprofile, nextshift.shift_start_time)





    return HttpResponse('received')



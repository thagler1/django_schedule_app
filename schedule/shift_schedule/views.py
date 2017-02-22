from django.http import HttpResponse
from django.template import loader
from .models import Shift, Controller, Console_oq



def index(request):
    allshifts = Shift.objects.all()
    allcontrollers = Controller.objects.all()

    template = loader.get_template('shift_schedule/index.html')
    context = {
        'allshifts': allshifts,
        'allcontrollers': allcontrollers,

    }
    return HttpResponse(template.render(context, request))



from django.http import HttpResponse
from .models import Shift

def index(request):
    return HttpResponse("You have reached the scheduling app")

def index(request):
    allshifts = Shift.objects.all()

    return HttpResponse(allshifts)
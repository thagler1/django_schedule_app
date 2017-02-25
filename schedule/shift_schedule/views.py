from django.http import HttpResponse
from django.template import loader
from .models import Shift, Controller, Console, Master_schedule, Console_schedule, Console_oq
import datetime



def index(request):
    allshifts = Shift.objects.all()
    allcontrollers = Controller.objects.all()

    template = loader.get_template('shift_schedule/index.html')
    context = {
        'allshifts': allshifts,
        'allcontrollers': allcontrollers,

    }
    return HttpResponse(template.render(context, request))


def console_schedule_menu(request):
    consoles = Console.objects.all()
    template = loader.get_template('shift_schedule/console_schedule_menu.html')
    todaysdate = datetime.datetime.now()
    start_date = datetime.date(todaysdate.year, todaysdate.month, 1)
    end_date = datetime.date(todaysdate.year, (todaysdate.month)+1, 1)
    span = (end_date - start_date)
    timeframe = span.days

    cal_dates = [start_date+datetime.timedelta(days =x) for x in range(timeframe)]
    daterange = Master_schedule.objects.filter(date__range= (start_date, end_date))

    shifts = Shift.objects.all()
    allshifts_console_schedule = []
    desk_shift_name = []

    for desk in consoles:
        #make dictionary of schedules. html will parse the dictionary

        for shift in shifts:

            primary_desk_controllers = Console_oq.objects.filter(primary_console=True, console=desk)
            active_controller = ""
            for controller in primary_desk_controllers:
                x = controller.controller

                if x.shift == shift:
                    desk_shift_name.append((desk, shift, x))
                    active_controller = x
            for date in cal_dates:
                try:
                    if Console_schedule.objects.filter(date = date, shift = shift,controller= active_controller).exists():
                        console_day_schedule = Console_schedule.objects.filter(date = date,
                                                                               shift = shift,
                                                                               controller= active_controller)
                        for day in console_day_schedule:
                            allshifts_console_schedule.append((day.which_shift, shift, desk, active_controller))
                    else:
                        allshifts_console_schedule.append(("", shift, desk, active_controller))
                except:
                    pass




    context = {
        'consoles':consoles,
        'daterange':daterange,
        'cal_dates':cal_dates,
        'shifts':shifts,
        'allshifts_console_schedule': allshifts_console_schedule,
        'desk_shift_name':desk_shift_name

    }
    return HttpResponse(template.render(context,request))
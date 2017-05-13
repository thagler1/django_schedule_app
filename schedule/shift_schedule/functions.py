from django.http import HttpResponse
from django.template import loader
from .models import Shift, UserProfile, Console, Master_schedule, Console_Map, Console_oq, PTO_table
import datetime
from .schedule_calculations import project_schedule
from .forms import UserForm
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import render




def user_oqs(user):
    '''
    :param user:
    :return: list of consoles
    '''
    user_object = User.objects.get(id=user.id)
    userprofile = UserProfile.objects.get(user = user_object)
    all_user_oqs = Console_oq.objects.filter(controller = userprofile)

    return all_user_oqs

def calcdaterange(today): #used for calendar output

    month = today.strftime("%B") #returns just the month value

    first_day_of_month = datetime.date(today.year, today.month,1)
    fdom_weekday = first_day_of_month.weekday()
    start_date = first_day_of_month + datetime.timedelta(days = 0-fdom_weekday) # starts the calendar on a monday
    end_date = start_date + datetime.timedelta(days = 42)

    return start_date, end_date, month

def find_oq_controllers(consoles):
    if isinstance(consoles,list) is False:
        consoles = [consoles]
    controllers = set()
    for console in consoles:
        all_qualified_controllers = Console_oq.objects.filter(console=console, primary_console=True)
        for controller in all_qualified_controllers:
            controllers.add((controller.controller, console))
    return controllers



def user_console_schedules(user, users_oqs, calyear,calmonth):
    '''
    :param user:
    :param user_oqs:
    :return: dictionary of consoles with schedules as their values
    '''
    user_object = User.objects.get(id=user.id)
    userprofile = UserProfile.objects.get(user = user_object)
    primary_console = "None"

    consoles = []
    for console in users_oqs:
        consoles.append(console.console)
        if console.primary_console:
            primary_console = console.console
    all_qualified_controllers = find_oq_controllers(consoles)

    print(calmonth)
    todaysdate = datetime.date.today()
    if calmonth: # DEFENSIVELY CODE THIS
        try:
            strippedmonth = int(calmonth)
            if strippedmonth>12 or strippedmonth < 1:
                pass
            else:
                todaysdate = datetime.date(2017,strippedmonth,1)
        except:
            pass

    start_date, end_date, month = calcdaterange(todaysdate)
    timeframe = (end_date - start_date).days

    cal_dates = [start_date + datetime.timedelta(days=x) for x in range(timeframe)] # generates list of datetime objects
    daterange = Master_schedule.objects.filter(date__range=(start_date, end_date)) # this needs to porint to recurring events and get a return
    recurring_calendar = project_schedule(start_date,end_date, userprofile)
    shifts = Shift.objects.all()
    user_calendar = [[] for y in range(7)] #creates 7 rows for calendar display.
    desk_shift_name = [] # i dont think this is used. Tagged for removal
    allshifts_console_schedule =[] # create the list that serves the desk schedules
    for i, date in enumerate(cal_dates):
        display_date = date.day # used to create calendar date in template
        rownum = i//7 # no remainder division
        found_event = False
        # for day in cal dates. if day is in recurring event calendar add to ascs, else add place holder
        for event in recurring_calendar:

            if event.date == date:
                found_event = True
                schedule_item = event  # the is the Master_schedule object itself
                #print(schedule_item.which_shift())
                '''
                if event.model_object.shift == userprofile.shift:
                    user_calendar[rownum].append(
                        (schedule_item.which_shift(), display_date, primary_console,pto_type ))
                '''
                # (schedule_item.which_shift(), display_date, primary_console, pto_type, original_controller))
                user_calendar[rownum].append(
                    (schedule_item, display_date))



        if found_event is False:
            user_calendar[rownum].append(("", display_date))
    #print(user_calendar)

    #create allshift_console_schedule, run project schedule for each qualified controller
    for controller in all_qualified_controllers:
        found_event = False
        temp_cal = []  # this is a temp calendar to move the dates through
        recurring_calendar = project_schedule(start_date,end_date,controller[0]) # get controller specific event calendar
        for i, date in enumerate(cal_dates): # scroll through requested date range

            display_date= date.day #this is to pull just the date number
            found_event = False
            for event in recurring_calendar:
                if event.date == date:
                    found_event = True
                    temp_cal.append(
                        (controller[0],controller[1],event))
            if found_event is False:
                temp_cal.append((controller[0],controller[1],"", display_date,None,None))
        allshifts_console_schedule.append(temp_cal)



    return (allshifts_console_schedule, user_calendar, desk_shift_name, shifts, consoles, cal_dates, daterange, month)


def OTO_calc(userprofile, year):
    total =0
    if PTO_table.objects.filter(coverage = userprofile,date_pto_taken__gte=datetime.date(year,1,1)).exists():
        total = len(PTO_table.objects.filter(coverage = userprofile, date_pto_taken__gte=datetime.date(year,1,1)))
    return total

def check_supervisor(userprofile):
    if userprofile.is_supervisor:
        return True
    else:
        return False
def importcsv():
    import csv

    with open(r"/home/todd/django_schedule_app/schedule/shift_schedule") as f:
        reader = csv.reader(f)
        for row in reader:
            try:

                print(row)
                if row[0] == 't':
                    day = True
                else:
                    day=False
                created = Console_Map.objects.get_or_create(
                is_day = day,
                shift = Shift.objects.get(shift_id=row[1]),
                date= row[2],
                repeat_start =row[3])
            except:
                print("error")



def handle_uploaded_file(f):
    with open('some/file/name.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


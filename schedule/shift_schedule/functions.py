from django.http import HttpResponse
from django.template import loader
from .models import Shift, UserProfile, Console, Master_schedule, Console_schedule, Console_oq
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

    first_day_of_month = datetime.datetime(today.year, today.month,1)
    fdom_weekday = first_day_of_month.weekday()
    start_date = first_day_of_month + datetime.timedelta(days = 0-fdom_weekday) # starts the calendar on a monday
    end_date = start_date + datetime.timedelta(days = 42)

    return start_date, end_date, month

def user_console_schedules(user, users_oqs):
    '''

    :param user:
    :param user_oqs:
    :return: dictionary of consoles with schedules as their values
    '''
    user_object = User.objects.get(id=user.id)
    userprofile = UserProfile.objects.get(user = user_object)

    consoles = []
    for console in users_oqs:
        consoles.append(console.console)

    todaysdate = datetime.date.today()
    start_date, end_date, month = calcdaterange(todaysdate)
    timeframe = (end_date - start_date).days

    cal_dates = [start_date + datetime.timedelta(days=x) for x in range(timeframe)] # generates list of datetime objects
    daterange = Master_schedule.objects.filter(date__range=(start_date, end_date)) # this needs to porint to recurring events and get a return
    recurring_calendar = project_schedule(start_date,end_date)
    shifts = Shift.objects.all()
    allshifts_console_schedule = [[] for y in range(7)] #creates 7 rows for calendar display. 
    desk_shift_name = [] # i dont think this is used. Tagged for removal

    for i, date in enumerate(cal_dates):
        display_date = date.day # used to create calendar date in template
        rownum = i//7 # no remainder division
        try:
            # for day in cal dates. if day is in recurring event calendar add to ascs, else add place holder
            if date in recurring_calendar:
                indices = [i for i, x in enumerate(recurring_calendar) if x == date]

                for day in indices:
                    allshifts_console_schedule[rownum].append((day[0].which_shift, display_date, day[0].deskname.console_name))
            else:
                allshifts_console_schedule[rownum].append(("", display_date))
        except:
            pass

    return (allshifts_console_schedule, desk_shift_name, shifts, consoles, cal_dates, daterange, month)









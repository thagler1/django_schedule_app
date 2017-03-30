from django.http import HttpResponse
from django.template import loader
from .models import Shift, UserProfile, Console, Master_schedule, Console_schedule, Console_oq
import datetime
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

def calcdaterange(today):
    month = today.strftime("%B")

    first_day_of_month = datetime.datetime(today.year, today.month,1)
    fdom_weekday = first_day_of_month.weekday()
    start_date = first_day_of_month + datetime.timedelta(days = 0-fdom_weekday)
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

    todaysdate = datetime.datetime.now()
    start_date, end_date, month = calcdaterange(todaysdate)
    span = (end_date - start_date)
    timeframe = span.days

    cal_dates = [start_date + datetime.timedelta(days=x) for x in range(timeframe)]
    daterange = Master_schedule.objects.filter(date__range=(start_date, end_date))

    shifts = Shift.objects.all()
    allshifts_console_schedule = [[] for y in range(7)]
    desk_shift_name = []
    rownum = 0
    for i, date in enumerate(cal_dates):
        display_date = date.day
        if i%7 == 0:
            rownum += 1
        try:
            # look at using date__range
            if Console_schedule.objects.filter(date=date, controller=userprofile).exists():
                console_day_schedule = Console_schedule.objects.filter(date=date,
                                                                       controller=userprofile)
                for day in console_day_schedule:
                    allshifts_console_schedule[rownum].append((day.which_shift, display_date, day.deskname.console_name))
            else:
                allshifts_console_schedule[rownum].append(("", display_date))
        except:
            pass

    return (allshifts_console_schedule, desk_shift_name, shifts, consoles, cal_dates, daterange, month)









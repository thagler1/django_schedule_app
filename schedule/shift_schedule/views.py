from django.http import HttpResponse
from django.template import loader
from .models import Shift, UserProfile, Console, Master_schedule, Console_schedule, Console_oq
import datetime
from .forms import UserForm
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import render



def index(request):
    allshifts = Shift.objects.all()
    allcontrollers = UserProfile.objects.all()

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

def lexusadduser(request):

    #template = loader.get_template("shift_schedule/adduser.html")
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(**form.cleaned_data)
            login(new_user)
            # redirect, or however you want to get to the main view
            return HttpResponseRedirect('index.html')
    else:
        form = UserForm()

    return render(request, 'shift_schedule/adduser.html', {'form':form})



def user_login(request):

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
                # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
                # because the request.POST.get('<variable>') returns None, if the value does not exist,
                # while the request.POST['<variable>'] will raise key error exception
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/shift_schedule/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print ("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'shift_schedule/login.html', {})

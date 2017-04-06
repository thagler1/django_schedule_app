from django.http import HttpResponse
from django.template import loader
from .models import Shift, UserProfile, Console, Master_schedule, Console_schedule, Console_oq, PTO_table
import datetime
from .forms import UserForm, PTOForm
from .schedule_calculations import project_schedule
from .functions import user_oqs, user_console_schedules
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import render
from .schedule_validation_rules import one_shift_per_controller, deviation_check
from collections import namedtuple



def index(request):
    allshifts = Shift.objects.all()
    allcontrollers = UserProfile.objects.all()

    template = loader.get_template('shift_schedule/index.html')
    context = {
        'allshifts': allshifts,
        'allcontrollers': allcontrollers,

    }
    return HttpResponse(template.render(context, request))


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
                return HttpResponseRedirect('/shift_schedule/user')
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

def user_page(request):
    user = request.user
    user_object = User.objects.get(id=user.id)
    userprofile = UserProfile.objects.get(user=user_object)
    testdate = datetime.datetime(2017,3,28)
    test = project_schedule(datetime.date(2017,3,1),datetime.date(2017,4,1), userprofile)
    #scroll through oq's and and get a list of consoles the user is oq'd on
    users_oqs = user_oqs(user)
    allshifts_console_schedule, user_calendar, desk_shift_name, shifts, consoles, cal_dates, daterange, month = user_console_schedules(user, users_oqs)


    if userprofile.is_manager is True or userprofile.is_supervisor is True:
        all_unapproved_pto = PTO_table.objects.filter(supervisor_approval=False)
    else:
        all_unapproved_pto = PTO_table.objects.filter(supervisor_approval=False, user=userprofile)

    context = {
        'consoles':consoles,
        'daterange':daterange,
        'cal_dates':cal_dates,
        'shifts':shifts,
        'user_calendar': user_calendar,
        'desk_shift_name':desk_shift_name,
        'oqs':users_oqs,
        'user_profile': userprofile,
        'month': month,
        'test':test,
        'all_unapproved_pto':all_unapproved_pto,
        'allshifts_console_schedule': allshifts_console_schedule


    }

    template = loader.get_template('shift_schedule/user_page.html')


    return HttpResponse(template.render(context, request))


def controller_pto_form(request):
    user = request.user
    user_object = User.objects.get(id=user.id)  # returns userprofile for logged in user
    userprofile = UserProfile.objects.get(user=user_object)

    if request.method =='POST':
        form = PTOForm(request.POST)
        if form.is_valid():
            form.save(commit=True)  # saves form and commits to DB
            return HttpResponseRedirect('/shift_schedule/user')
    else:
        form = PTOForm()
    return render(request, 'shift_schedule/controller_pto_form.html', {'form': form})

def unnaproved_pto(request):
    user = request.user
    user_object = User.objects.get(id=user.id)  # returns userprofile for logged in user
    userprofile = UserProfile.objects.get(user=user_object)

    template = loader.get_template('shift_schedule/unnaproved_pto.html')
    all_unapproved_pto = PTO_table.objects.filter(supervisor_approval=True)
    context = {
        'all_unapproved_pto': all_unapproved_pto
    }
    return HttpResponse(template.render(context, request))



from django.http import HttpResponse
from django.template import loader
from .models import Shift, UserProfile, Console, Master_schedule, Console_schedule, Console_oq, PTO_table, Console_Map
import datetime
from .forms import UserForm, PTOForm, UserprofileForm, ConsoleForm, schedule_pto
from .schedule_calculations import project_schedule
from .functions import user_oqs, user_console_schedules, OTO_calc, check_supervisor, importcsv, console_schedule, controller_pto_request
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import render
from .schedule_validation_rules import one_shift_per_controller, deviation_check
from collections import namedtuple
from .schedule_calculations import OqController, assign_coverage
from .tasks import celery_is_awful
from django.contrib.auth.decorators import login_required


def index(request):
    allshifts = Shift.objects.all()
    allcontrollers = UserProfile.objects.all()

    template = loader.get_template('shift_schedule/index.html')
    context = {
        'allshifts': allshifts,
        'allcontrollers': allcontrollers,

    }
    return HttpResponse(template.render(context, request))

@login_required
def create_user(request):
    #template = loader.get_template("shift_schedule/adduser.html")
    if request.method == "POST":
        form = UserForm(request.POST)
        uform = UserprofileForm(request.POST,  request.FILES)

        new_up = uform.save(commit=False)


        if form.is_valid():
            new_user = User.objects.create_user(**form.cleaned_data)
            userobject = User.objects.get(username = request.POST['username'])
            userprofile = UserProfile.objects.get(user = userobject)
            try:
                userprofile.pto = request.POST['pto']
            except:
                pass

            try:
                userprofile.profile_image = request.FILES['profile_image']
            except:
                pass
            try:
                userprofile.manager = UserProfile.objects.get(id = request.POST['manager'])
            except:
                pass
            try:
                userprofile.shift = Shift.objects.get(id = request.POST['shift'])
            except:
                pass
            try:
                userprofile.phone = request.POST['phone']
            except:
                pass
            userprofile.save()
            # redirect, or however you want to get to the main view
            return HttpResponseRedirect('login.html')
    else:
        form = UserForm()
        uform = UserprofileForm()

    return render(request, 'shift_schedule/adduser.html',{'form':form, 'uform':uform})



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
                userprofile = UserProfile.objects.get(user=user)
                if check_supervisor(userprofile):
                    login(request, user)
                    return HttpResponseRedirect("/shift_supervisor_console.html")

                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/user')
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

@login_required
def user_page(request, calyear = None,calmonth=None):

    from .functions import pto_calandar

    user = request.user
    user_object = User.objects.get(id=user.id)
    userprofile = UserProfile.objects.get(user=user_object)
    #testdate = datetime.datetime(2017,3,28)
    oto = OTO_calc(userprofile,2017)
    #scroll through oq's and and get a list of consoles the user is oq'd on
    users_oqs = user_oqs(user)
    user_calendar, desk_shift_name, shifts, consoles, cal_dates, daterange, request_range = user_console_schedules(user, users_oqs, calyear,calmonth)
    #importcsv()
    pending_pto, approved_pto = controller_pto_request(request)
    pto_events = pto_calandar(userprofile, 2017)
    context = {
        'consoles':consoles,
        'daterange':daterange,
        'cal_dates':cal_dates,
        'shifts':shifts,
        'oto':oto,
        'user_calendar': user_calendar,
        'desk_shift_name':desk_shift_name,
        'oqs':users_oqs,
        'user_profile': userprofile,
        'request_range': request_range,
        'pto_days': pto_events,

        'pending_pto':pending_pto,
        'approved_pto': approved_pto,
    }

    template = loader.get_template('shift_schedule/user_page.html')

    return HttpResponse(template.render(context, request))


def controller_pto_form(request):
    user = request.user
    user_object = User.objects.get(id=user.id)  # returns userprofile for logged in user
    userprofile = UserProfile.objects.get(user=user_object)

    if request.method =='POST':
        form = PTOForm(request.POST,userprofile = userprofile)


        if form.is_valid():
            print(request.POST['end_date'])
            #form.clean_recipeants(userprofile)
            post =form.save(commit=False)  # saves form and commits to DB
            post.date_requested=datetime.datetime.now()
            post.user = userprofile
            #post.coverage = userprofile

            if post.type == 'DND':
                post.supervisor_approval = True

            post.save()

            return HttpResponseRedirect('/user')
    else:
        form = PTOForm()
    return render(request, 'shift_schedule/controller_pto_form.html', {'form': form})

def unnaproved_pto(request):
    user = request.user
    user_object = User.objects.get(id=user.id)  # returns userprofile for logged in user
    userprofile = UserProfile.objects.get(user=user_object)

    template = loader.get_template('shift_schedule/unnaproved_pto.html')
    all_unapproved_pto = PTO_table.objects.filter(supervisor_approval=False)
    pto_by_desk = {pto.console:PTO_table.objects.filter(supervisor_approval=False, console=pto.console).count() for pto in all_unapproved_pto}
    context = {
        'all_unapproved_pto': all_unapproved_pto,
        'pto_by_desk':pto_by_desk
    }
    return HttpResponse(template.render(context, request))

def supervisors_console(request):
    if not request.user.is_authenticated:
        HttpResponseRedirect('/login')
    from .tasks import run_schedule_service
    run_schedule_service.delay()
    user = request.user
    user_object = User.objects.get(id = user.id)
    userprofile = UserProfile.objects.get(user= user_object)
    all_unapproved_pto = PTO_table.objects.filter(supervisor_approval=False)
    pto_by_desk = {pto.console: PTO_table.objects.filter(supervisor_approval=False, console=pto.console).count() for pto
                   in all_unapproved_pto}

    template = loader.get_template('shift_schedule/shift_supervisor_console.html')
    console_rows = Console_Map.objects.values('row').distinct()
    rows = []
    for row in console_rows:
        rows.append(row['row'])
    rows = sorted(rows)
    map = []
    for row in rows:
        print(row)
        rowlist = []
        columns = Console_Map.objects.filter(row=row).values('column').distinct()
        columnlist = []
        for column in columns:
            columnlist.append(column['column'])
        columnlist = sorted(columnlist)
        for column in columnlist:
            console = Console_Map.objects.get(row=row, column = column)
            rowlist.append(console)
        map.append(rowlist)

    #PTO map
    pto_days = PTO_table.objects.all()

    ptodata = {}
    #dlist = [[] for i in range(pto_days.count())]
    for day in pto_days:
        year = day.date_pto_taken.year
        month = day.date_pto_taken.month - 1
        thatday = day.date_pto_taken.day
        print(type(year))

        ptodata.setdefault(day.date_pto_taken, {'year':year, 'month':month, 'thatday':thatday, 'count':0})
        ptodata[day.date_pto_taken]['count'] +=1

    ############################
    #pto repot
    record = namedtuple('Record','controller pto'.split())
    pto_events = PTO_table.objects.all()
    pto_records = {}

    for item in pto_events:
        pto_item = project_schedule(item.date_pto_taken,item.date_pto_taken, item.user)
        pto_records.setdefault(pto_item.console, []).append(pto_item)
    print(pto_records)

    #/todo create onshift console layout that links to sister console tables

    context = {
        'map':map,
        'pto_records':pto_records,
        'user_profile':userprofile,
        'pto_by_desk': pto_by_desk,
        'all_unapproved_pto': all_unapproved_pto,
        'pto_days':ptodata


    }
    return HttpResponse(template.render(context, request))


def debugpage(request):
    #TWILIO_ACCOUNT_SID = 'ACd5b0e9b482445382c76c5d3c004dd8d6'
    #TWILIO_AUTH_TOKEN = 'dcde93c2e645e76d3bc4fa9e3dae2c2c'
    #client = Client(TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN)
    #importcsv()
    user = request.user
    user_object = User.objects.get(id=user.id)
    #from .functions import pto_calandar
    '''
    message = client.messages.create(
        body = 'it worked!',
        to = '+12147270215',
        from_ = '+19724498463'
    )
    '''
    to = '+12147270215'

    userprofile = UserProfile.objects.get(user=user_object)
    r = pto_calandar(userprofile, 2017)
    template = loader.get_template('shift_schedule/debug.html')

    pto_days = PTO_table.objects.all()



    context = {
        'pto_days': r,
        'user_profile':userprofile,

    }
    return HttpResponse(template.render(context, request))

def add_console(request):
    all_consoles = Console.objects.all()
    if request.method =='POST':
        form = ConsoleForm(request.POST)
        form.address = "n/a"
        if form.is_valid():
            new_console = Console(**form.cleaned_data)
            new_console.save()

            return HttpResponseRedirect('/add_console')
    else:
        form = ConsoleForm()
    return render(request, 'shift_schedule/new_console.html', {'form': form, 'consoles':all_consoles})

def schedule_coverage(request, pto_id):
    if not request.user.is_authenticated:
        HttpResponseRedirect('/login')
    pto_data = PTO_table.objects.get(id = pto_id)

    if request.method=="POST":
        from .tasks import send_txt_message
        form = schedule_pto(request.POST,instance = pto_data)
        print(form)
        if form.is_valid():

            pto_event = form.save()
            if pto_event.supervisor_approval:
                txt = "You have been scheduled to work %s %s"%(pto_event.date_pto_taken, pto_event.shift_type)
                send_txt_message(pto_event.coverage,txt).delay()

            return HttpResponseRedirect('/unapproved_pto')
    else:
        form  = schedule_pto(instance=pto_data)
    return render(request,'shift_schedule/schedule_coverage.html', {'form':form, 'pto_id':pto_id})

def console_approval(request, console):
    if not request.user.is_authenticated:
        HttpResponseRedirect('/login')
    user = request.user
    user_object = User.objects.get(id = user.id)
    userprofile = UserProfile.objects.get(user= user_object)
    console= Console.objects.get(console_name = console)
    month = datetime.date.today().month
    calendar, allshifts_console_schedule, shifts, desks = console_schedule(console, month)
    upto = {desk.console_name:{'requests':PTO_table.objects.filter(console = desk, supervisor_approval = False)} for desk in desks}

    context = {
        'calendar': calendar,
        'allshifts_console_schedule':allshifts_console_schedule,
        'shifts':shifts,
        'desks': desks,
        'upto': upto,
        'user_profile':userprofile,
    }
    template = loader.get_template('shift_schedule/console_approval_page.html')
    return HttpResponse(template.render(context, request))


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/login')


def reply_to_sms_message(request):
    from twilio import twiml
    r = twiml.Response()
    r.message('thanks for the text')
    return r

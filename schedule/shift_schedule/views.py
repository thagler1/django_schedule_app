from django.http import HttpResponse, JsonResponse
from django.template import loader
from .models import Shift, UserProfile, Console, PTO_table, Console_Map, Cancelled_PTO
import datetime
from .forms import UserForm, PTOForm, UserprofileForm, ConsoleForm, schedule_pto, user_pto_form
from .schedule_calculations import project_schedule
from .functions import user_oqs, user_console_schedules, OTO_calc, check_supervisor, console_schedule, \
    controller_pto_request
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import render
from collections import namedtuple
from django.contrib.auth.decorators import login_required


@login_required
def create_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        user_fields = ('username first_name last_name email').split()
        userprofile_fields = ('manager shift hire_date phone').split()

        if form.is_valid():
            print(form.cleaned_data)
            new_user = {field:value for field,value in form.cleaned_data.items() if field in user_fields}
            new_profile = {field:value for field,value in form.cleaned_data.items() if field in userprofile_fields}

            #set default password of firstnamelastname
            password=("%s%s"%(new_user['first_name'],new_user['last_name']))
            userobj = User(**new_user)
            userobj.set_password(password)
            userobj.save()

            #add userobj to userprofile
            new_profile['user'] = userobj
            profileobj = UserProfile(**new_profile)
            profileobj.save()
            return HttpResponseRedirect("/shift_supervisor_console.html")
        else:
            print(form.errors)

    else:
        form = UserForm()
    return render(request, 'shift_schedule/adduser.html', {'form': form,})

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
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'shift_schedule/login.html', {})


@login_required
def user_page(request, calyear=None, calmonth=None):
    args = {}
    from .functions import pto_calandar
    user = request.user
    user_object = User.objects.get(id=user.id)
    userprofile = UserProfile.objects.get(user=user_object)

    oto = OTO_calc(userprofile, 2017)
    # scroll through oq's and and get a list of consoles the user is oq'd on
    users_oqs = user_oqs(user)
    user_calendar, desk_shift_name, shifts, consoles, cal_dates, daterange, request_range = user_console_schedules(user,
                                                                                                                   users_oqs,
                                                                                                                   calyear,
                                                                                                                   calmonth)
    # importcsv()
    pending_pto, approved_pto = controller_pto_request(request)
    pto_events = pto_calandar(userprofile, 2017)

    if request.method == 'POST':
        form = PTOForm(request.POST, userprofile=userprofile)

        if form.is_valid():

            # form.clean_recipeants(userprofile)
            post = form.save(commit=False)  # saves form and commits to DB
            post.date_requested = datetime.datetime.now()
            post.user = userprofile
            # post.coverage = userprofile

            if post.type == 'DND':
                post.supervisor_approval = True

            post.save()

            return HttpResponseRedirect('/user')
    else:
        form = PTOForm()
        args['form'] = form
    ptoreport = user_pto_form()
    context = {
        'consoles': consoles,
        'daterange': daterange,
        'cal_dates': cal_dates,
        'shifts': shifts,
        'oto': oto,
        'user_calendar': user_calendar,
        'desk_shift_name': desk_shift_name,
        'oqs': users_oqs,
        'user_profile': userprofile,
        'request_range': request_range,
        'pto_days': pto_events,
        'pending_pto': pending_pto,
        'approved_pto': approved_pto,
        'form': form,
        'ptoreport':ptoreport

    }

    template = loader.get_template('shift_schedule/user_page.html')

    return HttpResponse(template.render(context, request))


@login_required
def controller_pto_form(request):
    import json
    user = request.user
    user_object = User.objects.get(id=user.id)  # returns userprofile for logged in user
    userprofile = UserProfile.objects.get(user=user_object)

    if request.method == 'POST':
        form = PTOForm(data=request.POST, userprofile=userprofile)

        print('post request made')
        if form.is_valid():
            print('form is valid')
            response_data = {}
            # form.clean_recipeants(userprofile)
            post = form.save(commit=False)  # saves form and commits to DB
            post.date_requested = datetime.datetime.now()
            post.user = userprofile
            # post.coverage = userprofile

            response_data['pto_added'] = 1
            response_data['success_message'] = "Request added successfully"

            if post.type == 'DND':
                post.supervisor_approval = True

            post.save()
            return JsonResponse(response_data)

        else:
            return JsonResponse(form.errors)


def unnaproved_pto(request):
    user = request.user
    user_object = User.objects.get(id=user.id)  # returns userprofile for logged in user
    userprofile = UserProfile.objects.get(user=user_object)

    template = loader.get_template('shift_schedule/unnaproved_pto.html')
    all_unapproved_pto = PTO_table.objects.filter(supervisors_approval=False)
    pto_by_desk = {pto.console: PTO_table.objects.filter(supervisor_approval=False, console=pto.console).count() for pto
                   in all_unapproved_pto}
    context = {
        'all_unapproved_pto': all_unapproved_pto,
        'pto_by_desk': pto_by_desk
    }
    return HttpResponse(template.render(context, request))


@login_required
def supervisors_console(request):
    if not request.user.is_authenticated:
        HttpResponseRedirect('/login')
    from .tasks import run_schedule_service
    run_schedule_service.delay()
    user = request.user
    user_object = User.objects.get(id=user.id)
    userprofile = UserProfile.objects.get(user=user_object)
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

        rowlist = []
        columns = Console_Map.objects.filter(row=row).values('column').distinct()
        columnlist = []
        for column in columns:
            columnlist.append(column['column'])
        columnlist = sorted(columnlist)
        for column in columnlist:
            console = Console_Map.objects.get(row=row, column=column)
            rowlist.append(console)
        map.append(rowlist)

    # PTO maps
    pto_days = PTO_table.objects.all()

    console_list = Console.objects.all()
    ptodata = {}
    # dlist = [[] for i in range(pto_days.count())]
    for day in pto_days:
        year = day.date_pto_taken.year
        month = day.date_pto_taken.month - 1
        thatday = day.date_pto_taken.day

        ptodata.setdefault(day.date_pto_taken, {'year': year, 'month': month, 'thatday': thatday, 'count': 0})
        ptodata[day.date_pto_taken]['count'] += 1

    ############################
    # pto repot
    record = namedtuple('Record', 'controller pto'.split())
    pto_events = PTO_table.objects.all()
    pto_records = {}

    for item in pto_events:
        pto_item = project_schedule(item.date_pto_taken, item.date_pto_taken, item.user)
        pto_records.setdefault(pto_item.console, []).append(pto_item)

    # /todo create onshift console layout that links to sister console tables

    context = {
        'map': map,
        'pto_records': pto_records,
        'user_profile': userprofile,
        'pto_by_desk': pto_by_desk,
        'all_unapproved_pto': all_unapproved_pto,
        'pto_days': ptodata,
        'console_list': console_list

    }
    return HttpResponse(template.render(context, request))


@login_required
def add_console(request):
    all_consoles = Console.objects.all()
    if request.method == 'POST':
        form = ConsoleForm(request.POST)
        form.address = "n/a"
        if form.is_valid():
            new_console = Console(**form.cleaned_data)
            new_console.save()

            return HttpResponseRedirect('/add_console')
    else:
        form = ConsoleForm()
    return render(request, 'shift_schedule/new_console.html', {'form': form, 'consoles': all_consoles})


@login_required
def schedule_coverage(request, pto_id):
    if not request.user.is_authenticated:
        HttpResponseRedirect('/login')

    user = request.user
    user_object = User.objects.get(id=user.id)
    userprofile = UserProfile.objects.get(user=user_object)

    if userprofile.is_supervisor is False:
        HttpResponseRedirect('/login')

    pto_data = PTO_table.objects.get(id=pto_id)
    month = pto_data.date_pto_taken.month
    console = pto_data.console
    calendar, allshifts_console_schedule, shifts, desks = console_schedule(console, month)
    if request.method == "POST":
        from .tasks import send_txt_message
        form = schedule_pto(request.POST, instance=pto_data)
        print(form)
        if form.is_valid():

            pto_event = form.save()
            if pto_event.supervisor_approval:
                txt = "You have been scheduled to work %s %s" % (pto_event.date_pto_taken, pto_event.shift_type)
                send_txt_message(pto_event.coverage, txt)

            return HttpResponseRedirect('/shift_supervisor_console')
    else:
        form = schedule_pto(instance=pto_data)
        context = {
            'form': form,
            'pto_id': pto_id,
            'calendar': calendar,
            'allshifts_console_schedule': allshifts_console_schedule,
            'shifts': shifts,
            'consoles': desks,
            'pto_data': pto_data,
            'user_profile': userprofile,

        }
    return render(request, 'shift_schedule/schedule_coverage.html', context)


@login_required
def console_approval(request, console):
    if not request.user.is_authenticated:
        HttpResponseRedirect('/login')
    user = request.user
    user_object = User.objects.get(id=user.id)
    userprofile = UserProfile.objects.get(user=user_object)
    console = Console.objects.get(console_name=console)
    month = datetime.date.today().month
    calendar, allshifts_console_schedule, shifts, desks = console_schedule(console, month)
    upto = {desk.console_name: {'requests': PTO_table.objects.filter(console=desk, supervisor_approval=False)} for desk
            in desks}

    context = {
        'calendar': calendar,
        'allshifts_console_schedule': allshifts_console_schedule,
        'shifts': shifts,
        'desks': desks,
        'upto': upto,
        'user_profile': userprofile,
    }
    template = loader.get_template('shift_schedule/console_approval_page.html')
    return HttpResponse(template.render(context, request))


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/login')


def approved_pto(request):
    user = request.user
    user_object = User.objects.get(id=user.id)
    userprofile = UserProfile.objects.get(user=user_object)
    pto_events = PTO_table.objects.filter(supervisor_approval=True)
    pto_events.extra(order_by=['-date_pto_taken'])

    template = loader.get_template('shift_schedule/approved_pto.html')
    context = {
        'approved_pto_events': pto_events,
        'user_profile': userprofile
    }

    return HttpResponse(template.render(context, request))


def console_schedule_menu(request):
    '''
    add manage sooooon
    :param request: 
    :param month: 
    :param console: 
    :return: 
    '''

    console_list = Console.objects.all()

    # calendar, allshifts_console_schedule, shifts, desks = console_schedule(console, month)
    template = loader.get_template('shift_schedule/console_schedule_menu.html')

    context = {
        'console_list': console_list,

    }
    return HttpResponse(template.render(context, request))


def ajax_schedule(request):
    from .functions import serialize_instance
    if request.method == 'POST':
        data = request.POST
        console = Console.objects.get(console_name=data['console'])
        month = int(data['month'])
        calendar, allshifts_console_schedule, shifts, desks = console_schedule(console, month)
        rshift = [[shift.shift_id, ""] for shift in shifts]
        ascs = {}

        #######
        cal_rows = {}

        for desknum, desk in enumerate(desks):
            cal_rows[desknum] = []
            for shift in shifts:
                for controller in allshifts_console_schedule:
                    cname = controller[0][0].full_name()
                    new_controller_row = []
                    if controller[0][0].shift == shift and controller[0][1].console_name == desk.console_name:
                        new_controller_row.append(controller[0][0].full_name())

                        for dcount, day in enumerate(calendar):
                            # print(controller[dcount][2])
                            if type(controller[dcount][2]) is str:
                                new_controller_row.append("")
                            else:
                                dateitem = serialize_instance(controller[dcount][2])
                                print(dateitem)
                                val = ''
                                try:
                                    stype = dateitem['date_object'].is_day

                                except:
                                    stype = controller[dcount][2].date_object.type

                                overtime = controller[dcount][2].is_overtime()

                                if stype is True and overtime is True:
                                    val = 'DO'
                                elif stype is True and overtime is False:
                                    val = 'D'
                                elif stype is False and overtime is True:
                                    val = "NO"
                                elif stype is False and overtime is False:
                                    val = "N"
                                elif dateitem['dnd']:
                                    val = 'DND'
                                try:
                                    if cname != controller[dcount][2].controller.full_name():
                                        val = controller[dcount][2].pto.type


                                except:
                                    pass

                                new_controller_row.append(val)
                        cal_rows[desknum].append(new_controller_row)

        # format dates
        rcalendar = [day.strftime("%-m/%d\n %a") for day in calendar]
        rdesks = [desk.console_name for desk in desks]
        context = {
            'calendar': rcalendar,
            'shifts': rshift,
            'cal_rows': cal_rows,
            'desks': rdesks,

        }

        return JsonResponse(context)
def ajax_user_pto_table(request):
    from.functions import serialize_instance
    from .reportLib.userReports import user_pto_requests
    from .forms import user_pto_form
    user = request.user
    user_object = User.objects.get(id=user.id)
    userprofile = UserProfile.objects.get(user=user_object)
    if request.method == 'POST':
        form=user_pto_form(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            pto_dict = user_pto_requests(userprofile,start=data['startdate'], end=data['enddate'])
            return JsonResponse(pto_dict)
        else:
            print(form.errors)
def cancel_pto_by_controller(request, pto_id):
    from .forms import Cancel_PTO_controller
    user = request.user
    user_object = User.objects.get(id=user.id)
    userprofile = UserProfile.objects.get(user=user_object)

    if request.method == 'POST':
        cancel_form = Cancel_PTO_controller(request.POST, instance= userprofile)
        if cancel_form.is_valid():

            data = cancel_form.cleaned_data

            data['user'] = userprofile
            data['cancelled_by'] = userprofile
            data['date_request_made'] = datetime.datetime.today()
            data['date_of_pto'] = data['pto_event'].date_pto_taken
            #edit PTO Record
            pto_event = data['pto_event']
            pto_event.active = False
            cancel_record = Cancelled_PTO(**data)
            cancel_record.save()
            pto_event.cancelled = cancel_record
            pto_event.save()
        return HttpResponseRedirect('/shift_supervisor_console')
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        form = Cancel_PTO_controller(instance = userprofile)
        return render(request, 'shift_schedule/controller_cancel_pto.html', {'form':form})

def ajax_pto_cancel(request):
    from.functions import serialize_instance
    from .reportLib.userReports import user_pto_requests
    from .forms import Cancelled_PTO
    user = request.user
    user_object = User.objects.get(id=user.id)
    userprofile = UserProfile.objects.get(user=user_object)


    if request.method == 'POST':
        print(request.POST)
        pto_event = PTO_table.objects.get(id= request.POST['pto_id'])
        print("ajax received")
        data = {}
        data['pto_event'] = pto_event
        data['user'] = userprofile
        data['cancelled_by'] = userprofile
        data['date_request_made'] = datetime.datetime.today()
        data['date_of_pto'] = data['pto_event'].date_pto_taken
        #edit PTO Record
        pto_event = data['pto_event']
        pto_event.active = False
        cancel_record = Cancelled_PTO(**data)
        cancel_record.save()
        pto_event.cancelled = cancel_record
        pto_event.save()
        rdict = {'success':'success'}
        print("did it!")

        return JsonResponse(rdict)


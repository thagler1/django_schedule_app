from django.http import HttpResponse
from django.template import loader
from .models import Shift, UserProfile, Console, Master_schedule, Console_Map, Console_oq, PTO_table, Schedule_Record
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
    nmonth =str(today.month).zfill(2)

    request_range = {'month':today.strftime("%B"),'year':today.year,'num_month':nmonth} #returns just the month value
#
    first_day_of_month = datetime.date(today.year, today.month,1)
    fdom_weekday = first_day_of_month.weekday()
    start_date = first_day_of_month + datetime.timedelta(days = 0-fdom_weekday) # starts the calendar on a monday
    end_date = start_date + datetime.timedelta(days = 42)

    return start_date, end_date, request_range

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

    start_date, end_date, request_range = calcdaterange(todaysdate)
    timeframe = (end_date - start_date).days

    cal_dates = [start_date + datetime.timedelta(days=x) for x in range(timeframe)] # generates list of datetime objects
    daterange = Master_schedule.objects.filter(date__range=(start_date, end_date)) # this needs to porint to recurring events and get a return
    recurring_calendar = project_schedule(start_date,end_date, userprofile)
    shifts = Shift.objects.all()
    user_calendar = [[] for y in range(7)] #creates 7 rows for calendar display.
    desk_shift_name = [] # i dont think this is used. Tagged for removal

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





    return ( user_calendar, desk_shift_name, shifts, consoles, cal_dates, daterange, request_range)


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

def get_model_fields(model):
    return model._meta.get_fields()

def importcsv(model):
    import csv, os
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    rel_path = "Book1.csv"
    abs_file_path = os.path.join(script_dir, rel_path)
    model_fields = get_model_fields(model)

    with open(abs_file_path) as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            # strip field names
            if i == 0:
                fields = {key:index for index, key in enumerate(row)}
            new_model = model()
            for field in model_fields:
                if field in fields:
                    new_model.field = fields[field]
            new_model.save()


def handle_uploaded_file(f):
    with open('some/file/name.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
    return next_month - datetime.timedelta(days=next_month.day)

def build_schedule_record():
    '''
    create a schedule record for each worked shift
    :return: 
    '''
    START = datetime.date.today()
    RANGE = 30
    #END = START + datetime.timedelta(days = RANGE)

    for day in range(RANGE):
        date = START + datetime.timedelta(days = day)
        for desk in Console.objects.all():
            all_oq_controller = find_oq_controllers(desk)
            for controller in all_oq_controller:
                di = project_schedule(date,date,controller[0])
                if di:
                    new_record = Schedule_Record(
                        date = di.date,
                        shift = di.shift,
                        controller = di.controller,
                        shift_start_time= di.shift_start_time,
                        shift_end_time=di.shift_end_time,
                        original_controller=di.original_controller,
                        is_day=di.date_object.is_day,
                        console=di.console,
                    )
                    if di.pto:
                        new_record.pto_event = di.pto
                    new_record.save()



def console_schedule(console, month, year = datetime.date.today().year):
    start_date = datetime.date(year, month, 1)
    end_date = last_day_of_month(start_date)
    drange = end_date-start_date

    calender = [start_date+ datetime.timedelta(days = i) for i in range(drange.days +1)]

    #create list of qualified controllers, and list of all consoles these controllers are qualified on
    oq_controllers = UserProfile.objects.filter(console_oq__console = console)

    #all desk for qualified controller
    desks = set()
    for controller in oq_controllers:
        controller_oqs = Console_oq.objects.filter(controller=controller).distinct()
        for oq in controller_oqs:
            desks.add(oq.console)


    all_qualified_controllers = find_oq_controllers(list(desks))
    allshifts_console_schedule = []

    for controller in all_qualified_controllers:
        found_event = False
        temp_cal = []  # this is a temp calendar to move the dates through
        recurring_calendar = project_schedule(start_date,end_date+datetime.timedelta(days=1),controller[0]) # get controller specific event calendar
        for i, date in enumerate(calender): # scroll through requested date range

            display_date= date.day #this is to pull just the date number
            found_event = False
            for event in recurring_calendar:
                if event.date == date:
                    found_event = True
                    temp_cal.append(
                        (controller[0],controller[1],event))
            if found_event is False:
                temp_cal.append((controller[0],controller[1],""))
        allshifts_console_schedule.append(temp_cal)
    shifts = Shift.objects.all()
    return calender, allshifts_console_schedule, shifts, desks


def controller_pto_request(request):
    user = request.user
    user_object = User.objects.get(id=user.id)  # returns userprofile for logged in user
    userprofile = UserProfile.objects.get(user=user_object)

    template = loader.get_template('shift_schedule/controller_pto_requests.html')
    pending_pto = PTO_table.objects.filter(user = userprofile, date_pto_taken__gte = datetime.date.today(),
                                           supervisor_approval = False).order_by('date_pto_taken')
    approved_pto = PTO_table.objects.filter(user=userprofile, date_pto_taken__gte=datetime.date.today(),
                                           supervisor_approval=True).order_by('date_pto_taken')
    return pending_pto, approved_pto

def scheduleing_service():
    from .schedule_calculations import assign_coverage
    pto_events = PTO_table.objects.all()
    test_coverage = []
    for event in pto_events:
        if event.supervisors_approval is False:
            if event.type != 'DND':
                test_coverage.append(assign_coverage(event))

    return test_coverage

def pto_calandar(userprofile, year):
    START = datetime.date(year,1,1)



    pto_events = PTO_table.objects.filter(date_pto_taken__year =year, user = userprofile)
    overtime_events = PTO_table.objects.filter(date_pto_taken__year =year, coverage = userprofile)
    pto_calendar_data = {}
    for event in pto_events:
        pto_calendar_data.setdefault(event.date_pto_taken, 1)
    for ot in overtime_events:
        pto_calendar_data.setdefault(ot.date_pto_taken, -1)
    return pto_calendar_data

'''
    for day in range(365):
        date = START + datetime.timedelta(day)
        if date in pto_calendar_data:
            pass
        else:
            pto_calendar_data[date] = 0
'''


def get_user_profile(request):

    user = request.user
    user_object = User.objects.get(id = user.id)
    userprofile = UserProfile.objects.get(user= user_object)

    return userprofile









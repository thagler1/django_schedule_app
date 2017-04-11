from .models import Shift, UserProfile, Console, Master_schedule, Console_schedule, Console_oq, PTO_table
import datetime
from collections import namedtuple
import operator


def check_date(master_schedule_object,testdate):
    '''

    :param master_schedule_object:
    :param testdate: Test date to see if recurring event occurs on this date
    :return: Binary
    '''
    day_delta = testdate - master_schedule_object.date
    if day_delta.days % master_schedule_object.repeat_interval !=0:
        return False
    else: return True


class DateItem:
    #/todo possible logic problem with self.date
    #/todo develope methof for assigning console
    def __init__ (self, date_object, controller,date=None, console = None, pto = None, dnd = False):
        # date object is master shift schedule object
        self.date_object = date_object
        self.date = date # optional allows access to date worked
        self.controller = controller
        self.shift = controller.shift
        self.original_controller = controller
        self.console = self.set_console()
        self.is_on_pto = False
        self.pto = self.check_pto()
        self.dnd = dnd
        self.set_shift_times()



    def check_pto(self):
        '''
        whether the controller is on PTO or not
        :param: date
        :return: binarry
        '''

        if PTO_table.objects.filter(date_pto_taken=self.date, user= self.original_controller).exists():
            pto_return = PTO_table.objects.filter(date_pto_taken=self.date, user= self.original_controller)
            for pto_event in pto_return:
                #print(pto_event)
                if pto_event.type != "DND":
                    if pto_event.supervisor_approval is True and pto_event.manager_approval is True:
                        self.is_on_pto = True
                        self.controller = pto_event.coverage
                        self.pto = pto_event
                    else:
                        self.pto = None
                else:
                    self.pto = None

        else:
            self.pto = None
        return self.pto


    def check_on_pto(self):
        if self.pto is not None:
            self.is_on_pto = True
        else: self.is_on_pto = False
        return self.is_on_pto


    def model_object(self):
        #print(self.date_object)
        return self.date_object

    def is_repeating(self):
        return self.date_object.is_repeating

    def is_overtime(self):
        if self.original_controller == self.controller:
            return False
        else:
            return True
    def change_controller(self, controller):
        self.controller = controller

    def set_console(self):

        oqs = all_user_oqs = Console_oq.objects.filter(controller = self.original_controller)
        for oq in oqs:
            if oq.primary_console:
                self.console = oq.console
        return self.console

    def set_shift_times(self):
        if self.dnd is False:
            if self.date_object.is_day:
                start_time = datetime.datetime.combine(self.date, datetime.time())
                self.shift_start_time= start_time.replace(hour=6)
                self.shift_end_time = start_time.replace(hour=18)
            else:
                placeholder_time =datetime.datetime.combine(self.date, datetime.time())
                self.shift_start_time= placeholder_time.replace(hour=18)
                self.shift_end_time=self.shift_start_time+datetime.timedelta(hours=12)
            return self.shift_start_time, self.shift_end_time
        else:
            start_time = datetime.datetime.combine(self.date, datetime.time())
            self.shift_start_time = start_time.replace(hour=6)
            self.shift_end_time = start_time.replace(hour=18)

    def set_controller(self, controller):
        self.controller = controller
        return self.controller

    def __eq__(self, other):
        return self.date == other.date

    def __hash__(self):
        return hash(self.date)


class OqController:

    def __init__(self, UserProfile):
        self.controller = UserProfile
        self.score = 0
        self.shift_list = set()
        self.schedule = set()


    def check_oqs(self):
        '''
        :return: queryset
        '''
        self.oq_list = Console_oq.objects.filter(controller = self.controller)
        return self.oq_list

    def build_schedule(self, startdate, enddate=None):
        startdate = startdate + datetime.timedelta(days=10)
        if enddate is None:
            enddate = startdate + datetime.timedelta(days=20)
        self.schedule = project_schedule(startdate, enddate, self.controller)

        return self.schedule

    def contiguous_shifts(self, testdate):
        self.shift_list.add(testdate)
        contiguous_shifts = (deviation_check(self.controller,testdate.date))
        for shift in contiguous_shifts:
            self.shift_list.add(shift)

        self.shift_list = sorted(self.shift_list,  key=operator.attrgetter('date'))
        return self.shift_list

    def get_date(self, date):
        for shift in self.shift_list:
            if shift.date == date:
                return shift
            else:
                return False

    def add_date(self, startdate, enddate=None):
        if enddate is None:
            enddate = startdate + datetime.timedelta(days=1)
        new_dates = project_schedule(startdate, enddate, self.controller)
        for shift in new_dates:
            self.shift_list.add(shift)

        return self.get_date(startdate)


def project_schedule(start_date, end_date, userprofile):
    #/todo currently does no handle non repeating events
    '''

    :param start_date:
    :param end_date:
    :param userprofile:
    :return: list of all scheduled events during time frame
    '''
    range_day_count = (end_date - start_date).days  # num days in query range
    if range_day_count == 0:
        range_day_count +=1
    recurring_event_list = Master_schedule.objects.filter(shift = userprofile.shift)  # gather all master schedule items for controller shift
    #print(recurring_event_list)
    event_calendar = []

    for i in range(range_day_count): # go through each day in requested range
        day = start_date + datetime.timedelta(days=i)
        is_off = False  # flipped if on PTO
        #find PTO
        for current_shift in recurring_event_list:
            if current_shift.is_repeating: # this is why it wont pick up oneoff events
                if check_date(current_shift, day):
                    new_event = DateItem(current_shift, userprofile, day)
                    event_calendar.append(new_event)

        if PTO_table.objects.filter(date_pto_taken=day, coverage=userprofile).exists():
            try:
                coverage_event = PTO_table.objects.get(date_pto_taken=day, coverage=userprofile)
                other_controller_schedule = project_schedule(day,day+datetime.timedelta(days=1),coverage_event.user)
                shift_object = other_controller_schedule[0]
                shift_object.change_controller(userprofile)
                event_calendar.append(shift_object)
            except:
                pass
        if PTO_table.objects.filter(date_pto_taken=day, user=userprofile, type='DND').exists():
            dnd = PTO_table.objects.get(date_pto_taken=day, user=userprofile, type='DND')
            new_event = DateItem(dnd, userprofile,day,dnd=True)
            event_calendar.append(new_event)

    return event_calendar


def one_shift_per_controller(controller, dateitem):
    """
    this does not take into account PTO or availability just not schedule on more than one shift at a time, no nights to
    days
    :param controller: pass a controller object
    :param console_shift: dateitem
    :return: boolean as to whether or not this controller is currently eligible to work
    """
    date = dateitem.date
    start_date = date - datetime.timedelta(days=1)
    end_date= date + datetime.timedelta(days=1)
    controller_schedule = project_schedule(start_date,end_date,controller)
    one_day_before = controller_schedule[0]
    next_day = controller_schedule[2]

    testdates = Console_schedule.objects.filter(date__range=[one_day_before, next_day], controller=controller)

    available = True  # flips to true if available

    previous_day = None
    day_of = None
    day_after = None
    # create cases
    for day in testdates:
        # this creates list for the switch below
        if day.date < dateitem.date:
            previous_day = day.is_day
        elif day.date == dateitem.date:
            day_of = day.is_day
        elif day.date > dateitem.date:
            day_after = day.is_day

    outcomes = [console_shift, previous_day, day_of, day_after]

    if outcomes[0].is_day is True:  # console shift schedule is a day shift
        if outcomes[1] is False:  # if previous night shift is a night
            available = False
            return available
    elif outcomes[2] is not None:  # if scheduled the day of
        available = False  # already scheduled for that day.
    elif outcomes[0] is False:  # if a night shift
        if outcomes[3] is True:  # if the next shift is a day shift
            available = False
    return available


def find_connected_shifts(controller, date,forward, previous_shift_time = None,off_count=0, window=[], loop_count =0):
    '''
    this is a recursive statement to find all the dates forward or backward of a test date that the controller works
    without a reset
    :param controller: controller that you are testing
    :param date: date to test
    :param forward: if true, you are looking forward of this date
    :param previous_shift_time: default value used for recursion
    :param off_count: leave blank
    :param window: list of shifts worked with out reset period
    :return:
    '''

    # variables
    thirtysixhours = (126000)*-1
#/todo: does not work in a DOD where the target is O


    if len(window)> 0 and loop_count == 0:
        window = [] # this is put in to garbage collect
    if off_count <2: # check for exit condition
        #new_window = []
        # check the previous date, if controller is scheduled add it to list and check the next date

       #/todo create try block that gets the testdate from oqcontroller, else it goes the normal way
        #testdate = project_schedule(date,date,controller)

        testdate = controller.add_date(date)

        #print(testdate.date)
        #if len(testdate)>0
        if testdate: # Controller is scheduled for this test day
            dateobject = testdate

            #print("%s %s %s" % (dateobject.date, dateobject.controller, controller.controller))
            #if dateobject.controller != controller or dateobject.dnd is True:
            if dateobject.dnd is True:
                #print("%s %s %s" % (dateobject.date, dateobject.controller, controller))
                off_count += 1
                if forward is True:
                    date += datetime.timedelta(days=1)
                else:
                    date -= datetime.timedelta(days=1)
                loop_count += 1
                return find_connected_shifts(controller, date, forward, previous_shift_time, off_count, window, loop_count)
            else:
                shift_start_time = dateobject.shift_start_time
                end_shift_time = dateobject.shift_end_time


                if forward is True:  # time off check for forward
                    try:
                        timeoff = shift_start_time - previous_shift_time

                        if abs(timeoff.total_seconds()) >= abs(thirtysixhours):
                            off_count += 2 # exit the loop
                            return find_connected_shifts(controller, date, forward, previous_shift_time, off_count, window,
                                                         loop_count)
                    except: pass

                elif forward is False:
                    try:
                        timeoff = end_shift_time - previous_shift_time
                        #print(timeoff.total_seconds())
                        if abs(timeoff.total_seconds()) >= abs(thirtysixhours):
                            off_count += 2
                            return find_connected_shifts(controller, date, forward, previous_shift_time, off_count, window,
                                                         loop_count)
                    except:
                        pass

                if forward is True:  #pass appropriate previous_shift_time on to the next call
                    previous_shift_time = end_shift_time
                else:
                    previous_shift_time = shift_start_time
                # call the next day base on the directions
                if forward is True:
                    date += datetime.timedelta(days=1)
                else:
                    date -= datetime.timedelta(days=1)


                loop_count += 1
                window.append(dateobject)
                return find_connected_shifts(controller,date, forward,previous_shift_time,off_count,window, loop_count)  # start the recursion


        else: # if the controller was not scheduled, then increment off count and call the function again
            off_count += 1
            if forward is True:
                date += datetime.timedelta(days=1)
            else:
                date -= datetime.timedelta(days=1)
            loop_count +=1
            return find_connected_shifts(controller, date, forward, previous_shift_time, off_count, window, loop_count)

    else:  # escape condition reached return the date
        #new_window = window  # shuffle this so it wont stack
        new_window = controller.shift_list

        previous_shift_time = None
        off_count = 0
        window = []

        return new_window

def deviation_check(controller, date):
    '''

    :param controller:
    :param date: standard test date
    :param testshift: Dateitem of shift that might be assigend to controller
    :return: list of contiguous shift
    '''
    controller_object = OqController(controller)

    string_of_shifts = set()
    forward_search = find_connected_shifts(controller_object,date, True)
    backward_search = find_connected_shifts(controller_object,date, False)

    for shift_object in backward_search:
        #print(shift_object.date)
        #print('********')
        string_of_shifts.add(shift_object)
    for shift_object in forward_search:
        string_of_shifts.add(shift_object)
    for shift in string_of_shifts:
        print(shift.date)
    return sorted(string_of_shifts, key=operator.attrgetter('date'))

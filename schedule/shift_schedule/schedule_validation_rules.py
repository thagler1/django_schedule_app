from .models import Shift, UserProfile, Console, Master_schedule, Console_schedule, Console_oq
import datetime
from django.core.cache import cache


def one_shift_per_controller(controller, console_shift):
    """
    this does not take into account PTO or availability just not schedule on more than one shift at a time, no nights to
    days
    :param controller: pass a controller object
    :param console_shift: pass the console_shift object
    :return: boolean as to whether or not this controller is currently eligible to work
    """
    date = console_shift.date
    one_day_before = date - datetime.timedelta(days=1)
    next_day = date + datetime.timedelta(days=1)

    testdates = Console_schedule.objects.filter(date__range=[one_day_before, next_day], controller=controller)

    available = True  # flips to true if available

    previous_day = None
    day_of = None
    day_after = None
    # create cases
    for day in testdates:
        # this creates list for the switch below
        if day.date < console_shift.date:
            previous_day = day.is_day
        elif day.date == console_shift.date:
            day_of = day.is_day
        elif day.date > console_shift.date:
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
    # CVFGBTYHNJMUKILO;P'[]
    # =\]
    # variables
    thirtysixhours = (126000)*-1
#/todo: does not work in a DOD where the target is O
#/todo: returns a list that is out of order

    if len(window)> 0 and loop_count == 0:
        window = []
    if off_count <2:
        #new_window = []
        # check the previous date, if controller is scheduled add it to list and check the next date
        testdate = Console_schedule.objects.filter(date=date, controller=controller)
        # create shift start and end times


        if testdate.exists(): # Controller is scheduled for this test day
            testdate = Console_schedule.objects.get(date=date, controller=controller)
            #print(testdate.controller, testdate.date)

            if testdate.is_day is True:  # if day shift set the start and end times
                shift_start_time = date.replace(hour=6)
                end_shift_time = date.replace(hour=18)
            else:  # its a night shift, set the start and end time
                shift_start_time = date.replace(hour=18)
                end_shift_time = shift_start_time + datetime.timedelta(hours=12)
            print(shift_start_time, end_shift_time)
            if forward is True:  # time off check for forward
                try:
                    print("forward")
                    timeoff = shift_start_time - previous_shift_time
                    if timeoff.total_seconds() >= thirtysixhours*-1:
                        off_count += 2
                        print("exited on forward")
                        return find_connected_shifts(controller, date, forward, previous_shift_time, off_count, window,
                                                     loop_count)
                except: pass

            elif forward is False:
                try:
                    print("Backward")
                    timeoff = end_shift_time - previous_shift_time
                    #print(timeoff.total_seconds())
                    if timeoff.total_seconds() >= thirtysixhours:
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
            window.append(testdate)
            return find_connected_shifts(controller,date, forward,previous_shift_time,off_count,window, loop_count)  # start the recursion


        elif testdate.exists() is False: # if the controller was not scheduled, then increment off count and call the function again
            off_count += 1
            if forward is True:
                date += datetime.timedelta(days=1)
            else:
                date -= datetime.timedelta(days=1)
            loop_count +=1
            return find_connected_shifts(controller, date, forward, previous_shift_time, off_count, window, loop_count)

    else:  # escape condition reached return the date
        new_window = window  # shuffle this so it wont stack
        previous_shift_time = None
        off_count = 0
        window = []

        return new_window

def deviation_check(controller, date):
    string_of_shifts = set()
    forward_search = find_connected_shifts(controller,date, True)
    backward_search = find_connected_shifts(controller,date, False)

    for shift_object in backward_search:
        string_of_shifts.add(shift_object)
    for shift_object in forward_search:
        string_of_shifts.add(shift_object)

    return string_of_shifts










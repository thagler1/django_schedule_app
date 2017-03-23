from .models import Shift, UserProfile, Console, Master_schedule, Console_schedule, Console_oq
import datetime


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

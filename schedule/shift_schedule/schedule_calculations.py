from .models import Shift, UserProfile, Console, Master_schedule, Console_schedule, Console_oq, PTO_table
import datetime
from collections import namedtuple


class DateItem:
    def __init__ (self, date_object):
        self.date_object = date_object

    def is_on_day(self, date):
        day_delta = date - self.date_object.date
        if day_delta.days % self.date_object.repeat_interval != 0:
            return False
        else:
            return True

    def model_object(self):
        #print(self.date_object)
        return self.date_object

    def is_repeating(self):
        return self.date_object.is_repeating




def project_schedule(start_date, end_date, userprofile):
    range_day_count = end_date - start_date  # num days in query range

    range_day_count = range_day_count.days
    if range_day_count ==0:
        range_day_count +=1
    master_schedule = Master_schedule.objects.all()  # gather all master schedule items
    recurring_event_list = []
    for recuring_event in master_schedule:
        if recuring_event.is_repeating is True:
            recurring_event_list.append(DateItem(recuring_event))
    event_calendar = []
    Events = namedtuple('Event','model_object date pto original_controller') # Calendar of all recurring events. not controller specific

    for i in range(range_day_count):
        day = start_date + datetime.timedelta(days=i)
        pto_events = PTO_table.objects.filter(date_pto_taken=day, user=userprofile)

        is_off = False
        overtime = False
        if PTO_table.objects.filter(date_pto_taken=day, coverage=userprofile).exists():
            coverage_events = PTO_table.objects.get(date_pto_taken=day, coverage=userprofile)
            shift_object = project_schedule(day,day,coverage_events.user)
            master_shift_object = shift_object[0] # this could cause problems if assigned to more than one shift for coverage

            new_event = Events(master_shift_object.model_object,day,None, coverage_events.user )
            print(new_event)
            event_calendar.append(new_event)
        for current_shift in recurring_event_list:

            if current_shift.is_repeating() is True:  # found repeating shift start calculation
                if current_shift.is_on_day(day) == True and current_shift.model_object().shift == userprofile.shift:
                    for pto in pto_events:
                        if pto.supervisor_approval and pto.manager_approval:
                            is_off = True
                        else:
                            pass
                        # Check for coverage

                    if is_off:
                        new_event = Events(current_shift.model_object(), day, pto, None)
                        event_calendar.append(new_event)
                    else:
                        new_event = Events(current_shift.model_object(), day, None, None)
                        event_calendar.append(new_event)
    #print(event_calendar)
    return event_calendar
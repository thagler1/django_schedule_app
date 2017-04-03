from .models import Shift, UserProfile, Console, Master_schedule, Console_schedule, Console_oq
import datetime

class DateItem:
    def __init__ (self, date_object):
        self.date_object = date_object

    def is_on_day(self, date):
        day_delta = date - self.date_object.date
        if day_delta.days % self.date_object.reapeat_interval != 0:
            return False
        else:
            return date
    def is_repeating(self):
        return self.date_object.is_repeating
   


def project_schedule(start_date, end_date):
    master_schedule = Master_schedule.objects.all()  # gather all master schedule items
    recurring_event_list = [DateItem(recuring_event) for recuring_event in master_schedule, if master_schedule.is_repeating == True]
    event_calendar
    
    range_day_count = (end_date-start_date).days # num days in query range
    for i in range(range_day_count):
        day = start_date + timedelta(days=i)
        for current_shift in recurring_event_list:
            
            if current_shift.is_repeating is True:  # found repeating shift start calculation
                if current_shift.is_on_day(day) == True
                    event_calendar((current_shift,day))
    return event_calendar
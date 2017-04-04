from .models import Shift, UserProfile, Console, Master_schedule, Console_schedule, Console_oq
import datetime

class DateItem:
    def __init__ (self, date_object):
        self.date_object = date_object

    def is_on_day(self, date):
        day_delta = date - self.date_object.date
        if day_delta.days % self.date_object.repeat_interval != 0:
            return False
        else:
            return True
    def is_repeating(self):
        print("running check")
        self.date_object.is_repeating
        return self.date_object.is_repeating
   


def project_schedule(start_date, end_date):
    range_day_count = end_date - start_date  # num days in query range
    range_day_count = range_day_count.days
    master_schedule = Master_schedule.objects.all()  # gather all master schedule items
    recurring_event_list = []
    for recuring_event in master_schedule:
        if recuring_event.is_repeating is True:
            print("Found event")
            recurring_event_list.append(DateItem(recuring_event))
    event_calendar = []
    

    for i in range(range_day_count):
        day = start_date + datetime.timedelta(days=i)
        for current_shift in recurring_event_list:
            print(current_shift)
            if current_shift.is_repeating() is True:  # found repeating shift start calculation
                print(current_shift)
                if current_shift.is_on_day(day) == True:

                    event_calendar.append((current_shift,day))
    return event_calendar
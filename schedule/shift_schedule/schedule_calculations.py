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
        








def project_schedule(start_date, end_date):
    master_schedule = Master_schedule.objects.all()  # gather all master schedule items
    for current_shift in master_schedule:
        if current_shift.is_repeating is True:  # found repeating shift start calculation
            pass
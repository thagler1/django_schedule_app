from .models import Shift, UserProfile, Console, Master_schedule, Console_schedule, Console_oq, PTO_table
import datetime
from collections import namedtuple



def check_date(master_schedule_object,testdate):
    day_delta = testdate - master_schedule_object.date
    if day_delta.days % master_schedule_object.repeat_interval !=0:
        return False
    else: return True


class DateItem:
    #/todo possible logic problem with self.date
    #/todo develope methof for assigning console
    def __init__ (self, date_object, controller,date=None, console = None, pto = None):
        # date object is master shift schedule object
        self.date_object = date_object
        self.date = date # optional allows access to date worked
        self.controller = controller
        self.shift = controller.shift
        self.original_controller = controller
        self.console = self.set_console()
        self.is_on_pto = False
        self.pto = self.check_pto()


    def check_pto(self):
        '''
        whether the controller is on PTO or not
        :param: date
        :return: binarry
        '''

        if PTO_table.objects.filter(date_pto_taken=self.date, user=self.controller).exists():
            pto_return = PTO_table.objects.filter(date_pto_taken=self.date, user=self.original_controller)
            for pto_event in pto_return:
                #print(pto_event)
                if pto_event.supervisor_approval is True and pto_event.manager_approval is True:
                    self.is_on_pto = True

                    self.pto = pto_event
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


def project_schedule(start_date, end_date, userprofile):
    #/todo currently does no handle non repeating events
    '''

    :param start_date:
    :param end_date:
    :param userprofile:
    :return: list of all scheduled events during time frame
    '''
    range_day_count = (end_date - start_date).days  # num days in query range
    recurring_event_list = Master_schedule.objects.filter(shift = userprofile.shift)  # gather all master schedule items for controller shift
    #print(recurring_event_list)
    event_calendar = []

    for i in range(range_day_count): # go through each day in requested range
        day = start_date + datetime.timedelta(days=i)
        is_off = False  # flipped if on PTO
        #find PTO
        for current_shift in recurring_event_list:
            if current_shift.is_repeating:
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
    return event_calendar
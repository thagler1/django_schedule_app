from .models import Shift, UserProfile, Console, Master_schedule, Console_schedule, Console_oq, PTO_table
import datetime


class Node(object):
    def __init__(self, data):
        self.left = None
        self.right = None
        self.data = data

    def __repr__(self):
        return repr((self.data, self.left, self.right))


class Tree(object):
    def __init__(self):
        self.root = None

    def __repr__(self):
        return repr(self.root)

    # Private helper functions
    def _insert(self, data, root):
        if data < root.data:
            if root.left is None:
                root.left = Node(data)
            else:
                self._insert(data, root.left)
        else: # data >= root.data:
            if root.right is None:
                root.right = Node(data)
            else:
                self._insert(data, root.right)

    def _traverse(self, root, mode):
        if mode == 'pre':
            yield root.data
        if root.left:
            for u in self._traverse(root.left, mode):
                yield u
        if mode == 'in':
            yield root.data
        if root.right:
            for u in self._traverse(root.right, mode):
                yield u
        if mode == 'post':
            yield root.data

    # Wrapper Functions
    def insert(self, data):
        if self.root == None:
            self.root = Node(data)
        else:
            self._insert(data, self.root)

    def preOrder(self):
        for u in self._traverse(self.root, 'pre'):
            yield u

    def inOrder(self):
        for u in self._traverse(self.root, 'in'):
            yield u

    def postOrder(self):
        for u in self._traverse(self.root, 'post'):
            yield u


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

    def __init__ (self, date_object, controller,date=None, console = None, pto = None, dnd = False):
        # date object is master shift schedule object
        self.date_object = date_object # this is the actual Master shift Model
        self.date = date # optional allows access to date worked
        self.controller = controller
        self.shift = controller.shift
        self.original_controller = controller # this is meant to show who was supposed to work
        self.console = self.set_console()
        self.is_on_pto = False
        self.pto = self.check_pto()
        self.dnd = dnd # flips if the controller is on PTO
        self.set_shift_times()
        self.time_off = 0




    def check_pto(self):
        '''
        whether the controller is on PTO or not
        :param: date
        :return: binarry
        '''

        if PTO_table.objects.filter(date_pto_taken=self.date, user= self.original_controller).exists():
            pto_return = PTO_table.objects.filter(date_pto_taken=self.date, user= self.original_controller)
            for pto_event in pto_return:
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


    def qualified_coverage(self):
        oq_controller = Console_oq.objects.filter(console = self.console)
        controller_list = []
        for controller in oq_controller:
            controller_list.append(controller)
        return controller_list


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

    def set_time_off(self,time_int):
        self.time_off = time_int
        return self.time_off

    def __eq__(self, other):
        if isinstance(other,self):

            return self.date == other.date
        return NotImplemented

    def __gt__(self,other):
        return self.date > other.date
    def __lt__(self,other):
        return self.date < other.date
    def __ge__(self,other):
        return self.date >= other.date
    def __le__(self,other):
        return self.date <= other.date


    def __hash__(self):
        return hash(self.date)

    def __repr__(self):
        return repr((self.date, self.controller, self.console.console_name, self.time_off))


class OqController:

    def __init__(self, UserProfile):
        self.controller = UserProfile
        self.score = 0
        self.oqs = self.check_oqs()
        self.pto_days = Tree()



    def check_oqs(self):
        '''
        :return: queryset
        '''
        self.oq_list = Console_oq.objects.filter(controller=self.controller)
        return self.oq_list

    def build_schedule(self, date):
        #/todo i need to work on this logic
        self.schedule = Tree()
        scheduled_days = project_schedule(date-datetime.timedelta(days = 20), date+datetime.timedelta(days=20), self.controller)
        for day in scheduled_days:
            if day.controller == self.controller:
                self.schedule.insert(day)
            if day.original_controller == self.controller and day.is_on_pto: # not sure why i am adding pto days
                self.pto_days.insert(day)

        self.calc_time_off()
    #def build_test_scheudle(self):

    def calc_time_off(self):
        prev_shift = None
        for shift in self.schedule.inOrder():
            if prev_shift is None:
                prev_shift = shift
            else:
                timeoff = shift.shift_start_time - prev_shift.shift_end_time
                prev_shift = shift
                shift.set_time_off((timeoff.total_seconds()/60/60))

    def deviation_check(self, testdate = None, date =None):
        '''
        given a test dateItem this will build a contigous shift string
        :param testdate:
        :param date:
        :return:
        '''
        if testdate: # see if you were passed a testdate
            for day in self.schedule.inOrder(): # scroll through schedule and look for start and end times that match testdate
                if day.dnd is False or testdate.is_on_pto is False:
                    if testdate.shift_start_time == day.shift_start_time:
                        self.score +=5

                    elif testdate.shift_start_time == day.shift_end_time:
                        self.score +=5

                    elif testdate.shift_end_time == day.shift_start_time:
                        self.score +=5

                    elif testdate.shift_end_time == day.shift_end_time:
                        self.score +=5

            testdate.set_controller(self.controller) # assign testdate to controller
            self.schedule.insert(testdate) # insert into schedule
        else:
            testdate = date

        self.deviations = Tree() #create tree to store contiguous objects
        self.calc_time_off()
        check_list = []
        for day in self.schedule.inOrder():
            check_list.append(day)
        for day in reversed(check_list):
            if day <= testdate:
                if day.time_off < 35:
                    self.deviations.insert(day)
                if day.time_off >= 35:

                    self.deviations.insert(day)
                    break

        for day in self.schedule.inOrder():
            if day > testdate:
                if day.time_off < 35:
                     self.deviations.insert(day)
                if day.time_off >= 35:
                    #self.deviations.insert(day)
                    break
    def is_available(self, testdate):
        for day in self.schedule:
            if testdate == day:
                return False

    def coverage_check(self, testdate):
        self.deviation_check(testdate)
        self.contiguous_hours = 0
        for shift in self.deviations.inOrder():
            self.contiguous_hours+=12

        return self.contiguous_hours

    def score_coverage(self,pto_event, dateItem):
        '''
        this function will score pto coverage. This is the only function that needs to run in order to build, check and
        score pto coverage
        :param dateItem: this is the dateitem for the shift that needs to be covered
        :return: score for coverage event
        '''
        testdate = pto_event.date_pto_taken
        self.build_schedule(testdate)
        self.coverage_check(dateItem)

        MAX_HOURS = 65
        DEVIATION_WEIGHT = 3
        PTO_WEIGHT = 2
        DND_WEIGHT = 1

        # check for deviation
        if self.contiguous_hours > MAX_HOURS:
            self.score += DEVIATION_WEIGHT

        # check for PTO, exclude DND
        try:
            for day in self.pto_days.inOrder():
                if day.date == testdate:
                    self.score += PTO_WEIGHT
        except:
            pass
        # check for DND days
        for day in self.schedule.inOrder():
            if day.date == testdate and day.dnd is True:
                self.score += DND_WEIGHT






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
    event_calendar = []

    for i in range(range_day_count): # go through each day in requested range

        day = start_date + datetime.timedelta(days=i)
        #find PTO
        for current_shift in recurring_event_list:
            if current_shift.is_repeating: # this is why it wont pick up oneoff events
                if check_date(current_shift, day):
                    new_event = DateItem(current_shift, userprofile, day)
                    event_calendar.append(new_event)
            #/todo check for non repeating events

        if PTO_table.objects.filter(date_pto_taken=day, coverage=userprofile).exists():
            try:
                # for day search for pto coverage. if schedule, create a dateItem with the control assigned to it
                coverage_event = PTO_table.objects.get(date_pto_taken=day, coverage=userprofile)
                other_controller_schedule = project_schedule(day,day+datetime.timedelta(days=1),coverage_event.user)
                shift_object = other_controller_schedule
                shift_object.change_controller(userprofile)
                event_calendar.append(shift_object)
            except:
                pass
        if PTO_table.objects.filter(date_pto_taken=day, user=userprofile, type='DND').exists():
            dnd = PTO_table.objects.get(date_pto_taken=day, user=userprofile, type='DND')
            new_event = DateItem(dnd, userprofile,day,dnd=True)
            event_calendar.append(new_event)


    if len(event_calendar)==1:
        return event_calendar[0]
    return event_calendar

def by_score_key(controller):
    # created for sorting purposes in assign_coverage
    return controller.score


def assign_coverage(pto_event):
    controller_return = []
    pto_dateItem = project_schedule(pto_event.date_pto_taken, pto_event.date_pto_taken, pto_event.user)
    console = pto_dateItem.console
    qualified_controllers = pto_dateItem.qualified_coverage()
    for controller in qualified_controllers:
        if controller.controller != pto_dateItem.original_controller:
            new_controller = OqController(controller.controller)
            new_controller.score_coverage(pto_event,pto_dateItem)
            controller_return.append(new_controller)

    pto_event.coverage = sorted(controller_return, key= by_score_key)[0].controller
    pto_event.save()

    return controller_return

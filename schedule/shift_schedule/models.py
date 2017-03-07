from django.db import models
from django.contrib.auth.models import User #used fro user profiles



class Supervisor(models.Model):
    '''
    shift supervisors. They manage the schedules for all shifts.
    '''
    name = models.CharField(max_length=120)
    email = models.CharField(max_length=120)

    def __str__(self):
        return self.name




class Shift(models.Model):
    '''
    this shift itself is agnostic the the supervisor, a supervisor can be replaced on a shift without effecting the
    underlying shift characteristics
    '''
    shift_id = models.CharField(max_length=20)
    supervisor = models.ForeignKey(Supervisor)
    zero_day = models.IntegerField()

    def __str__(self):
        return self.shift_id

    def supervisor_name(self):
        supervisor_name = Supervisor.objects.get(name = self.supervisor)
        return supervisor_name



class Manager(models.Model):
    '''
    employees and consoles are assigned a manager. This model is more for reporting purposes
    '''
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    '''
    controllers can work multiple consoles, and can fill schedule openings on other shifts, but they are assigned a
    shift, and scheduled for a primary console (found in employee oq)
    '''
    hire_date = models.DateField(blank=True, default ="1950-01-01")
    pto = models.IntegerField(default=120, blank= True)
    manager = models.ForeignKey(Manager, blank=True,null = True)
    shift = models.ForeignKey(Shift, blank=True,null = True)
    user = models.OneToOneField(User)
    phone = models.CharField(max_length=20, blank = True, default="")


    def list_oqs(self):
        alloqs = Console_oq.objects.filter(controller = self.id)
        return alloqs
    def onshift(self):
        allshifts = Shift.objects.filter(id = self.shift)
        return allshifts
    def full_name(self):
        user_object = User.objects.get(id = self.user.id)
        user_last_name = user_object.last_name
        user_first_name = user_object.first_name

        return "%s %s"%(user_first_name, user_last_name)
    def __str__(self):
       return self.full_name()


class Console(models.Model):
    '''
    console have a manager, and a list of qualified employees(console_oq) and have to be staffed 24 seven
    '''
    console_name = models.CharField(max_length=100)
    manager = models.ForeignKey(Manager)

    def __str__(self):
        return self.console_name
    def deskname(self):
        return "%s"%(self.console_name)

class Console_oq(models.Model):
    '''
    this manages which employees are qualified to work which consoles. This is the main table used for scheduling.
    employees can be qualified on more than one console, but are scheduled based on their primary console and the
    employees assigned shift
    '''
    controller = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    oq_date = models.DateField()
    console = models.ForeignKey(Console)
    primary_console = models.BooleanField(default=True)

    def readable(self):
        console_name = Console.objects.get(console_name = self.console)
        controller_object = User.objects.get(id = self.controller.user.id)
        controller_first_name = controller_object.first_name
        controller_last_name = controller_object.last_name
        return "%s %s"%(console_name, self.oq_date)



    def __str__(self):
        console_name = Console.objects.get(console_name = self.console)
        controller_object = User.objects.get(id = self.controller.user.id)
        controller_first_name = controller_object.first_name
        controller_last_name = controller_object.last_name
        return "%s %s %s %s"%(controller_first_name, controller_last_name, console_name, self.oq_date)

class Contoller_shift(models.Model):
    employee = models.ForeignKey(UserProfile)
    workdate = models.DateField()
    console = models.ForeignKey(Console)
    holiday = models.BooleanField(default=False)
    rover = models.BooleanField(default=False)
    meeting = models.BooleanField(default=False)


    def __str__(self):
        employee_name = UserProfile.objects.get(user = self.employee)
        console_name = Console.objects.get(console_name = self.console)


        return "%s  - %s - %s"%(self.workdate, employee_name, console_name)



class Console_schedule(models.Model):
    '''
    this is the schedule table. each desk is assigned a dayshift and a night shift, based on the master schedule. this
    serves as the record for who is responsible to work each date on each console
    '''
    deskname = models.ForeignKey(Console)
    is_day = models.BooleanField()
    shift = models.ForeignKey(Shift, null=True)
    controller = models.ForeignKey(UserProfile, null=True)
    is_holiday = models.BooleanField(default=False)
    off_schedule_controller = models.BooleanField(default=False)
    date = models.DateField(default='2000-01-01')

    def __str__(self):
       #shift_supervisor = Supervisor.objects.get(name = shift_object)
        return "%s %s" %(self.date, self.deskname)
    def which_shift(self):
        if self.is_day == True:
            return 'D'
        else:
            return 'N'

class Master_schedule(models.Model):
    '''
    this is a schedule temple based on information contained in the shift table. a rule is written in the singals.py
    file for creating a schedule for each shift. This information is used to create the console_schedule which serves as
    the official schedule.
    '''
    shift = models.ForeignKey(Shift)
    date = models.DateField()
    is_day = models.BooleanField()

    def __str__(self):
        return "%s %s"%(Shift.objects.get(shift_id = self.shift), self.date)


from .signals import initialize_desk_schedule
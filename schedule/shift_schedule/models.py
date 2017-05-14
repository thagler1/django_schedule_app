from django.db import models
import PIL
import os
from django.contrib.auth.models import User #used fro user profiles
from django.utils.deconstruct import deconstructible

@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        filename = '{}.{}'.format(instance.pk, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename)

path_and_rename = PathAndRename("")


class Supervisor(models.Model):
    '''
    shift supervisors. They manage the schedules for all shifts.
    '''
    name = models.CharField(max_length=120)
    email = models.CharField(max_length=120)

    def __str__(self):
        return self.name




class Manager(models.Model):
    """
    employees and consoles are assigned a manager. This model is more for reporting purposes
    """
    name = models.ForeignKey('UserProfile', limit_choices_to={'is_manager':True}, related_name='Operations_Manager')
    email = models.CharField(max_length=100)

    def __str__(self):
        return self.name.full_name()

class UserProfile(models.Model):
    """
    controllers can work multiple consoles, and can fill schedule openings on other shifts, but they are assigned a
    shift, and scheduled for a primary console (found in employee oq)
    """

   

    hire_date = models.DateField(blank=True, default ="1950-01-01")
    pto = models.IntegerField(default=120, blank=True)
    manager = models.ForeignKey('UserProfile', limit_choices_to={'is_manager':True}, blank=True, null=True)
    shift = models.ForeignKey('Shift', blank=True, null=True)
    user = models.OneToOneField(User)
    phone = models.CharField(max_length=20, blank=True, default="")
    profile_image = models.ImageField(upload_to=path_and_rename, blank=True, null=True)
    is_supervisor = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)


    def list_oqs(self):
        alloqs = Console_oq.objects.filter(controller=self.id)
        return alloqs


    def full_name(self):
        user_object = User.objects.get(id=self.user.id)
        user_last_name = user_object.last_name
        user_first_name = user_object.first_name

        return "%s %s" % (user_first_name, user_last_name)

    def __str__(self):
        return self.full_name()

class Shift(models.Model):
    """
    this shift itself is agnostic the the supervisor, a supervisor can be replaced on a shift without effecting the
    underlying shift characteristics
    """

    shift_id = models.CharField(max_length=20)
    supervisor = models.ForeignKey(UserProfile, limit_choices_to={'is_supervisor': True},related_name='Supervisor')
    zero_day = models.IntegerField()

    def __str__(self):
        return self.shift_id

    def supervisor_name(self):
        supervisor_name = UserProfile.objects.get(name=self.supervisor)
        return supervisor_name.Full_name

class Console(models.Model):
    """
    console have a manager, and a list of qualified employees(console_oq) and have to be staffed 24 seven
    """
    console_name = models.CharField(max_length=100)
    manager = models.ForeignKey(UserProfile, limit_choices_to={'is_manager':True})
    address = models.CharField(max_length=10, null=True)

    def __str__(self):
        return self.console_name

    def deskname(self):
        return "%s" % self.console_name


class Console_oq(models.Model):
    """
    this manages which employees are qualified to work which consoles. This is the main table used for scheduling.
    employees can be qualified on more than one console, but are scheduled based on their primary console and the
    employees assigned shift
    """
    controller = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    oq_date = models.DateField()
    console = models.ForeignKey(Console)
    primary_console = models.BooleanField(default=True)

    def __str__(self):
        console_name = Console.objects.get(console_name = self.console)
        controller_object = User.objects.get(id = self.controller.user.id)
        controller_first_name = controller_object.first_name
        controller_last_name = controller_object.last_name
        return "%s %s %s %s" % (controller_first_name, controller_last_name, console_name, self.oq_date)


class Contoller_shift(models.Model):
    employee = models.ForeignKey(UserProfile)
    workdate = models.DateField()
    console = models.ForeignKey(Console)
    holiday = models.BooleanField(default=False)
    rover = models.BooleanField(default=False)
    meeting = models.BooleanField(default=False)

    def __str__(self):
        employee_name = UserProfile.objects.get(user=self.employee)
        console_name = Console.objects.get(console_name=self.console)
        return "%s  - %s - %s"%(self.workdate, employee_name, console_name)


class Console_schedule(models.Model):
    """
    this is the schedule table. each desk is assigned a dayshift and a night shift, based on the master schedule. this
    serves as the record for who is responsible to work each date on each console
    """
    deskname = models.ForeignKey(Console)
    is_day = models.BooleanField(default=True,)
    shift = models.ForeignKey(Shift, null=True)
    controller = models.ForeignKey(UserProfile, null=True)
    is_holiday = models.BooleanField(default=False)
    off_schedule_controller = models.BooleanField(default=False)
    date = models.DateField(default='2000-01-01')
    #is_deviation = models.BooleanField(default=False)

    def __str__(self):
        return "%s %s" % (self.date, self.deskname)

    def which_shift(self):
        if self.is_day is True:
            return 'D'
        else:
            return 'N'


class Master_schedule(models.Model):
    """
    this is a schedule temple based on information contained in the shift table. a rule is written in the singals.py
    file for creating a schedule for each shift. This information is used to create the console_schedule which serves as
    the official schedule.
    """
    shift = models.ForeignKey(Shift)
    date = models.DateField()
    is_day = models.BooleanField()
    is_repeating = models.BooleanField(default=True)
    repeat_start = models.DateField(default="2017-01-01")
    repeat_interval = models.BigIntegerField(default= 28)
    repeat_end = models.DateField(default="2099-12-31")

    def __str__(self):
        return "%s %s" % (Shift.objects.get(shift_id=self.shift), self.date)

    def which_shift(self):
        if self.is_day is True:
            return 'D'
        else:
            return 'N'

class PTO_table(models.Model):
    """
    table used for tracking and approving pto
    """
    regularPTO = 'PTO'
    shortnoticePTO = 'PTOS'
    juryduty = 'J'
    bereavement = 'B'
    shortterm_disability = 'STD'
    longterm_disability = 'LTD'
    DoNotDisturb = 'DND'

    pto_choices = (
        (regularPTO, 'Regular PTO'),
        (shortnoticePTO, 'Short notice PTO'),
        (juryduty, 'Jury Duty'),
        (bereavement, "Bereavement"),
        (shortterm_disability, 'Short Term Disability'),
        (longterm_disability, 'Long Term Disability'),
        (DoNotDisturb, 'Do Not Disurb')
    )

    date_requested = models.DateField()
    date_pto_taken = models.DateField()
    user = models.ForeignKey(UserProfile)
    coverage = models.ForeignKey(UserProfile, default=None,blank=True,null=True, related_name="+")
    #console_date = models.ForeignKey(Console_schedule)
    supervisor_approval = models.BooleanField(default=False)
    manager_approval = models.BooleanField(default=True)
    shift_type = models.CharField(max_length=20, null=True)
    notes = models.TextField(default="")
    type = models.CharField(max_length=4,
                            choices=pto_choices,
                            default=regularPTO)
    console = models.ForeignKey(Console, default=None, null=True)


    def __str__(self):
        controller_object = User.objects.get(id=self.user.user.id)
        controller_first_name = controller_object.first_name
        controller_last_name = controller_object.last_name

        return "%s %s %s %s" % (controller_first_name, controller_last_name, self.date_pto_taken,self.console)

class Console_Map(models.Model):
    console = models.ForeignKey(Console)
    row = models.IntegerField()
    column = models.IntegerField()


    def __str__(self):
        console_name = Console.objects.get(console_name = self.console)
        return "%s at Row: %s, Column: %s" % (console_name, self.row, self.column)



from .signals import add_pto_to_schedule
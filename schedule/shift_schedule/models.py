from django.db import models


class Supervisor(models.Model):
    name = models.CharField(max_length=120)
    email = models.CharField(max_length=120)

    def __str__(self):
        return self.name




class Shift(models.Model):
    shift_id = models.CharField(max_length=20)
    supervisor = models.ForeignKey(Supervisor)
    zero_day = models.IntegerField()

    def __str__(self):
        return self.shift_id

    def supervisor_name(self):
        supervisor_name = Supervisor.objects.get(name = self.supervisor)
        return supervisor_name



class Manager(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Controller(models.Model):
    employee_name = models.CharField(max_length=100)
    hire_date = models.DateField()
    pto = models.IntegerField(default=120)
    manager = models.ForeignKey(Manager)
    shift = models.ForeignKey(Shift)
    employee_id = models.IntegerField(default= 9999, unique=True)

    def list_oqs(self):
        alloqs = Console_oq.objects.filter(controller = self.id)
        return alloqs
    def onshift(self):
        allshifts = Shift.objects.filter(id = self.shift)
        return allshifts
    def full_name(self):
        return self.employee_name


    def __str__(self):
        return self.employee_name


class Console(models.Model):
    console_name = models.CharField(max_length=100)
    manager = models.ForeignKey(Manager)

    def __str__(self):
        return self.console_name
    def deskname(self):
        return "%s"%(self.console_name)

class Console_oq(models.Model):
    controller = models.ForeignKey(Controller, on_delete=models.CASCADE)
    oq_date = models.DateField()
    console = models.ForeignKey(Console)
    primary_console = models.BooleanField(default=True)

    def readable(self):
        controller = Controller.objects.get(employee_name = self.controller)
        console_name = Console.objects.get(console_name=self.console)
        return "%s %s %s" % (controller, console_name, self.oq_date)



    def __str__(self):
        console_name = Console.objects.get(console_name = self.console)
        controller_name = Controller.objects.get(employee_name = self.controller)
        return "%s %s %s"%(controller_name, console_name, self.oq_date)

class Contoller_shift(models.Model):
    employee = models.ForeignKey(Controller)
    workdate = models.DateField()
    console = models.ForeignKey(Console)
    holiday = models.BooleanField(default=False)
    rover = models.BooleanField(default=False)
    meeting = models.BooleanField(default=False)


    def __str__(self):
        employee_name = Controller.objects.get(employee_name = self.employee)
        console_name = Console.objects.get(console_name = self.console)

        return "%s  - %s - %s"%(self.workdate, employee_name, console_name)



class Console_schedule(models.Model):
    deskname = models.ForeignKey(Console)
    is_day = models.BooleanField()
    shift = models.ForeignKey(Shift, null=True)
    controller = models.ForeignKey(Controller, null=True)
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
    shift = models.ForeignKey(Shift)
    date = models.DateField()
    is_day = models.BooleanField()

    def __str__(self):
        return "%s %s"%(Shift.objects.get(shift_id = self.shift), self.date)


from .signals import initialize_desk_schedule
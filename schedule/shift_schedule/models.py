from django.db import models


class Supervisor(models.Model):
    name = models.CharField(max_length=120)
    email = models.CharField(max_length=120)

    def __str__(self):
        return self.name




class Shift(models.Model):
    shift_id = models.CharField(max_length=20)
    supervisor = models.ForeignKey(Supervisor)

    def __str__(self):
        return self.shift_id


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

    def __str__(self):
        return self.employee_name


class Console(models.Model):
    console_name = models.CharField(max_length=100)
    manager = models.ForeignKey(Manager)

    def __str__(self):
        return self.console_name

class Console_oq(models.Model):
    controller = models.ForeignKey(Controller, on_delete=models.CASCADE)
    oq_date = models.DateField()
    console = models.ForeignKey(Console)

    def __str__(self):
        console_name = Console.objects.get(console_name = self.console)
        controller_name = Controller.objects.get(employee_name = self.controller)
        return "%s %s %s"%(controller_name, console_name, self.oq_date)




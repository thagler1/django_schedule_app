from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Console, Manager, Console_schedule, Master_schedule, Shift, Controller, Console_oq
import datetime

@receiver(post_save, sender=Console_oq)
def initialize_desk_schedule(sender, instance, created, **kwargs):
    #/todo enforce one primary controller per shift
    if instance.primary_console ==True:
        controller = instance.controller
        shift = controller.shift
        start_date = instance.oq_date
        date_range = Master_schedule.objects.filter(date__gte = start_date, shift = shift )
        for date in date_range:
            if date.shift == shift:
                Console_schedule.objects.update_or_create(deskname = instance.console,
                                                   is_day = date.is_day,
                                                   shift = shift,
                                                   controller = controller,
                                                   date = date.date)

#Build Master Schedule
def addshift (sequence, instance, start_date):
    for i, shift in enumerate(sequence):
        date = (start_date + datetime.timedelta(days=i)).strftime('%Y-%m-%d')
        if shift == "Day":
            Master_schedule.objects.update_or_create(shift = instance, date = date, is_day = True)
        elif shift == "Night":
            Master_schedule.objects.update_or_create(shift=instance, date=date, is_day=False)
        else:
            pass


@receiver(post_save, sender = Shift)
def assign_shift_to_Console_schedule(sender, instance, created, **kwargs):
    n = "Night"
    d = "Day"
    o = "off"
    dupont = [n, n, n, n, o, o, o, d, d, d, o, n, n, n, o, o, o, d, d, d, d, o, o, o, o, o, o, o]

    sequence = []
    full_sequence = []
    start_date = datetime.date(2017, 1, 1)
    end_date = datetime.date(2017,12,31)
    span = (end_date - start_date)
    timeframe = span.days


    zeroday = instance.zero_day

    for shift in dupont[zeroday - 1:]:
        sequence.append(shift)
    for shift in dupont[:zeroday - 1]:
        sequence.append(shift)
    while len(full_sequence) <timeframe:
        for shift in sequence:
            full_sequence.append(shift)

    addshift(full_sequence[:timeframe], instance, start_date)

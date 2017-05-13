from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Console, Manager, Console_schedule, Master_schedule, Shift, UserProfile, Console_oq, PTO_table
import datetime
from .schedule_calculations import check_date
'''
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
'''

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



@receiver(post_save, sender = User)
def create_new_user_profife(sender, instance, created, **kwargs):
    '''
    creates a UserProfile when a new user is added. Extends Djangos standard user class
    '''
    user = instance
    if created:
        user_profile = UserProfile(user = user)
        user_profile.save()

@receiver(post_save, sender = PTO_table)
def add_pto_to_schedule(sender, instance, created, **kwargs):
    '''

    once pto has been approved by supervisor remove controller from scheduled shift
    '''
    pto_event = instance
    pto_taker = UserProfile.objects.get(id=pto_event.user.id)
    if pto_event.type != 'DND':
        if created:
            pto_taker.pto -=12
            pto_taker.save()

    elif PTO_table.objects.filter(user = pto_taker, date_pto_taken= instance.date_pto_taken).count()>1:
        print(pto_taker)
        print(pto_event)

        pto_event.delete()


@receiver(pre_delete, sender= PTO_table)
def recredit_pto(sender, instance, **kwargs):
    pto_event = instance
    if pto_event.type != 'DND':
        pto_taker = UserProfile.objects.get(id = pto_event.user.id)
        pto_taker.pto +=12
        pto_taker.save()
    else:
        pass
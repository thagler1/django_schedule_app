from ..models import Shift, UserProfile, Console, Master_schedule, Console_Map, Console_oq, PTO_table, Schedule_Record
import datetime
from ..functions import serialize_instance
from ..schedule_calculations import project_schedule
from django.contrib.auth import login, authenticate
from django.shortcuts import render

def user_pto_requests(userProfile, start=None, end=None):
    '''
    :param UserProfile: 
    :param Start: pull on or before this date
    :param End: End query on this date, if not supplied Todays date will be uses
    :return: {'userprofile':[pto_events**events are stored as dictionaries**, ...]}
    '''
    if start:
        if not end:
            end = datetime.datetime.today()
        else:
            pass
        pto_events = PTO_table.objects.filter(date_pto_taken__range = [start, end],user=userProfile, )
    else:
        pto_events = PTO_table.objects.filter(user=userProfile)

    rdict =  {'report':[serialize_instance(pto_event) for pto_event in pto_events]}

    for event in rdict['report']:
        id = event['coverage_id']
        if UserProfile.objects.filter(id=id).exists():
            event['coverage_id'] = UserProfile.objects.get(id=id).full_name()
    return rdict

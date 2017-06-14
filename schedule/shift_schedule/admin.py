from django.contrib import admin
from .models import UserProfile, Supervisor, Manager, Console, Shift, Console_oq, Console_schedule, Master_schedule, PTO_table, Console_Map, Schedule_Record, CommsLog,OT_offer

admin.site.register(Schedule_Record)
admin.site.register(Master_schedule)
admin.site.register(UserProfile)
admin.site.register(Console)
admin.site.register(Shift)
admin.site.register(Console_oq)
admin.site.register(PTO_table)
admin.site.register(Console_Map)
admin.site.register(CommsLog)
admin.site.register(OT_offer)

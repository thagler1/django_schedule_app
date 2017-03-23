from django.contrib import admin
from .models import UserProfile, Supervisor, Manager, Console, Shift, Console_oq, Console_schedule, Master_schedule, PTO_table

admin.site.register(Console_schedule)
admin.site.register(Master_schedule)
admin.site.register(UserProfile)
admin.site.register(Supervisor)
admin.site.register(Manager)
admin.site.register(Console)
admin.site.register(Shift)
admin.site.register(Console_oq)
admin.site.register(PTO_table)

from django.contrib import admin
from .models import Controller, Supervisor, Manager, Console, Shift, Console_oq, Console_schedule, Master_schedule

admin.site.register(Console_schedule)
admin.site.register(Master_schedule)
admin.site.register(Controller)
admin.site.register(Supervisor)
admin.site.register(Manager)
admin.site.register(Console)
admin.site.register(Shift)
admin.site.register(Console_oq)

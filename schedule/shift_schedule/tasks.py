from schedule.shift_schedule.models import UserProfile
from django.contrib.auth.models import User #used fro user profiles

@app.task(ignore_result=True)
def addpto():
    user = User.objects.get(first_name = 'Todd')
    up = UserProfile.objects.get(id = user.id)

    up.pto +=10
    up.save()

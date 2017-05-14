from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms
from .models import PTO_table, UserProfile
from django.contrib.admin import widgets
from .schedule_calculations import project_schedule


class DateInput(forms.DateInput):
    input_type = 'date'

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']
        widgets = {
            'password':forms.PasswordInput(attrs={'placeholder': ''}),
        }

class PTOForm(ModelForm):
    class Meta:
        model = PTO_table
        fields =  ['date_pto_taken', 'type', 'notes']

    def clean_type(self, userprofile):
        # test the rate limit by passing in the cached user object
        scheduled = False
        #Check to see if controller is scheduled that day
        print(self.cleaned_data)
        schedule = project_schedule(self.cleaned_data['date_pto_taken']
            ,self.cleaned_data['date_pto_taken'],userprofile)
        print(schedule)
        if schedule:
            scheduled = True

        if scheduled == True:
            #Check if DND is set for scheduled day, if it is reject the form
            if self.cleaned_data['type'] == 'DND':
                raise forms.ValidationError("You cannot mark a day you are scheduled to work with Do No Disturb.")

        return self.cleaned_data

class UserprofileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['hire_date','pto', 'manager', 'shift', 'phone', 'profile_image']
        widgets = {
            'hire_date':forms.DateInput(attrs={'class':'datepicker'}),
        }
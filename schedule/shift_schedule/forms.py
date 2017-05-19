from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms
from .models import PTO_table, UserProfile, Console, Console_oq
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


    def __init__(self, *args, **kwargs):
        self.userprofile = kwargs.pop('userprofile', None)
        super(PTOForm, self).__init__(*args, **kwargs)



    def clean_type(self):
        # test the rate limit by passing in the cached user object
        scheduled = False
        #Check to see if controller is scheduled that day

        schedule = project_schedule(self.cleaned_data['date_pto_taken']
            ,self.cleaned_data['date_pto_taken'],self.userprofile)

        if schedule:
            scheduled = True

        if scheduled is True:
            #Check if DND is set for scheduled day, if it is reject the form
            if self.cleaned_data['type'] == 'DND':
                raise forms.ValidationError("You cannot mark a day you are scheduled to work with Do No Disturb.")

            #check to see if it is short notice pto

            #if on PTO already, reject
            if PTO_table.objects.filter(user = self.userprofile, date_pto_taken = self.cleaned_data['date_pto_taken']).exists():
                raise forms.ValidationError("You are already on PTO")

        if scheduled is False:
            # reject pto taken on days not scheduled
            if self.cleaned_data['type'] == 'PTO' or self.cleaned_data['type'] == 'PTOS':
                raise forms.ValidationError("You cannot take %(value)s on a day you are not scheduled",
                                            params={'value': self.cleaned_data['type']},)
        return self.cleaned_data['type']

class UserprofileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['hire_date','pto', 'manager', 'shift', 'phone', 'profile_image']
        widgets = {
            'hire_date':forms.DateInput(attrs={'class':'datepicker'}),
        }

class ConsoleForm(ModelForm):
    class Meta:
        model = Console
        fields = ['console_name', 'manager']

def oq_controllers(console):
    return Console_oq.objects.filter(console=console).only('controller')

class schedule_pto(ModelForm):
    class Meta:
        model = PTO_table
        fields = ['supervisor_approval', 'notes', 'type', 'coverage', 'console']


    def __init__(self, *args, **kwargs):
        #console = kwargs.pop('instance')
        console = kwargs['instance'].console
        super(schedule_pto, self).__init__(*args, **kwargs)
        self.fields['coverage'].queryset = oq_controllers(console)




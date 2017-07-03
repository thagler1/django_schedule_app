from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms
from .models import PTO_table, UserProfile, Console, Console_oq, Cancelled_PTO, Shift
from django.contrib.admin import widgets
from .schedule_calculations import project_schedule
import datetime
from django.contrib.auth.models import User



class DateInput(forms.DateInput):
    input_type = 'datepicker'

class UserForm(forms.Form):
    managers = UserProfile.objects.filter(is_manager= True)
    manager_choices  = [(profile.id,profile.full_name()) for profile in managers ]

    shifts = Shift.objects.all()
    shift_choices = [(shift.id, shift.shift_id) for shift in shifts]

    username = forms.CharField(label="Username",widget=forms.TextInput(attrs={'placeholder':"Enter Username", 'class':'form-control'}))
    first_name =forms.CharField(label="First Name",widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(label="Last Name",widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    manager = forms.ChoiceField(label="Manager", choices=manager_choices )
    shift = forms.ChoiceField(label="Select Shift", choices=shift_choices)
    hire_date = forms.DateField(label="Date Hired")
    email = forms.EmailField(label="Last Name",widget=forms.TextInput(attrs={'placeholder': 'email@gmail.com'}))
    phone = forms.CharField(label="Phone Number")
    def clean_username(self):
        if User.objects.filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError("%s is unavailable"%(self.cleaned_data['username']))
        return self.cleaned_data['username']

    def clean_hire_date(self):
        if self.cleaned_data['hire_date'] > datetime.date.today():
            raise forms.ValidationError('Hire date can not be in the future')
        return self.cleaned_data['hire_date']

    def clean_manager(self):
        return UserProfile.objects.get(id=self.cleaned_data['manager'])

    def clean_shift(self):
        return Shift.objects.get(id=self.cleaned_data['shift'])


class PTOForm(ModelForm):
    class Meta:
        model = PTO_table
        fields =  ['date_pto_taken', 'type', 'notes']


    def __init__(self, *args, **kwargs):
        self.userprofile = kwargs.pop('userprofile', None)
        super(PTOForm, self).__init__(*args, **kwargs)



    def clean_type(self):

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

            #see if controller has enough PTO
            

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
        fields = ['pto', 'manager', 'shift', 'phone', 'profile_image']


class ConsoleForm(ModelForm):
    class Meta:
        model = Console
        fields = ['console_name', 'manager']

def oq_controllers(console):
    return UserProfile.objects.filter(console_oq__console = console)


class schedule_pto(ModelForm):
    class Meta:
        model = PTO_table
        fields = ['notes', 'type', 'coverage','supervisor_approval']


    def __init__(self, *args, **kwargs):
        #console = kwargs.pop('instance')
        console = kwargs['instance'].console
        super(schedule_pto, self).__init__(*args, **kwargs)
        self.fields['coverage'].queryset = oq_controllers(console)

class user_pto_form(forms.Form): #Note that it is not inheriting from forms.ModelForm
    startdate = forms.DateTimeField(label='Start Date')
    enddate = forms.DateTimeField(label='End Date')

class Cancel_PTO_controller(ModelForm):
    class Meta:
        model = Cancelled_PTO
        fields = ['pto_event', 'notes']

    def __init__(self, *args, **kwargs):
        #console = kwargs.pop('instance')
        userprofile = kwargs['instance']

        super(Cancel_PTO_controller, self).__init__(*args, **kwargs)
        self.fields['pto_event'].queryset = PTO_table.objects.filter(user=userprofile, date_pto_taken__gt=datetime.datetime.today())
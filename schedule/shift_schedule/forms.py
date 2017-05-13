from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms
from .models import PTO_table, UserProfile

class DateInput(forms.DateInput):
    input_type = 'date'

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

class PTOForm(ModelForm):
    class Meta:
        model = PTO_table
        fields =  ['date_pto_taken', 'type', 'notes']

class UserprofileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['hire_date','pto', 'manager', 'shift', 'phone', 'profile_image', 'is_supervisor', 'is_manager']
        widgets = {
            'hire_date': DateInput(),
        }
from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms
from .models import PTO_table


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')

class PTOForm(ModelForm):
    class Meta:
        model = PTO_table
        fields = ['date_requested', 'date_pto_taken','user', 'type', 'notes', 'console_date']

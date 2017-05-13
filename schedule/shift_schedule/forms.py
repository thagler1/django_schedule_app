from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms
from .models import PTO_table, UserProfile
from django.contrib.admin import widgets


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
        exclude = ()
        #fields = ['hire_date','pto', 'manager', 'shift', 'phone', 'profile_image', 'is_supervisor', 'is_manager', 'user']
        widgets = {
            'hire_date':forms.DateInput(attrs={'class':'datepicker'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserprofileForm, self).__init__(*args, **kwargs)
        self.fields['user'].required = False
        data = kwargs.get('data')
        # 'prefix' parameter required if in a modelFormset
        self.user_form = UserForm(instance=self.instance and self.instance.user,
                                    prefix=self.prefix, data=data)

    def clean(self):
        if not self.user_form.is_valid():
            raise forms.ValidationError("User not valid")

    def save(self, commit=True):
        obj = super(UserprofileForm, self).save(commit=commit)
        obj.user = self.user_form.save()
        obj.save()
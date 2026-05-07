from django import forms
from .models import *

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'phone_number', 'location', 'emergency_contact_name', 'emergency_contact_phone']

class IncidentReportForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['description', 'latitude', 'longitude']
        widgets = {
            'description': forms.Textarea(attrs={'class':'form-control'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

from django import forms
from django.contrib.auth.models import User
from .models import Responder

class ResponderCreateForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    username = forms.CharField(max_length=100)

    department = forms.ModelChoiceField(queryset=None)
    phone_number = forms.CharField(max_length=20)

    def __init__(self, *args, **kwargs):
        departments = kwargs.pop('departments', None)
        super().__init__(*args, **kwargs)

        if departments:
            self.fields['department'].queryset = departments
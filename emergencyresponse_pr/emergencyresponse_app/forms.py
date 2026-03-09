from django import forms
from .models import *

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'phone_number', 'location', 'emergency_contact_name', 'emergency_contact_phone']

class IncidentReportForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['description', 'location_name', 'location_description', 'latitude', 'longitude']
        widgets = {
            'description': forms.Textarea(attrs={'class':'form-control'}),
            'location_name': forms.Select(attrs={'class':'form-select'}),
            'location_description': forms.TextInput(attrs={'class':'form-control'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
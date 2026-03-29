from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML, Submit

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email Address")
    phone_number = forms.CharField(required=True, max_length=20, label="Mobile Number")
    
    # Optional fields
    full_name = forms.CharField(required=False, max_length=255, label="Full Name")
    emergency_contact_name = forms.CharField(required=False, max_length=255, label="Contact Name")
    emergency_contact_phone = forms.CharField(required=False, max_length=20, label="Contact Phone")

    class Meta:
        model = User
        fields = ('email', 'username', 'phone_number', 'emergency_contact_name', 'emergency_contact_phone')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Clean up Help Text
        self.fields['username'].help_text = ""
        self.fields['password1'].help_text = ""
        self.fields['password2'].help_text = ""

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        # We keep form_tag = True here so Crispy generates the <form> tags for us
        self.helper.form_tag = True 
        
        self.helper.layout = Layout(
            HTML('<h5 class="section-title">Account Security</h5>'),
            'email',
            Row(
                Column('password1', css_class='form-group col-md-6 mb-3'),
                Column('password2', css_class='form-group col-md-6 mb-3'),
            ),
            
            HTML('<h5 class="section-title mt-4">Identity & Contact</h5>'),
            Row(
                Column('username', css_class='form-group col-md-6 mb-3'),
                Column('phone_number', css_class='form-group col-md-6 mb-3'),
            ),

            HTML('<h5 class="section-title mt-4">Emergency Contact (Optional)</h5>'),
            HTML('''
                <div class="alert alert-light border small mb-3 text-muted">
                    Adding these now ensures faster response times during an incident.
                </div>
            '''),
            Row(
                Column('emergency_contact_name', css_class='form-group col-md-6 mb-3'),
                Column('emergency_contact_phone', css_class='form-group col-md-6 mb-3'),
            ),

            # THE MISSING PIECE: The Submit Button added via the Helper
            Submit('submit', 'PROTECT MY ACCOUNT', css_class='btn btn-primary-custom w-100 mt-4 fw-bold shadow-sm')
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile = user.profile
            profile.phone_number = self.cleaned_data.get('phone_number', '')
            profile.emergency_contact_name = self.cleaned_data.get('emergency_contact_name', '')
            profile.emergency_contact_phone = self.cleaned_data.get('emergency_contact_phone', '')
            profile.save()
        return user
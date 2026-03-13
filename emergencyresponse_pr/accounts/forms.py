from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

# accounts/forms.py


from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

# accounts/forms.py


class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=255)
    phone_number = forms.CharField(max_length=20)
    email = forms.EmailField(required=True)
    emergency_contact_name = forms.CharField(max_length=255)
    emergency_contact_phone = forms.CharField(max_length=20)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password1',
            'password2',
            'full_name',
            'phone_number', 
            'emergency_contact_name',
            'emergency_contact_phone',
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

            # Profile was created by signal
            profile = user.profile
            profile.full_name = self.cleaned_data['full_name']
            profile.phone_number = self.cleaned_data['phone_number']
            profile.emergency_contact_name = self.cleaned_data['emergency_contact_name']
            profile.emergency_contact_phone = self.cleaned_data['emergency_contact_phone']
            profile.save()

        return user
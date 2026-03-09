from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, Tudor_AREA_CHOICES
from django.contrib.auth.models import *


# Create your views here.

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        
        ''' Handling GET request ==> If the request method is not POST, it creates an empty instance of the registration form. This typically happens when the user first visits the registration page. '''
    # If it's not a POST request (meaning the user just opened the page), it creates a new, empty registration form.    
    else:
        form = CustomUserCreationForm()

    
    return render(request, 'templates/register.html', {
    'form': form,
    'locations': Tudor_AREA_CHOICES,
})


def logout_view(request):
    """Log the user out and redirect home (allows GET requests)."""
    logout(request)
    return redirect('home')

def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        
    else:
        form = AuthenticationForm()
    
    return render(request, 'templates/login.html', {'form': form})



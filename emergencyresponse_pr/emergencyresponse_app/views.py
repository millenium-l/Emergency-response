from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.db.models import Q
import json
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import datetime
from .forms import *

from .models import (
    Department, Profile, Responder, EmergencyUser, Incident, 
    IncidentResponse, PRIORITY_CHOICES, CHUDA_AREA_CHOICES
)
from django.contrib.auth.decorators import login_required

def home(request):
    """Home page with emergency map and incident list"""

    departments = Department.objects.all()

    if request.user.is_authenticated:

        # SUPERUSER → see everything
        if request.user.is_superuser:
            incidents = Incident.objects.filter(
                status__in=['pending', 'assigned', 'in_progress']
            ).order_by('-created_at')[:10]

        # RESPONDER → see department incidents
        elif hasattr(request.user, "responder"):
            responder = request.user.responder

            incidents = Incident.objects.filter(
                department=responder.department,
                status__in=['pending', 'assigned', 'in_progress']
            ).order_by('-created_at')[:10]

        else:
            incidents = Incident.objects.none()

    else:
        incidents = Incident.objects.filter(
            status__in=['pending', 'assigned', 'in_progress']
        ).order_by('-created_at')[:10]

    context = {
        'incidents': incidents,
        'departments': departments,
        'mombasa_lat': -4.0435,
        'mombasa_lng': 39.6682,
        'map_zoom': 14,
    }

    return render(request, 'templates/home.html', context)

@login_required
def profile(request):
    profile = request.user.profile
    context = {
        'title': profile,
        'profile': profile, }
    return render(request, 'templates/profile.html', context)

@login_required
def profile_edit(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
        return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'templates/profile_edit.html', {'form': form})



def report_incident(request, department):

    department_obj = Department.objects.get(name=department)

    if request.method == "POST":
        form = IncidentReportForm(request.POST)

        if form.is_valid():
            incident = form.save(commit=False)
            incident.user = request.user.profile
            incident.department = department_obj

            incident.title = f"{department_obj.get_name_display()} Emergency"

            incident.priority = "high" 
            incident.save()
            return redirect("incidents_list")

    else:
        form = IncidentReportForm()

    return render(request, "templates/report_incident.html", {
        "department": department_obj,
        "form": form
    })


def my_incidents(request):
    profile = request.user.profile  # get the current logged-in user profile
    incidents = Incident.objects.filter(user=profile).order_by('-created_at')

    return render(request, "templates/incidents_list.html", {
        "incidents": incidents
    })

#role based views for staff to see all incidents and manage them
@staff_member_required
def all_incidents(request):

    # 🔍 Get shared filters first
    search = request.GET.get('search', '')
    status = request.GET.get('status')  # optional if you want later

    # SUPERUSER → full access
    if request.user.is_superuser:
        incidents = Incident.objects.select_related(
            'user', 'department', 'assigned_responder'
        ).order_by('-created_at')

        departments = Department.objects.all()

        # 🏢 Department filter
        department_id = request.GET.get('department')
        if department_id:
            incidents = incidents.filter(department_id=department_id)


    # STAFF → restricted access
    else:
        responder = request.user.responder

        incidents = Incident.objects.select_related(
            'user', 'department', 'assigned_responder'
        ).filter(
            department=responder.department
        ).order_by('-created_at')

        departments = None

        # 📊 Status filter (optional for superuser)
        if status:
            incidents = incidents.filter(status=status)

    # 🔍 SEARCH (applies to BOTH)
    if search:
        incidents = incidents.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(user__user__first_name__icontains=search) |
            Q(user__user__last_name__icontains=search) |
            Q(department__name__icontains=search)
        )

    return render(request, "templates/allincidents.html", {
        "incidents": incidents,
        "departments": departments
    })

@staff_member_required
def resolve_incident(request, incident_id):

    incident = get_object_or_404(Incident, id=incident_id)

    incident.status = "resolved"
    incident.resolved_at = timezone.now()

    incident.save()

    return redirect("incident_detail", incident_id=incident.id)





@login_required
def incident_detail(request, incident_id):
    """View incident details and map"""
    incident = get_object_or_404(Incident, id=incident_id)
    responses = incident.responses.all()
    
    context = {
        'incident': incident,
        'responses': responses,
        'can_edit': incident.user.user == request.user,
    }
    return render(request, 'templates/incident_detail.html', context)


@login_required
def incidents_list(request):
    """List all incidents for current user"""
    try:
        emergency_user = EmergencyUser.objects.get(user=request.user)
        incidents = Incident.objects.filter(user=emergency_user).order_by('-created_at')
    except EmergencyUser.DoesNotExist:
        incidents = []
    
    context = {'incidents': incidents}
    return render(request, 'templates/incidents_list.html', context)



def start_incident(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)

    incident.status = "in_progress"
    incident.save()

    return redirect("incident_detail", incident_id=incident_id)


def cancel_incident(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)

    incident.status = "cancelled"
    incident.save()

    return redirect("incident_detail", incident_id=incident_id)



















@login_required
def responders_map(request):
    """Map view of available responders"""
    responders = Responder.objects.filter(is_available=True)
    departments = Department.objects.all()
    
    context = {
        'responders': responders,
        'departments': departments,
        'mombasa_lat': -4.0435,
        'mombasa_lng': 39.6682,
        'map_zoom': 14,
    }
    return render(request, 'templates/responders_map.html', context)


# API endpoints for AJAX requests
@require_http_methods(["GET"])
def api_get_incidents(request):
    """Get all active incidents as JSON for map"""
    incidents = Incident.objects.filter(
        status__in=['pending', 'assigned', 'in_progress']
    ).values(
        'id', 'title', 'latitude', 'longitude', 
        'priority', 'status', 'created_at'
    )
    return JsonResponse(list(incidents), safe=False)


@require_http_methods(["GET"])
def api_get_departments(request):
    """Get all departments as JSON for map"""
    departments = Department.objects.values(
        'id', 'name', 'latitude', 'longitude', 
        'location_name', 'phone_number'
    )
    return JsonResponse(list(departments), safe=False)


@require_http_methods(["GET"])
def api_get_responders(request):
    """Get available responders as JSON for map"""
    responders = Responder.objects.filter(
        is_available=True
    ).values(
        'id', 'user__first_name', 'user__last_name', 
        'latitude', 'longitude', 'department__name'
    )
    return JsonResponse(list(responders), safe=False)


@login_required
@require_http_methods(["POST"])
def api_update_responder_location(request):
    """Update responder's GPS location"""
    try:
        responder = Responder.objects.get(user=request.user)
        data = json.loads(request.body)
        responder.latitude = data.get('latitude')
        responder.longitude = data.get('longitude')
        responder.save()
        return JsonResponse({'success': True})
    except Responder.DoesNotExist:
        return JsonResponse({'error': 'Responder not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.db.models import Q
import json
from datetime import datetime


from .models import (
    Department, Profile, Responder, EmergencyUser, Incident, 
    IncidentResponse, PRIORITY_CHOICES, CHUDA_AREA_CHOICES
)



def home(request):
    """Home page with emergency map and incident list"""
    incidents = Incident.objects.filter(status__in=['pending', 'assigned', 'in_progress']).order_by('-created_at')[:10]
    departments = Department.objects.all()
    
    # Mombasa Chuda area coordinates
    context = {
        'incidents': incidents,
        'departments': departments,
        'mombasa_lat': -4.0435,
        'mombasa_lng': 39.6682,
        'map_zoom': 14,
    }
    return render(request, 'templates/home.html', context)

def profile(request):
    profile = request.user.profile
    context = {
        'title': profile,
        'profile': profile, }
    return render(request, 'templates/profile.html', context)




@login_required
def create_incident(request):
    """Create new incident/SOS request"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority', 'high')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        location_description = request.POST.get('location_description', '')
        department_id = request.POST.get('department')
        
        try:
            emergency_user = EmergencyUser.objects.get(user=request.user)
        except EmergencyUser.DoesNotExist:
            return render(request, 'create_incident.html', 
                        {'error': 'Please complete your profile first'})
        
        department = None
        if department_id:
            department = get_object_or_404(Department, id=department_id)
        
        incident = Incident.objects.create(
            user=emergency_user,
            title=title,
            description=description,
            priority=priority,
            latitude=float(latitude),
            longitude=float(longitude),
            location_description=location_description,
            department=department,
        )
        
        return redirect('templates/incident_detail', incident_id=incident.id)
    
    departments = Department.objects.all()
    context = {
        'departments': departments,
        'priorities': PRIORITY_CHOICES,
        'mombasa_lat': -4.0435,
        'mombasa_lng': 39.6682,
    }
    return render(request, 'templates/create_incident.html', context)


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

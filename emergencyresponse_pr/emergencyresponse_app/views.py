from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.db.models import Q
from django.db import transaction
import json
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import datetime
from .forms import *


from .models import (
    Department, Profile, Responder, EmergencyUser, Incident, 
    IncidentResponse, PRIORITY_CHOICES, CHUDA_AREA_CHOICES
)


# home view with role-based incident filtering and map integration
def home(request):
    departments = Department.objects.all()

    if request.user.is_authenticated:
        if request.user.is_superuser:
            incidents = Incident.objects.filter(
                status__in=['pending', 'assigned', 'in_progress']
            ).order_by('-created_at')[:10]

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

# Profile views with proper authentication and form handling
@login_required
def profile(request):
    profile = request.user.profile
    return render(request, 'templates/profile.html', {
        'title': profile,
        'profile': profile,
    })

# Profile edit view with proper authentication and form handling
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


# Incident reporting view with proper authentication, form handling, and atomic transaction to ensure data integrity
@login_required
def report_incident(request, department):
    department_obj = Department.objects.get(name=department)

    if request.method == "POST":
        form = IncidentReportForm(request.POST)

        if form.is_valid():
            with transaction.atomic():  #  ACID
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

# My Incidents view with proper authentication and role-based filtering
@login_required
def my_incidents(request):
    profile = request.user.profile
    incidents = Incident.objects.filter(user=profile).order_by('-created_at')

    return render(request, "templates/incidents_list.html", {
        "incidents": incidents
    })

# All Incidents view with proper authentication, role-based filtering, and search functionality
@staff_member_required
def all_incidents(request):
    search = request.GET.get('search', '')
    status = request.GET.get('status')

    if request.user.is_superuser:
        incidents = Incident.objects.select_related(
            'user', 'department', 'assigned_responder'
        ).order_by('-created_at')

        departments = Department.objects.all()

        department_id = request.GET.get('department')
        if department_id:
            incidents = incidents.filter(department_id=department_id)
    else:
        responder = request.user.responder

        incidents = Incident.objects.select_related(
            'user', 'department', 'assigned_responder'
        ).filter(
            department=responder.department
        ).order_by('-created_at')

        departments = None

    if status:
        incidents = incidents.filter(status=status)

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


# Incident management views (start, cancel, resolve) with proper status checks and atomic transactions
# Responder list view with role-based filtering, search, and status filters

@staff_member_required
def responders_list(request):

    #  SUPERUSER → sees everything
    if request.user.is_superuser:
        responders = Responder.objects.select_related('user', 'department')

    #  DEPARTMENT ADMIN → filter by department
    else:
        #  You MUST decide how admin is linked to department
        # Using responder relation (same pattern as your incidents view)
        if hasattr(request.user, "responder"):
            responders = Responder.objects.select_related('user', 'department').filter(
                department=request.user.responder.department
            )
        else:
            responders = Responder.objects.none()

    # Filters (apply AFTER role filtering)
    status_filter = request.GET.get('status')
    if status_filter:
        responders = responders.filter(status=status_filter)

    search = request.GET.get('search')
    if search:
        responders = responders.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(department__name__icontains=search)
        )

    stats = {
        "total": responders.count(),
        "available": responders.filter(status='available').count(),
        "busy": responders.filter(status='busy').count(),
        "offline": responders.filter(status='offline').count(),
    }

    return render(request, "templates/responders_list.html", {
        "responders": responders,
        "stats": stats
    })


# API view to update responder status with proper authentication, validation, and error handling
@login_required
@require_http_methods(["POST"])
def update_responder_status(request, responder_id):
    responder = get_object_or_404(Responder, id=responder_id)

    new_status = request.POST.get("status")
    if new_status in ['available', 'busy', 'offline']:
        responder.status = new_status
        responder.save()

    return redirect('responders_list')

# API view to assign responder to incident with proper status checks and atomic transaction
@login_required
@transaction.atomic
def assign_responder(request, responder_id, incident_id):
    responder = get_object_or_404(Responder, id=responder_id)
    incident = get_object_or_404(Incident, id=incident_id)

    if responder.status == "available":
        responder.status = "busy"
        responder.save()

        incident.assigned_responder = responder
        incident.status = "assigned"
        incident.save()

        IncidentResponse.objects.create(
            incident=incident,
            responder=responder,
            status="assigned"
        )

    return redirect("responders_list")


@staff_member_required
@transaction.atomic
def resolve_incident(request, incident_id):
    incident = Incident.objects.select_for_update().get(id=incident_id)

    if incident.status != "resolved":
        incident.status = "resolved"
        incident.resolved_at = timezone.now()
        incident.save()

    return redirect("incident_detail", incident_id=incident.id)


@login_required
def incident_detail(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)
    responses = incident.responses.all()


    available_responders = Responder.objects.filter(
        status='available',
        department=incident.department
    )


    context = {
        'incident': incident,
        'responses': responses,
        'available_responders': available_responders,
        'can_edit': incident.user.user == request.user,
    }
    return render(request, 'templates/incident_detail.html', context)


from django.contrib.auth.hashers import make_password

@staff_member_required
def create_responder(request):
    departments = Department.objects.all()

    if request.method == "POST":
        form = ResponderCreateForm(request.POST, departments=departments)

        if form.is_valid():
            # Create User
            user = User.objects.create(
                username=form.cleaned_data['username'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )

            # Create Responder
            Responder.objects.create(
                user=user,
                department=form.cleaned_data['department'],
                phone_number=form.cleaned_data['phone_number'],
                status='offline'  # default safer
            )

            return redirect("responders_list")

    else:
        form = ResponderCreateForm(departments=departments)

    return render(request, "templates/create_responder.html", {
        "form": form
    })

@staff_member_required
@transaction.atomic
def assign_responder_to_incident(request, incident_id):
    incident = get_object_or_404(Incident.objects.select_for_update(), id=incident_id)

    if request.method == "POST":
        responder_id = request.POST.get("responder_id")
        responder = get_object_or_404(Responder.objects.select_for_update(), id=responder_id)

        # Only assign if available
        if responder.status != "available":
            return redirect("incident_detail", incident_id=incident.id)

        #  Assign
        incident.assigned_responder = responder
        incident.status = "assigned"
        incident.save()

        #  Update responder
        responder.status = "busy"
        responder.save()

        #  Track response
        IncidentResponse.objects.create(
            incident=incident,
            responder=responder,
            status="assigned"
        )

    return redirect("incident_detail", incident_id=incident.id)



@login_required
def incidents_list(request):
    try:
        emergency_user = EmergencyUser.objects.get(user=request.user)
        incidents = Incident.objects.filter(user=emergency_user).order_by('-created_at')
    except EmergencyUser.DoesNotExist:
        incidents = []

    return render(request, 'templates/incidents_list.html', {'incidents': incidents})


@login_required
@transaction.atomic
def start_incident(request, incident_id):
    incident = Incident.objects.select_for_update().get(id=incident_id)

    if incident.status == "assigned":
        incident.status = "in_progress"
        incident.save()

    return redirect("incident_detail", incident_id=incident_id)


@login_required
@transaction.atomic
def cancel_incident(request, incident_id):
    incident = Incident.objects.select_for_update().get(id=incident_id)

    if incident.status not in ["resolved", "cancelled"]:
        incident.status = "cancelled"
        incident.save()

    return redirect("incident_detail", incident_id=incident_id)


@login_required
def responders_map(request):
    responders = Responder.objects.filter(status='available').select_related('department')
    departments = Department.objects.all()

    context = {
        'responders': responders,
        'departments': departments,
        'mombasa_lat': -4.0435,
        'mombasa_lng': 39.6682,
        'map_zoom': 14,
    }
    return render(request, 'templates/responders_map.html', context)


@require_http_methods(["GET"])
def api_get_incidents(request):
    incidents = Incident.objects.filter(
        status__in=['pending', 'assigned', 'in_progress']
    ).values(
        'id', 'title', 'latitude', 'longitude',
        'priority', 'status', 'created_at'
    )
    return JsonResponse(list(incidents), safe=False)


@require_http_methods(["GET"])
def api_get_departments(request):
    departments = Department.objects.values(
        'id', 'name', 'latitude', 'longitude',
        'location_name', 'phone_number'
    )
    return JsonResponse(list(departments), safe=False)


@require_http_methods(["GET"])
def api_get_responders(request):
    responders = Responder.objects.filter(
        status='available'
    ).values(
        'id', 'user__first_name', 'user__last_name',
        'latitude', 'longitude', 'department__name'
    )
    return JsonResponse(list(responders), safe=False)


@login_required
@require_http_methods(["POST"])
@transaction.atomic
def api_update_responder_location(request):
    try:
        responder = Responder.objects.select_for_update().get(user=request.user)
        data = json.loads(request.body)

        responder.latitude = data.get('latitude')
        responder.longitude = data.get('longitude')
        responder.save()

        return JsonResponse({'success': True})

    except Responder.DoesNotExist:
        return JsonResponse({'error': 'Responder not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Django 6+: use LogoutView instead of deprecated logout_view
    # allow GET requests so simple links work (LogoutView defaults to POST only)
    # custom view handles GET/POST
    
    # Incident management
    path('incident/report/<str:department>/', views.report_incident, name='report_incident'),
    path('incident/<int:incident_id>/', views.incident_detail, name='incident_detail'),
    path('incidents/', views.my_incidents, name='incidents_list'),
    path('all-incidents/', views.all_incidents, name='all_incidents'),
    path("incident/<int:incident_id>/resolve/",views.resolve_incident,name="resolve_incident"),

    path("incident/<int:incident_id>/start/", views.start_incident, name="start_incident"),
    path("incident/<int:incident_id>/cancel/", views.cancel_incident, name="cancel_incident"),

    # Responder views
    path('responders/', views.responders_map, name='responders_map'),
    
    # API endpoints
    path('api/incidents/', views.api_get_incidents, name='api_incidents'),
    path('api/departments/', views.api_get_departments, name='api_departments'),
    path('api/responders/', views.api_get_responders, name='api_responders'),
    path('api/responder/location/', views.api_update_responder_location, name='api_update_location'),
]

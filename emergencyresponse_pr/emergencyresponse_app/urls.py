from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    # Django 6+: use LogoutView instead of deprecated logout_view
    # allow GET requests so simple links work (LogoutView defaults to POST only)
    # custom view handles GET/POST
    path('logout/', views.logout_view, name='logout'),
    
    # Incident management
    path('incident/create/', views.create_incident, name='create_incident'),
    path('incident/<int:incident_id>/', views.incident_detail, name='incident_detail'),
    path('incidents/', views.incidents_list, name='incidents_list'),
    
    # Responder views
    path('responders/', views.responders_map, name='responders_map'),
    
    # API endpoints
    path('api/incidents/', views.api_get_incidents, name='api_incidents'),
    path('api/departments/', views.api_get_departments, name='api_departments'),
    path('api/responders/', views.api_get_responders, name='api_responders'),
    path('api/responder/location/', views.api_update_responder_location, name='api_update_location'),
]

from django.db import models
from django.contrib.auth.models import User

# Department types for emergency services
DEPARTMENT_CHOICES = [
    ('fire', 'Fire Department'),
    ('medical', 'Medical/Ambulance'),
    ('police', 'Police Department'),
]

# Incident status choices
INCIDENT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('assigned', 'Assigned'),
    ('in_progress', 'In Progress'),
    ('resolved', 'Resolved'),
    ('cancelled', 'Cancelled'),
]

# Priority levels
PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('critical', 'Critical'),
]

# Neighborhoods / areas within Mombasa Chuda to use in registration dropdown
CHUDA_AREA_CHOICES = [
    ('Tudor', 'Tudor'),
    ('Tudor_centre', 'Tudor Centre'),
    ('Tudor_estate', 'Tudor Estate'),
    ('kizingo', 'Kizingo'),
    ('miritini', 'Miritini'),
    ('tononoka', 'Tononoka'),
    ('kipevu', 'Kipevu'),
    ('ganjoni', 'Ganjoni'),
    ('magongo', 'Magongo'),
]


class Profile(models.Model):
    """Extended user profile for emergency users and responders"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    location = models.CharField(max_length=100, choices=CHUDA_AREA_CHOICES, default=CHUDA_AREA_CHOICES[0][0])
    emergency_contact_name = models.CharField(max_length=255)
    emergency_contact_phone = models.CharField(max_length=20)
    
    def __str__(self):
        return self.full_name

class Department(models.Model):
    """Emergency Response Departments"""
    name = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)
    description = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20)
    latitude = models.FloatField(default=-4.0435, null=True, blank=True)  # Mombasa Chuda area
    longitude = models.FloatField(default=39.6682, null=True, blank=True)  # Mombasa Chuda area
    location_name = models.CharField(max_length=255, choices=CHUDA_AREA_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Departments'
    
    def __str__(self):
        return f"{self.get_name_display()} - {self.location_name}"


class Responder(models.Model):
    """Emergency Response Personnel"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    phone_number = models.CharField(max_length=20)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department.get_name_display()}"


class EmergencyUser(models.Model):
    """Users who report emergencies"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    location = models.CharField(max_length=100, choices=CHUDA_AREA_CHOICES, default=CHUDA_AREA_CHOICES[0][0])
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=255)
    emergency_contact_phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.location}"


class Incident(models.Model):
    """Emergency Incidents/Requests"""
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)  # ← use Profile
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=2000)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='high')
    status = models.CharField(max_length=20, choices=INCIDENT_STATUS_CHOICES, default='pending')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_name = models.CharField(max_length=255, blank=True, choices=CHUDA_AREA_CHOICES)
    location_description = models.CharField(max_length=255, blank=True)
    assigned_responder = models.ForeignKey(Responder, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    reported_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    @property
    def priority_color(self):
        """Return a color code based on priority level."""
        return {
            'critical': '#8b0000',
            'high': '#dc3545',
            'medium': '#ff9800',
            'low': '#ffc107',
        }.get(self.priority, '#ffc107')

    @property
    def status_color(self):
        """Return a color code based on current status."""
        return {
            'pending': '#ffc107',
            'assigned': '#0dcaf0',
            'in_progress': '#0d6efd',
            'resolved': '#198754',
            'cancelled': '#dc3545',
        }.get(self.status, '#ffc107')


class IncidentResponse(models.Model):
    """Tracking response to incidents"""
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(Responder, on_delete=models.SET_NULL, null=True)
    response_time = models.DateTimeField(auto_now_add=True)
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    actual_arrival = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=INCIDENT_STATUS_CHOICES)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Response to {self.incident.title} by {self.responder}"

    @property
    def status_color(self):
        return {
            'pending': '#ffc107',
            'assigned': '#0dcaf0',
            'in_progress': '#0d6efd',
            'resolved': '#198754',
            'cancelled': '#dc3545',
        }.get(self.status, '#ffc107')

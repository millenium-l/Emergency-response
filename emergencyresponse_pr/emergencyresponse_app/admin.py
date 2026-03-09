from django.contrib import admin
from .models import Department, Responder, EmergencyUser, Incident, IncidentResponse, Profile


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('get_name_display', 'location_name', 'phone_number', 'latitude', 'longitude')
    list_filter = ('name', 'location_name')
    search_fields = ('name', 'location_name', 'phone_number')
    fieldsets = (
        ('Department Info', {'fields': ('name', 'description', 'phone_number')}),
        ('Location', {'fields': ('location_name', 'latitude', 'longitude')}),
    )


@admin.register(Responder)
class ResponderAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'get_department', 'phone_number', 'is_available', 'created_at')
    list_filter = ('is_available', 'department', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'phone_number', 'department__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User', {'fields': ('user', 'department')}),
        ('Contact', {'fields': ('phone_number',)}),
        ('Location', {'fields': ('latitude', 'longitude')}),
        ('Status', {'fields': ('is_available',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Responder'
    
    def get_department(self, obj):
        return obj.department.get_name_display() if obj.department else 'N/A'
    get_department.short_description = 'Department'


@admin.register(EmergencyUser)
class EmergencyUserAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'phone_number', 'location', 'emergency_contact_name', 'created_at')
    list_filter = ('location', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'phone_number', 'location')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Contact', {'fields': ('phone_number',)}),
        ('Location', {'fields': ('location', 'latitude', 'longitude')}),
        ('Emergency Contact', {'fields': ('emergency_contact_name', 'emergency_contact_phone')}),
        ('Timestamps', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'User'


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_priority_display', 'get_status_display', 'user', 'get_department', 'created_at')
    list_filter = ('status', 'priority', 'department', 'created_at')
    search_fields = ('title', 'description', 'user__user__first_name', 'user__user__last_name', 'location_description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Incident Info', {'fields': ('title', 'description', 'priority', 'status')}),
        ('Department & Responder', {'fields': ('department', 'assigned_responder')}),
        ('Location', {'fields': ('latitude', 'longitude', 'location_description')}),
        ('Reporter', {'fields': ('user',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'resolved_at'), 'classes': ('collapse',)}),
    )
    
    def get_department(self, obj):
        return obj.department.get_name_display() if obj.department else 'N/A'
    get_department.short_description = 'Department'


@admin.register(IncidentResponse)
class IncidentResponseAdmin(admin.ModelAdmin):
    list_display = ('get_incident_title', 'get_responder_name', 'get_status_display', 'response_time', 'actual_arrival')
    list_filter = ('status', 'response_time')
    search_fields = ('incident__title', 'responder__user__first_name', 'responder__user__last_name')
    readonly_fields = ('response_time',)
    
    fieldsets = (
        ('Incident & Responder', {'fields': ('incident', 'responder')}),
        ('Timeline', {'fields': ('response_time', 'estimated_arrival', 'actual_arrival')}),
        ('Status & Notes', {'fields': ('status', 'notes')}),
    )
    
    def get_incident_title(self, obj):
        return obj.incident.title
    get_incident_title.short_description = 'Incident'
    
    def get_responder_name(self, obj):
        return obj.responder.user.get_full_name() if obj.responder else 'N/A'
    get_responder_name.short_description = 'Responder'

admin.site.register(Profile)

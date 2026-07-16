from django.contrib import admin
from .models import Department, Responder, EmergencyUser, Incident, IncidentResponse, Profile, AssignmentRequest, Notification


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
    list_display = ('get_full_name', 'get_department', 'get_status_display', 'created_at')
    list_filter = ('status', 'profile__department', 'created_at')
    search_fields = ('profile__full_name', 'profile__department__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Profile', {'fields': ('profile',)}),
        ('Location', {'fields': ('latitude', 'longitude')}),
        ('Status', {'fields': ('status',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    def get_full_name(self, obj):
        return obj.profile.full_name if obj.profile else "Unknown"
    get_full_name.short_description = 'Responder'

    def get_department(self, obj):
        if obj.profile and obj.profile.department:
            return obj.profile.department.get_name_display()
        return "N/A"
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
    search_fields = ('incident__title', 'responder__profile__full_name',)
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
        return (
            obj.responder.profile.full_name
            if obj.responder and obj.responder.profile
            else 'N/A'
        )
    get_responder_name.short_description = 'Responder'

admin.site.register(Profile)


@admin.register(AssignmentRequest)
class AssignmentRequestAdmin(admin.ModelAdmin):
    list_display = ('get_incident_title', 'get_responder_name', 'get_status_display', 'created_at', 'responded_at')
    list_filter = ('status', 'created_at')
    search_fields = ('incident__title', 'responder__profile__full_name',)
    readonly_fields = ('created_at', 'responded_at')
    
    fieldsets = (
        ('Assignment', {'fields': ('incident', 'responder', 'dispatched_by')}),
        ('Status', {'fields': ('status',)}),
        ('Timeline', {'fields': ('created_at', 'responded_at', 'expires_at')}),
    )
    
    def get_incident_title(self, obj):
        return obj.incident.title
    get_incident_title.short_description = 'Incident'
    
    def get_responder_name(self, obj):
        return (
        obj.responder.profile.full_name
        if obj.responder and obj.responder.profile
        else 'N/A'
    )
    get_responder_name.short_description = 'Responder'
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    get_status_display.short_description = 'Status'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_responder_name', 'get_incident', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'assignment_request__responder__profile__full_name',)
    readonly_fields = ('created_at', 'updated_at', 'read_at')
    
    fieldsets = (
        ('Notification Info', {'fields': ('assignmentrequest__responder', 'assignmentrequest__incident', 'assignment_request', 'notification_type')}),
        ('Content', {'fields': ('title', 'message')}),
        ('Read Status', {'fields': ('is_read', 'read_at')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    def get_responder_name(self, obj):
        if (
        obj.assignment_request and
        obj.assignment_request.responder and
        obj.assignment_request.responder.profile
        ):
            return obj.assignment_request.responder.profile.full_name
        return "N/A"

    get_responder_name.short_description = "Responder"

    def get_incident(self, obj):
        if obj.assignment_request and obj.assignment_request.incident:
            return obj.assignment_request.incident.title
        return "N/A"

    get_incident.short_description = "Incident"

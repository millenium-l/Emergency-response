from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, AssignmentRequest, Notification

@receiver(post_save, sender=User)
def create_user_related_objects(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            )


@receiver(post_save, sender=AssignmentRequest)
def create_assignment_notification(sender, instance, created, **kwargs):
    """Create a notification when an AssignmentRequest is created"""
    if created:
        incident = instance.incident
        responder = instance.responder
        dispatcher_name = instance.dispatched_by.get_full_name() if instance.dispatched_by else "System"
        
        # Build notification message with all required details
        priority_display = incident.get_priority_display() if hasattr(incident, 'get_priority_display') else incident.priority
        location = incident.location_name or incident.location_description or "Unknown Location"
        
        message = f"""
New Emergency Assignment:

Incident: {incident.title}
Priority: {priority_display}
Location: {location}
Description: {incident.description}
Assigned by: {dispatcher_name}

Please accept or reject this assignment in your dashboard.
        """.strip()
        
        # Create notification
        Notification.objects.create(
            responder=responder,
            incident=incident,
            assignment_request=instance,
            notification_type='assignment',
            title=f"New Assignment: {incident.title}",
            message=message
        )
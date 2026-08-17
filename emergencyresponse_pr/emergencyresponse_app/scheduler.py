from django.utils import timezone
from .models import (AssignmentRequest, AdminNotification)
from apscheduler.schedulers.background import BackgroundScheduler

def expire_assignments():

    expired_requests = AssignmentRequest.objects.filter(
        status="pending",
        expires_at__lt=timezone.now()
    )

    for assignment in expired_requests:

        assignment.status = "expired"
        assignment.responded_at = timezone.now()
        assignment.save()

        AdminNotification.objects.create(
            department=assignment.incident.department,
            incident=assignment.incident,
            responder=assignment.responder,
            notification_type="expired",
            title="Assignment Expired",
            message=(
                f"{assignment.responder.full_name} "
                f"did not respond within 5 minutes."
            )
        )


def start():

    scheduler = BackgroundScheduler()

    scheduler.add_job(
        expire_assignments,
        trigger='interval',
        minutes=1
    )

    scheduler.start()
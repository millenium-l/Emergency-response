from django.shortcuts import redirect
from .models import *

# Decorator to ensure the user is a responder before accessing certain views
def responder_required(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            if request.user.profile.role != "responder":
                return redirect("custom_403")

            request.responder = request.user.profile.responder
        except (Profile.DoesNotExist, Responder.DoesNotExist):
            return redirect("custom_403")

        return view_func(request, *args, **kwargs)

    return wrapper
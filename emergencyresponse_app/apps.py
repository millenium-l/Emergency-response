from django.apps import AppConfig


class EmergencyresponseAppConfig(AppConfig):
    name = 'emergencyresponse_app'


    def ready(self):
        import emergencyresponse_app.signals
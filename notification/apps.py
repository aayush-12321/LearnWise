from django.apps import AppConfig

class NotificationConfig(AppConfig):
    # default_auto_field = 'django.db.models.BigAutoField'
    name = 'notification'

    # def ready(self):
    #     print("Notification app ready")  # Debug print statement
    #     # raise Exception("NotificationConfig ready() triggered")
    #     import notification.signals1  # Import your signals here

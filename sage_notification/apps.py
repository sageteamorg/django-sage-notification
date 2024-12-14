from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SageNotificationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sage_notification"
    verbose_name = _("Notification")

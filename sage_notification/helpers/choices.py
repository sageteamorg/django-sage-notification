from django.db import models
from django.utils.translation import gettext_lazy as _


class NotificationPriority(models.TextChoices):
    LOW = 'low', _('Low')
    MEDIUM = 'medium', _('Medium')
    HIGH = 'high', _('High')


class NotificationScope(models.TextChoices):
    GLOBAL = 'global', _('Global')
    USER = 'user', _('User-Specific')
    ADMIN = 'admin', _('Admin-Only')


class NotificationSeverity(models.TextChoices):
    SUCCESS = 'success', _('Success')
    INFO = 'info', _('Info')
    WARNING = 'warning', _('Warning')
    ERROR = 'error', _('Error')


class NotificationDeliveryMethod(models.TextChoices):
    EMAIL = 'email', _('Email')
    PUSH = 'push', _('Push Notification')
    SMS = 'sms', _('SMS')
    WEB = 'web', _('Web Notification')

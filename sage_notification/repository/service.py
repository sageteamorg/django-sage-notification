from abc import ABC, abstractmethod
from django.contrib.contenttypes.models import ContentType
from sage_notification.models import Notification


class BaseNotificationService(ABC):
    """
    Abstract Base Service for Notification creation.
    """

    def __init__(self, user=None, sender=None, entity=None, context=None):
        """
        Initialize the base service with common parameters.
        """
        self.user = user
        self.sender = sender
        self.entity = entity
        self.context = context

    @abstractmethod
    def create_notification(self):
        """
        Abstract method to define the creation logic for a notification.
        """
        raise NotImplementedError

    def _get_sender_content_type(self):
        """
        Retrieve ContentType for the sender.
        """
        return ContentType.objects.get_for_model(self.sender) if self.sender else None

    def _get_entity_content_type(self):
        """
        Retrieve ContentType for the entity.
        """
        return ContentType.objects.get_for_model(self.entity) if self.entity else None

class DefaultNotificationService(BaseNotificationService):
    """
    Default service for creating basic notifications.
    """

    def create_notification(self, action, priority='medium', severity='info', delivery_method='web'):
        """
        Create a standard notification with default behavior.
        """
        notification = Notification.objects.create(
            user=self.user,
            sender_type=self._get_sender_content_type(),
            sender_id=self.sender.id if self.sender else None,
            action=action,
            entity_type=self._get_entity_content_type(),
            entity_id=self.entity.id if self.entity else None,
            context=self.context,
            priority=priority,
            severity=severity,
            delivery_method=delivery_method,
        )
        return notification

class GroupNotificationService(BaseNotificationService):
    """
    Service for grouped notifications.
    """

    def create_notification(self, action, group_id, priority='medium', severity='info', delivery_method='web'):
        """
        Create or update a grouped notification.
        """
        notification, created = Notification.objects.update_or_create(
            user=self.user,
            group_id=group_id,
            defaults={
                'sender_type': self._get_sender_content_type(),
                'sender_id': self.sender.id if self.sender else None,
                'action': action,
                'entity_type': self._get_entity_content_type(),
                'entity_id': self.entity.id if self.entity else None,
                'context': self.context,
                'priority': priority,
                'severity': severity,
                'delivery_method': delivery_method,
                'is_read': False,  # Reset read status for updates
            }
        )
        return notification

class ExpiringNotificationService(BaseNotificationService):
    """
    Service for notifications with expiration dates.
    """

    def create_notification(self, action, expires_in_hours=24, priority='low', severity='info', delivery_method='web'):
        """
        Create a notification with an expiration date.
        """
        expiration_time = now() + timedelta(hours=expires_in_hours)
        notification = Notification.objects.create(
            user=self.user,
            sender_type=self._get_sender_content_type(),
            sender_id=self.sender.id if self.sender else None,
            action=action,
            entity_type=self._get_entity_content_type(),
            entity_id=self.entity.id if self.entity else None,
            context=self.context,
            priority=priority,
            severity=severity,
            delivery_method=delivery_method,
            expires_at=expiration_time,
        )
        return notification

class NotificationServiceFactory:
    """
    Factory to choose the appropriate notification service.
    """

    @staticmethod
    def get_service(service_type, **kwargs):
        """
        Return the appropriate notification service.
        """
        if service_type == 'default':
            return DefaultNotificationService(**kwargs)
        elif service_type == 'grouped':
            return GroupNotificationService(**kwargs)
        elif service_type == 'expiring':
            return ExpiringNotificationService(**kwargs)
        else:
            raise ValueError(f"Unknown service type: {service_type}")

from datetime import timedelta

from django.db import models
from django.utils.timezone import now


class NotificationQuerySet(models.QuerySet):
    def unread(self):
        """
        Retrieve all unread notifications.
        """
        return self.filter(is_read=False)

    def read(self):
        """
        Retrieve all read notifications.
        """
        return self.filter(is_read=True)

    def visible(self):
        """
        Retrieve all notifications that are currently visible.
        """
        return self.filter(is_visible=True)

    def hidden(self):
        """
        Retrieve all archived (hidden) notifications.
        """
        return self.filter(is_visible=False)

    def expired(self):
        """
        Retrieve all expired notifications based on the `expires_at` field.
        """
        return self.filter(expires_at__lte=now())

    def not_expired(self):
        """
        Retrieve notifications that are not expired.
        """
        return self.filter(models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now()))

    def by_user(self, user):
        """
        Retrieve all notifications for a specific user.
        """
        return self.filter(user=user)

    def by_scope(self, scope):
        """
        Retrieve notifications filtered by their scope (e.g., `global`, `user`, `admin`).
        """
        return self.filter(scope=scope)

    def by_priority(self, priority):
        """
        Retrieve notifications filtered by their priority (e.g., `low`, `medium`, `high`).
        """
        return self.filter(priority=priority)

    def by_delivery_method(self, method):
        """
        Retrieve notifications filtered by their delivery method (e.g., `email`, `push`).
        """
        return self.filter(delivery_method=method)

    def by_severity(self, severity):
        """
        Retrieve notifications filtered by their severity level (e.g., `info`, `warning`).
        """
        return self.filter(severity=severity)

    def for_entity(self, entity_type, entity_id):
        """
        Retrieve all notifications related to a specific entity.
        """
        return self.filter(entity_type=entity_type, entity_id=entity_id)

    def grouped_by(self, group_id):
        """
        Retrieve all notifications belonging to a specific group ID.
        """
        return self.filter(group_id=group_id)

    def count_by_user(self):
        """
        Return the count of notifications for each user.
        """
        return self.values('user').annotate(total=models.Count('id')).order_by('-total')

    def count_by_scope(self):
        """
        Return the count of notifications grouped by scope.
        """
        return self.values('scope').annotate(total=models.Count('id')).order_by('-total')

    def count_by_priority(self):
        """
        Return the count of notifications grouped by priority.
        """
        return self.values('priority').annotate(total=models.Count('id')).order_by('-total')

    def count_by_delivery_method(self):
        """
        Return the count of notifications grouped by delivery method.
        """
        return self.values('delivery_method').annotate(total=models.Count('id')).order_by('-total')

    def count_by_severity(self):
        """
        Return the count of notifications grouped by severity.
        """
        return self.values('severity').annotate(total=models.Count('id')).order_by('-total')

    def mark_all_as_read(self, user):
        """
        Mark all unread notifications for a specific user as read.
        """
        return self.filter(user=user, is_read=False).update(is_read=True)

    def mark_all_as_unread(self, user):
        """
        Mark all read notifications for a specific user as unread.
        """
        return self.filter(user=user, is_read=True).update(is_read=False)

    def archive_all(self, user):
        """
        Archive all visible notifications for a specific user.
        """
        return self.filter(user=user, is_visible=True).update(is_visible=False)

    def unarchive_all(self, user):
        """
        Unarchive all hidden notifications for a specific user.
        """
        return self.filter(user=user, is_visible=False).update(is_visible=True)

    def delete_all_expired(self):
        """
        Delete all expired notifications.
        """
        return self.filter(expires_at__lte=models.functions.Now()).delete()

    def created_today(self):
        """
        Retrieve notifications created today.
        """
        today = now().date()
        return self.filter(created_at__date=today)

    def created_in_last(self, days):
        """
        Retrieve notifications created in the last `days` number of days.
        """
        since_date = now() - timedelta(days=days)
        return self.filter(created_at__gte=since_date)

    def updated_in_last(self, hours):
        """
        Retrieve notifications updated in the last `hours` number of hours.
        """
        since_time = now() - timedelta(hours=hours)
        return self.filter(updated_at__gte=since_time)

    def expired_today(self):
        """
        Retrieve notifications that expired today.
        """
        today = now().date()
        return self.filter(expires_at__date=today)

    def expiring_soon(self, hours=24):
        """
        Retrieve notifications that will expire in the next `hours` number of hours.
        """
        upcoming_expiry = now() + timedelta(hours=hours)
        return self.filter(expires_at__lte=upcoming_expiry, expires_at__gte=now())

    def high_priority(self):
        """
        Retrieve all notifications with high priority.
        """
        return self.filter(priority='high')

    def critical_notifications(self):
        """
        Retrieve notifications with severity set to 'warning' or 'error'.
        """
        return self.filter(severity__in=['warning', 'error'])

    def recent(self, limit=10):
        """
        Retrieve the most recent `limit` number of notifications.
        """
        return self.order_by('-created_at')[:limit]

    def for_active_users(self):
        """
        Retrieve notifications for users who are currently active (`user.is_active=True`).
        """
        return self.filter(user__is_active=True)

    def for_active_users(self):
        """
        Retrieve notifications for users who are currently active (`user.is_active=True`).
        """
        return self.filter(user__is_active=True)

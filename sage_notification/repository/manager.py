from django.db import models
from sage_notification.repository.queryset import NotificationQuerySet


class NotificationManager(models.Manager):
    def get_queryset(self):
        """
        Use the custom NotificationQuerySet for all queries.
        """
        return NotificationQuerySet(self.model, using=self._db)

    def unread(self):
        return self.get_queryset().unread()

    def read(self):
        return self.get_queryset().read()

    def visible(self):
        return self.get_queryset().visible()

    def hidden(self):
        return self.get_queryset().hidden()

    def expired(self):
        return self.get_queryset().expired()

    def not_expired(self):
        return self.get_queryset().not_expired()

    def by_user(self, user):
        return self.get_queryset().by_user(user)

    def by_scope(self, scope):
        return self.get_queryset().by_scope(scope)

    def by_priority(self, priority):
        return self.get_queryset().by_priority(priority)

    def by_delivery_method(self, method):
        return self.get_queryset().by_delivery_method(method)

    def by_severity(self, severity):
        return self.get_queryset().by_severity(severity)

    def for_entity(self, entity_type, entity_id):
        return self.get_queryset().for_entity(entity_type, entity_id)

    def grouped_by(self, group_id):
        return self.get_queryset().grouped_by(group_id)

    def count_by_user(self):
        return self.get_queryset().count_by_user()

    def count_by_scope(self):
        return self.get_queryset().count_by_scope()

    def count_by_priority(self):
        return self.get_queryset().count_by_priority()

    def count_by_delivery_method(self):
        return self.get_queryset().count_by_delivery_method()

    def count_by_severity(self):
        return self.get_queryset().count_by_severity()

    def mark_all_as_read(self, user):
        return self.get_queryset().mark_all_as_read(user)

    def mark_all_as_unread(self, user):
        return self.get_queryset().mark_all_as_unread(user)

    def archive_all(self, user):
        return self.get_queryset().archive_all(user)

    def unarchive_all(self, user):
        return self.get_queryset().unarchive_all(user)

    def delete_all_expired(self):
        return self.get_queryset().delete_all_expired()

    def created_today(self):
        return self.get_queryset().created_today()

    def created_in_last(self, days):
        return self.get_queryset().created_in_last(days)

    def updated_in_last(self, hours):
        return self.get_queryset().updated_in_last(hours)

    def expired_today(self):
        return self.get_queryset().expired_today()

    def expiring_soon(self, hours=24):
        return self.get_queryset().expiring_soon(hours)

    def high_priority(self):
        return self.get_queryset().high_priority()

    def critical_notifications(self):
        return self.get_queryset().critical_notifications()

    def recent(self, limit=10):
        return self.get_queryset().recent(limit)

    def for_active_users(self):
        return self.get_queryset().for_active_users()

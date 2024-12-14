from django.db import models
from django.utils import timezone as tz
from django.utils.timezone import localtime
from django.utils.timesince import timesince
from django.core.validators import MaxLengthValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from sage_notification.repository.manager import NotificationManager
from sage_notification.helpers import (
    NotificationPriority,
    NotificationScope,
    NotificationSeverity,
    NotificationDeliveryMethod
)
from sage_tools.mixins.models import TimeStampMixin


class Notification(TimeStampMixin):
    """
    Notification model representing system-wide, user-specific, or admin notifications for various events.

    This model captures details about a notification, including the recipient, the
    action triggering the notification, associated entities, and metadata.
    Notifications can be customized for delivery methods, priority, and visibility scope.

    Generalized Format::

        <recipient> <action> <on entity> <with metadata> <at time>
        <global/system notification> <about event> <to all users/admins> <at time>

    Examples::

        <user:john_doe> <liked> <post_id:42> <{'post_title': 'Great Tips'}> <5 minutes ago>
        <global notification> <system maintenance scheduled> <to all users> <at 3 hours ago>
        <user:jane_doe> <commented> <on article_id:123> <{'comment_excerpt': 'Nice article!'}> <1 day ago>
        <user:admin> <sent warning> <to user:jane_doe> <{'reason': 'Policy violation'}> <2 days ago>

    Unicode Representation::

        john_doe liked post_id:42 (5 minutes ago)
        System Maintenance Scheduled (to all users) (3 hours ago)
        jane_doe commented on article_id:123 (1 day ago)
        Admin sent warning to jane_doe (2 days ago)

    Use Cases::

        - A user likes a post:
            `user:john_doe` `liked` `post_id:42` `{'post_title': 'Great Tips'}` `at 5 minutes ago`.

        - A global notification about maintenance:
            `system notification` `scheduled maintenance` `to all users` `at 3 hours ago`.

        - A warning notification:
            `user:admin` `sent warning` `to user:jane_doe` `{'reason': 'Policy violation'}` `at 2 days ago`.

        - A user comments on an article:
            `user:jane_doe` `commented` `on article_id:123` `{'comment_excerpt': 'Nice article!'}` `at 1 day ago`.
    """ 

    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
        verbose_name=_("Recipient"),
        help_text=_("The user who receives this notification."),
        db_comment=(
            "Refers to the user who is the recipient of the notification. Null for "
            "global notifications."
        )
    )

    sender_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='notification_senders',
        verbose_name=_("Sender Type"),
        help_text=_("The type of the sender object (e.g., User, System)."),
        db_comment=(
            "Specifies the type of the sender (e.g., User, System) using the "
            "ContentType framework."
        )
    )
    sender_id = models.PositiveIntegerField(
        verbose_name=_("Sender ID"),
        help_text=_("The ID of the sender object."),
        db_comment="References the specific ID of the sender object."
    )
    sender = GenericForeignKey('sender_type', 'sender_id')

    action = models.CharField(
        max_length=255,
        verbose_name=_("Action"),
        help_text=_("Short description of the action (e.g., 'commented', 'liked')."),
        db_comment=(
            "Describes the action performed (e.g., 'liked', 'commented')."
        ),
        validators=[MaxLengthValidator(255)]
    )
    entity_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='notification_entities',
        null=True,
        blank=True,
        verbose_name=_("Entity Type"),
        help_text=_("The type of the associated entity (e.g., Post, Comment)."),
        db_comment=(
            "Specifies the type of the associated entity using the ContentType "
            "framework."
        )
    )
    entity_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Entity ID"),
        help_text=_("The ID of the associated entity (optional)."),
        db_comment=(
            "References the specific ID of the associated entity (optional)."
        )
    )
    entity = GenericForeignKey('entity_type', 'entity_id')

    context = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_("Context"),
        help_text=_("Additional details or metadata about the notification."),
        db_comment=(
            "Stores additional metadata or contextual information in JSON format. "
            "Ensure valid JSON structure."
        )
    )

    is_read = models.BooleanField(
        default=False,
        verbose_name=_("Is Read"),
        help_text=_("Whether the notification has been read by the user."),
        db_comment="Indicates whether the user has read the notification. Defaults to False."
    )
    is_sent = models.BooleanField(
        default=False,
        verbose_name=_("Is Sent"),
        help_text=_("Whether the notification has been sent via email or another channel."),
        db_comment=(
            "Indicates whether the notification has been sent via external channels. "
            "Defaults to False."
        )
    )
    priority = models.CharField(
        max_length=50,
        choices=NotificationPriority.choices,
        default=NotificationPriority.MEDIUM,
        verbose_name=_("Priority"),
        help_text=_("Priority level of the notification (e.g., low, medium, high)."),
        db_comment="Specifies the priority of the notification. Defaults to 'medium'."
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Expires At"),
        help_text=_("When the notification expires and should no longer be displayed."),
        db_comment=(
            "The timestamp after which the notification becomes invalid. Used to "
            "automatically filter expired notifications."
        )
    )
    is_visible = models.BooleanField(
        default=True,
        verbose_name=_("Is Visible"),
        help_text=_("Whether the notification is currently visible to the user."),
        db_comment=(
            "Indicates if the notification should be displayed to the user. "
            "Set to False to archive notifications."
        )
    )
    scope = models.CharField(
        max_length=50,
        choices=NotificationScope.choices,
        default=NotificationScope.USER,
        verbose_name=_("Scope"),
        help_text=_("Defines the visibility scope of the notification."),
        db_comment=(
            "Specifies the scope of the notification. Possible values: "
            "'global' for system-wide notifications, "
            "'user' for user-specific notifications, and 'admin' for admin-only "
            "notifications. Defaults to 'user'."
        )
    )
    group_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("Group ID"),
        help_text=_("Identifier for grouping similar notifications."),
        db_comment=(
            "A unique identifier used to group related notifications "
            "(e.g., likes on the same post). "
            "Helps in aggregating notifications for better user experience."
        )
    )
    delivery_method = models.CharField(
        max_length=50,
        choices=NotificationDeliveryMethod.choices,
        default=NotificationDeliveryMethod.WEB,
        verbose_name=_("Delivery Method"),
        help_text=_("The method used to deliver this notification."),
        db_comment=(
            "Defines the delivery method for the notification. Possible values: "
            "'email', 'push', 'sms', or 'web'.  Defaults to 'web'."
        )
    )
    severity = models.CharField(
        max_length=50,
        choices=NotificationSeverity.choices,
        default=NotificationSeverity.INFO,
        verbose_name=_("Severity"),
        help_text=_("The severity level of the notification."),
        db_comment=(
            "Specifies the severity level of the notification. Possible values: "
            "'success', 'info', 'warning', 'error'. Defaults to 'info'."
        )
    )

    objects = NotificationManager()

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ['-created_at']
        db_table = 'notification'
        indexes = [
            models.Index(fields=['user'], name='notification_user_idx'),
            models.Index(fields=['is_read'], name='notification_is_read_idx'),
            models.Index(fields=['priority'], name='notification_priority_idx'),
            models.Index(fields=['created_at'], name='notification_created_at_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(priority__in=['low', 'medium', 'high']),
                name='valid_priority'
            )
        ]

    def __str__(self):
        user_repr = f"user={self.user}" if self.user else "global"
        return f"Notification(id={self.id}, action={self.action}, {user_repr})"

    def mark_as_read(self):
        """
        Mark the notification as read.
        """
        if not self.is_read:
            self.is_read = True
            self.save()

    def mark_as_unread(self):
        """
        Mark the notification as unread.
        """
        if self.is_read:
            self.is_read = False
            self.save()

    def toggle_read_status(self):
        """
        Toggle the read status of the notification.
        """
        self.is_read = not self.is_read
        self.save()

    def archive(self):
        """
        Archive the notification by setting is_visible to False.
        """
        if self.is_visible:
            self.is_visible = False
            self.save()

    def unarchive(self):
        """
        Unarchive the notification by setting is_visible to True.
        """
        if not self.is_visible:
            self.is_visible = True
            self.save()

    def is_expired(self):
        """
        Check if the notification has expired.
        """
        if self.expires_at:
            return self.expires_at <= tz.now()
        return False

    def send_notification(self):
        """
        Simulate sending the notification via the specified delivery method.
        """
        if not self.is_sent:
            # Add logic to send via email, push, or SMS based on delivery_method
            self.is_sent = True
            self.save()

    def resend_notification(self):
        """
        Resend the notification if it has already been sent.
        """
        if self.is_sent:
            # Add resend logic here (e.g., send via email/push/SMS)
            # Example: self.send_notification() or call a service
            pass

    def get_display_message(self):
        """
        Construct a user-friendly message for the notification.
        """
        base_message = f"Action: {self.action}"
        if self.context:
            base_message += f", Context: {self.context}"
        if self.entity:
            base_message += f", Related Entity: {self.entity}"
        return base_message

    def get_group_display(self):
        """
        Get a display-friendly string for the notification's group.
        """
        return self.group_id if self.group_id else "Ungrouped"

    def is_high_severity(self):
        """
        Check if the notification's severity is 'warning' or 'error'.
        """
        return self.severity in [
            NotificationSeverity.WARNING,
            NotificationSeverity.ERROR
        ]

    def time_since_created(self):
        """
        Return a human-readable time difference like '1 day ago' or '3 hours ago'.
        """
        return f"{timesince(self.created_at, tz.now())} ago"

    def natural_day(self):
        """
        Return natural day descriptions like 'today', 'yesterday', or a date string.
        """
        from django.template.defaultfilters import date
        return date(self.created_at, "N j, Y, P")

    def human_readable_time(self):
        """
        Return a human-readable time difference or natural day description.
        """
        current_time = tz.now()
        time_difference = current_time - self.created_at

        # Time difference in seconds
        seconds = time_difference.total_seconds()

        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif seconds < 172800:  # Less than 2 days
            return "yesterday"
        else:
            return localtime(self.created_at).strftime("%b %d, %Y")  # e.g., "Jan 01, 2023"

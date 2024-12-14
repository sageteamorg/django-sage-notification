from datetime import timedelta
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.admin import GenericStackedInline
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType

from sage_notification.models import Notification
from sage_notification.forms import NotificationAdminForm

class ContextInline(GenericStackedInline):
    model = Notification
    ct_field = 'entity_type'
    ct_fk_field = 'entity_id'
    fields = ('context',)
    extra = 0

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.utils.translation import gettext_lazy as _
from .models import Notification


from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.utils.translation import gettext_lazy as _
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Django admin interface for the Notification model.
    Organized with fieldsets for better clarity and usability.
    Handles generic foreign keys gracefully.
    """

    list_display = (
        'id', 'user', 'action', 'priority', 'is_read', 'is_sent', 'created_at', 'expires_at', 'scope'
    )
    list_filter = (
        'is_read', 'is_sent', 'priority', 'severity', 'delivery_method', 'scope', 'created_at', 'expires_at'
    )
    search_fields = ('user__username', 'action', 'group_id', 'context')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'modified_at', 'sender', 'entity')
    save_on_top = True
    autocomplete_fields = (
        'user',
    )


    actions = [
        "mark_selected_as_read",
        "mark_selected_as_unread",
        "archive_selected",
        "unarchive_selected",
        "delete_selected",
        "mark_selected_as_sent",
        "mark_selected_as_unsent",
        "update_priority_to_high",
        "update_priority_to_low",
        "expire_selected",
        "extend_expiration",
    ]

    fieldsets = (
        (_("Notification Details"), {
            'fields': ('user', 'action', 'context', 'group_id', 'is_read', 'is_sent', 'is_visible')
        }),
        (_("Sender Information"), {
            'fields': ('sender_type', 'sender_id'),
            'description': _("Details about the sender of the notification, such as type and ID.")
        }),
        (_("Related Entity"), {
            'fields': ('entity_type', 'entity_id'),
            'description': _("Information about the associated entity, such as a post or comment.")
        }),
        (_("Delivery and Priority"), {
            'fields': ('priority', 'severity', 'delivery_method', 'scope', 'expires_at'),
            'description': _("Settings for delivery, priority, and expiration of the notification.")
        }),
        (_("Timestamps"), {
            'fields': ('created_at', 'modified_at'),
            'description': _("Automatically managed timestamps for creation and modification.")
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        """
        Customize the admin form to handle generic foreign keys.
        """
        form = super().get_form(request, obj, **kwargs)

        # Add placeholder text for generic fields
        form.base_fields['sender_type'].widget.attrs.update({'placeholder': _('Select sender type (e.g., User, System)')})
        form.base_fields['entity_type'].widget.attrs.update({'placeholder': _('Select entity type (e.g., Post, Comment)')})

        return form

    @admin.display(description=_('Sender'))
    def sender(self, obj):
        """Display the sender object in a readable format."""
        return str(obj.sender) if obj.sender else "-"

    @admin.display(description=_('Entity'))
    def entity(self, obj):
        """Display the entity object in a readable format."""
        return str(obj.entity) if obj.entity else "-"

    @admin.action(description=_("Mark selected notifications as read"))
    def mark_selected_as_read(self, request, queryset):
        updated_count = queryset.update(is_read=True)
        self.message_user(request, _("%d notifications marked as read.") % updated_count)

    @admin.action(description=_("Mark selected notifications as unread"))
    def mark_selected_as_unread(self, request, queryset):
        updated_count = queryset.update(is_read=False)
        self.message_user(request, _("%d notifications marked as unread.") % updated_count)

    @admin.action(description=_("Archive selected notifications"))
    def archive_selected(self, request, queryset):
        updated_count = queryset.update(is_visible=False)
        self.message_user(request, _("%d notifications archived.") % updated_count)

    @admin.action(description=_("Unarchive selected notifications"))
    def unarchive_selected(self, request, queryset):
        updated_count = queryset.update(is_visible=True)
        self.message_user(request, _("%d notifications unarchived.") % updated_count)

    @admin.action(description=_("Delete selected notifications"))
    def delete_selected(self, request, queryset):
        deleted_count = queryset.delete()[0]
        self.message_user(request, _("%d notifications deleted.") % deleted_count)

    @admin.action(description=_("Mark selected notifications as sent"))
    def mark_selected_as_sent(self, request, queryset):
        updated_count = queryset.update(is_sent=True)
        self.message_user(request, _("%d notifications marked as sent.") % updated_count)

    @admin.action(description=_("Mark selected notifications as unsent"))
    def mark_selected_as_unsent(self, request, queryset):
        updated_count = queryset.update(is_sent=False)
        self.message_user(request, _("%d notifications marked as unsent.") % updated_count)

    @admin.action(description=_("Update priority of selected notifications to high"))
    def update_priority_to_high(self, request, queryset):
        updated_count = queryset.update(priority='high')
        self.message_user(request, _("%d notifications updated to high priority.") % updated_count)

    @admin.action(description=_("Update priority of selected notifications to low"))
    def update_priority_to_low(self, request, queryset):
        updated_count = queryset.update(priority='low')
        self.message_user(request, _("%d notifications updated to low priority.") % updated_count)

    @admin.action(description=_("Expire selected notifications"))
    def expire_selected(self, request, queryset):
        updated_count = queryset.update(expires_at=now())
        self.message_user(request, _("%d notifications expired.") % updated_count)

    @admin.action(description=_("Extend expiration of selected notifications by 7 days"))
    def extend_expiration(self, request, queryset):
        extended_count = 0
        for notification in queryset:
            if notification.expires_at:
                notification.expires_at += timedelta(days=7)
                notification.save()
                extended_count += 1
        self.message_user(request, _("%d notifications' expiration extended by 7 days.") % extended_count)

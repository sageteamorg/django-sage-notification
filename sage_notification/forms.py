from django import forms
from django.contrib.contenttypes.models import ContentType
from sage_notification.models import Notification


class NotificationAdminForm(forms.ModelForm):
    sender_content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.all(),
        label="Sender Type",
        required=False,
        help_text="Select the type of the sender (e.g., User, Post)."
    )
    sender_object_id = forms.IntegerField(
        label="Sender Object ID",
        required=False,
        help_text="Enter the ID of the sender object."
    )

    class Meta:
        model = Notification
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        sender_type = cleaned_data.get('sender_content_type')
        sender_id = cleaned_data.get('sender_object_id')

        if sender_type and not sender_id:
            raise forms.ValidationError("You must specify an object ID for the selected sender type.")
        if not sender_type and sender_id:
            raise forms.ValidationError("You must select a sender type if providing an object ID.")

        # Assign sender_type and sender_id to the instance
        cleaned_data['sender_type'] = sender_type
        cleaned_data['sender_id'] = sender_id

        return cleaned_data

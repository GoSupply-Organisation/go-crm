"""Communication tracking models for Go CRM.

This module defines models for tracking email and SMS communications
sent to contacts in the CRM system. These models provide a history
of all communications with each contact.
"""

from django.db import models
from user.models import CustomUser
from contacts.models import Contact


class sent_emails(models.Model):
    """Model representing an email sent to a contact.

    This model tracks all emails sent through the CRM system,
    storing the subject, message content, timestamp, and sender
    information.

    Attributes:
        contact: The contact who received the email.
        subject: Email subject line.
        message: Email body content.
        sent_at: Timestamp when the email was sent.
        from_email: Sender's email address.
        sent_by: User who sent the email (if authenticated).
    """

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.CharField(null=True, blank=True, max_length=2000)
    sent_at = models.DateTimeField(auto_now_add=True)
    from_email = models.EmailField(null=True, blank=True)
    sent_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        """Return string representation of the email.

        Returns:
            str: Description including recipient name and timestamp.
        """
        return f"Email to {self.contact.Full_name} on {self.sent_at.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        """Meta options for sent_emails model.

        Attributes:
            ordering: Default ordering for queries by sent time (newest first).
            verbose_name: Human-readable name for the model.
            verbose_name_plural: Human-readable plural name.
        """
        ordering = ['-sent_at']
        verbose_name = 'Sent Email'
        verbose_name_plural = 'Sent Emails'


class sent_sms(models.Model):
    """Model representing an SMS message sent to a contact.

    This model tracks all SMS messages sent through the CRM system,
    storing the message body and timestamp.

    Attributes:
        contact: The contact who received the SMS.
        body: SMS message content (max 2000 characters).
        sent_at: Timestamp when the SMS was sent.
    """

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    body = models.CharField(max_length=2000, blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return string representation of the SMS.

        Returns:
            str: Description including recipient name and timestamp.
        """
        return f"SMS to {self.contact.Full_name} on {self.sent_at.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        """Meta options for sent_sms model.

        Attributes:
            ordering: Default ordering for queries by sent time (newest first).
            verbose_name: Human-readable name for the model.
            verbose_name_plural: Human-readable plural name.
        """
        ordering = ['-sent_at']
        verbose_name = 'Sent SMS'
        verbose_name_plural = 'Sent SMS'

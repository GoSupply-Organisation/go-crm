"""API endpoints for email and SMS communications.

This module provides Django Ninja API endpoints for sending emails and SMS
messages to contacts, as well as retrieving communication history.
"""

from ninja import ModelSchema, Router, Schema
from ninja.security import django_auth
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from django.utils import timezone
from sms import send_sms
from .models import sent_emails, sent_sms
from contacts.models import Contact


class SentEmailSchema(ModelSchema):
    """Schema for sent_emails model serialization.

    This schema defines which fields are included when serializing
    sent_emails objects for API responses.
    """

    class Meta:
        """Meta configuration for SentEmailSchema.

        Attributes:
            model: The Django model to serialize.
            fields: List of fields to include in serialization.
        """
        model = sent_emails
        fields = [
            'id',
            'contact',
            'subject',
            'message',
            'sent_at',
            'from_email',
            'sent_by',
        ]


class SentSmsSchema(ModelSchema):
    """Schema for sent_sms model serialization.

    This schema defines which fields are included when serializing
    sent_sms objects for API responses.
    """

    class Meta:
        """Meta configuration for SentSmsSchema.

        Attributes:
            model: The Django model to serialize.
            fields: List of fields to include in serialization.
        """
        model = sent_sms
        fields = [
            'id',
            'contact',
            'body',
            'sent_at',
        ]


class EmailSendSchema(Schema):
    """Schema for sending an email.

    This schema validates input data for email sending requests.
    """

    subject: str
    message: str


class SMSSendSchema(Schema):
    """Schema for sending an SMS.

    This schema validates input data for SMS sending requests.
    """

    body: str


communications_router = Router()


@communications_router.post("/send-email/{contact_id}", response=SentEmailSchema, auth=django_auth)
def send_email_endpoint(request, contact_id: int, payload: EmailSendSchema):
    """Send an email to a contact.

    This endpoint sends an email to the specified contact using Django's
    email system. After successful sending, the email is logged in the
    sent_emails table. If the contact's lead_class is 'New', it will be
    automatically updated to 'Contacted'.

    Args:
        request: Django request object with authenticated user.
        contact_id: Primary key of the contact to send email to.
        payload: EmailSendSchema containing subject and message.

    Returns:
        SentEmailSchema: The created email record.

    Raises:
        Http404: If contact with given ID does not exist.

    Authentication:
        Requires valid Django session authentication.
    """
    contact = get_object_or_404(Contact, pk=contact_id)

    message = EmailMessage(
        subject=payload.subject,
        body=payload.message,
        from_email="zachaldin@outlook.com",
        to=[contact.email],
    )

    message.send()

    # Create email record
    email_record = sent_emails.objects.create(
        contact=contact,
        subject=payload.subject,
        message=payload.message,
        sent_at=timezone.now(),
        from_email="zachaldin@outlook.com",
        sent_by=request.user.id if request.user.is_authenticated else None
    )

    # Update lead class if it's a new contact
    if contact.lead_class == "New":
        contact.lead_class = "Contacted"
        contact.save()

    return email_record


@communications_router.post("/send-sms/{contact_id}", response=SentSmsSchema, auth=django_auth)
def send_sms_endpoint(request, contact_id: int, payload: SMSSendSchema):
    """Send an SMS message to a contact.

    This endpoint sends an SMS to the specified contact using the SMS API.
    After successful sending, the SMS is logged in the sent_sms table.
    If the contact's lead_class is 'New', it will be automatically
    updated to 'Contacted'.

    Args:
        request: Django request object with authenticated user.
        contact_id: Primary key of the contact to send SMS to.
        payload: SMSSendSchema containing the message body.

    Returns:
        SentSmsSchema: The created SMS record.

    Raises:
        HttpError: If contact not found (404), missing data (400),
                  or SMS sending fails (500).

    Authentication:
        Requires valid Django session authentication.
    """
    try:
        contact = get_object_or_404(Contact, pk=contact_id)
        company_number = "0424854899"
        recip_number = contact.phone_number

        if not all([payload.body, recip_number]):
            from ninja.errors import HttpError
            raise HttpError(400, 'Need body and phone number')

        sms = send_sms(
            body=payload.body,
            originator=company_number,
            recipients=[recip_number]
        )

        sms_record = sent_sms.objects.create(
            contact=contact,
            body=payload.body,
            sent_at=timezone.now()
        )

        if sms and contact.lead_class == "New":
            contact.lead_class = "Contacted"
            contact.save()

        return sms_record

    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(500, f'Failed to send SMS: {str(e)}')


@communications_router.get("/communication-logs", response=dict, auth=django_auth)
def get_communication_logs(request):
    """Retrieve all email and SMS communication logs.

    This endpoint returns a combined list of all sent emails and SMS
    messages, ordered by most recent first.

    Args:
        request: Django request object.

    Returns:
        dict: Dictionary containing:
            - emails: List of all sent emails with contact info
            - sms: List of all sent SMS messages with contact info

    Authentication:
        Requires valid Django session authentication.
    """
    email_logs = sent_emails.objects.all().order_by('-sent_at')
    sms_logs = sent_sms.objects.all().order_by('-sent_at')

    email_list = [
        {
            "id": e.id,
            "contact": e.contact.Full_name,
            "contact_id": e.contact.id,
            "subject": e.subject,
            "message": e.message,
            "sent_at": e.sent_at.isoformat()
        } for e in email_logs
    ]

    sms_list = [
        {
            "id": s.id,
            "contact": s.contact.Full_name,
            "contact_id": s.contact.id,
            "body": s.body,
            "sent_at": s.sent_at.isoformat()
        } for s in sms_logs
    ]

    return {"emails": email_list, "sms": sms_list}


@communications_router.get("/contact-emails/{contact_id}", response=list[SentEmailSchema], auth=django_auth)
def get_contact_emails(request, contact_id: int):
    """Retrieve all emails sent to a specific contact.

    This endpoint returns all emails that have been sent to the
    specified contact, ordered by most recent first.

    Args:
        request: Django request object.
        contact_id: Primary key of the contact.

    Returns:
        list[SentEmailSchema]: List of emails sent to the contact.

    Raises:
        Http404: If contact with given ID does not exist.

    Authentication:
        Requires valid Django session authentication.
    """
    contact = get_object_or_404(Contact, pk=contact_id)
    emails = sent_emails.objects.filter(contact=contact).order_by('-sent_at')
    return emails

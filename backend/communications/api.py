from ninja import ModelSchema, Router
from ninja.security import django_auth
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.utils import timezone
from sms import send_sms
from .models import sent_emails, sent_sms
from contacts.models import Contact


class SentEmailSchema(ModelSchema):
    class Meta:
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
    class Meta:
        model = sent_sms
        fields = [
            'id',
            'contact',
            'body',
            'sent_at',
        ]


communications_router = Router()


@communications_router.post("/send-email/{contact_id}", response=SentEmailSchema, auth=django_auth)
def send_email_endpoint(request, contact_id: int, payload: dict):
    try:
        contact = get_object_or_404(Contact, pk=contact_id)
        subject = payload.get('subject')
        message = payload.get('message')
        from_email = payload.get('from_email', contact.email)

        if not all([subject, message]):
            from ninja.errors import HttpError
            raise HttpError(400, 'Subject and message are required')

        sent = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[contact.email],
            fail_silently=False,
        )

        email_record = sent_emails.objects.create(
            contact=contact,
            subject=subject,
            message=message,
            sent_at=timezone.now(),
            from_email=from_email,
            sent_by=request.auth
        )

        if sent and contact.lead_class == "New":
            contact.lead_class = "Contacted"
            contact.save()

        return email_record

    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(500, f'Failed to send email: {str(e)}')


@communications_router.post("/send-sms/{contact_id}", response=SentSmsSchema, auth=django_auth)
def send_sms_endpoint(request, contact_id: int, payload: dict):
    try:
        contact = get_object_or_404(Contact, pk=contact_id)
        company_number = "0424854899"
        body = payload.get('body')
        recip_number = contact.phone_number

        if not all([body, recip_number]):
            from ninja.errors import HttpError
            raise HttpError(400, 'Need body and phone number')

        sms = send_sms(
            body=body,
            originator=company_number,
            recipients=[recip_number]
        )

        sms_record = sent_sms.objects.create(
            contact=contact,
            body=body,
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
    contact = get_object_or_404(Contact, pk=contact_id)
    emails = sent_emails.objects.filter(contact=contact).order_by('-sent_at')
    return emails
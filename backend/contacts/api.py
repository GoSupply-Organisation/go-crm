from ninja import NinjaAPI, ModelSchema
from .models import Contact, sent_emails, sent_sms
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.utils import timezone
from sms import send_sms

class ContactSchema(ModelSchema):
    class Meta:
        model = Contact
        fields = [
            'id',
            'Full_name',
            'email',
            'phone_number',
            'company',
            'lead_class',
            'notes',
            'address',
            'created_at',
        ]

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
contact_api = NinjaAPI()

@contact_api.get("/index", response=list[ContactSchema])
def contact_list(request):
    if not request.user.is_authenticated:
        return 403, {'error': 'Authentication required'}

    lead_class = request.GET.get('lead_class')
    search_query = request.GET.get('search')
    sort_by = request.GET.get('sort_by', 'Full_name')

    contacts = Contact.objects.all()

    if lead_class:
        contacts = contacts.filter(lead_class=lead_class)

    if search_query:
        contacts = contacts.filter(
            Q(Full_name__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )

    contacts = contacts.order_by(sort_by)

    return 200, contacts


@contact_api.post("/add", response=ContactSchema)
def create_contact(request, payload: ContactSchema):
    if not request.user.is_authenticated:
        return 403, {'error': 'Authentication required'}

    contact = Contact.objects.create(
        Full_name=payload.Full_name,
        email=payload.email,
        phone_number=payload.phone_number,
        company=payload.company,
        lead_class=payload.lead_class or 'New',
        notes=payload.notes,
        address=payload.address,
    )
    return 201, contact

@contact_api.get("/moreinfo/{contact_id}", response=ContactSchema)
def contact_detail(request, contact_id: int):
    if not request.user.is_authenticated:
        return 403, {'error': 'Authentication required'}

    contact = get_object_or_404(Contact, pk=contact_id)
    return 200, contact

@contact_api.post("/update/{contact_id}", response=ContactSchema)
def edit_contact(request, contact_id: int, payload: ContactSchema):
    if not request.user.is_authenticated:
        return 403, {'error': 'Authentication required'}

    try:
        contact = Contact.objects.get(pk=contact_id)
        contact.Full_name = payload.Full_name
        contact.email = payload.email
        contact.phone_number = payload.phone_number
        contact.company = payload.company
        contact.lead_class = payload.lead_class
        contact.notes = payload.notes
        contact.address = payload.address
        contact.save()
        return 200, contact
    except Contact.DoesNotExist:
        return 404, {'error': 'Contact not found'}

@contact_api.delete("/delete/{contact_id}")
def delete_contact(request, contact_id: int):
    if not request.user.is_authenticated:
        return 403, {'error': 'Authentication required'}

    try:
        contact = get_object_or_404(Contact, pk=contact_id)
        contact_name = contact.Full_name if contact.Full_name else 'Unnamed Contact'
        contact.delete()
        return 200, {'success': True, 'message': f'Contact {contact_name} deleted successfully'}
    except Exception as e:
        return 500, {'success': False, 'error': str(e)}


@contact_api.post("/send-email/{contact_id}", response=SentEmailSchema)
def send_email_endpoint(request, contact_id: int, payload: dict):
    if not request.user.is_authenticated:
        return 403, {'error': 'Authentication required'}

    try:
        contact = get_object_or_404(Contact, pk=contact_id)
        subject = payload.get('subject')
        message = payload.get('message')
        from_email = payload.get('from_email', contact.email)

        if not all([subject, message]):
            return 400, {'error': 'Subject and message are required'}

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
            sent_by=request.user if request.user.is_authenticated else None
        )

        if sent and contact.lead_class == "New":
            contact.lead_class = "Contacted"
            contact.save()

        return 201, email_record

    except Exception as e:
        return 500, {'error': f'Failed to send email: {str(e)}'}

@contact_api.post("/send-sms/{contact_id}", response=SentSmsSchema)
def send_sms_endpoint(request, contact_id: int, payload: dict):
    if not request.user.is_authenticated:
        return 403, {'error': 'Authentication required'}

    try:
        contact = get_object_or_404(Contact, pk=contact_id)
        company_number = "0424854899"
        body = payload.get('body')
        recip_number = contact.phone_number

        if not all([body, recip_number]):
            return 400, {'error': 'Need body and phone number'}

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

        return 201, sms_record

    except Exception as e:
        return 500, {'error': f'Failed to send SMS: {str(e)}'}

@contact_api.get("/communication-logs")
def get_communication_logs(request):
    if not request.user.is_authenticated:
        return 403, {'error': 'Authentication required'}

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

    return 200, {"emails": email_list, "sms": sms_list}

@contact_api.get("/contact-emails/{contact_id}", response=list[SentEmailSchema])
def get_contact_emails(request, contact_id: int):
    if not request.user.is_authenticated:
        return 403, {'error': 'Authentication required'}

    contact = get_object_or_404(Contact, pk=contact_id)
    emails = sent_emails.objects.filter(contact=contact).order_by('-sent_at')
    return 200, emails


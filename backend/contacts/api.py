from ninja import ModelSchema, Router
from ninja.security import django_auth
from .models import Contact
from django.db.models import Q
from django.shortcuts import get_object_or_404


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

class ContactCreateSchema(ModelSchema):
    class Meta:
        model = Contact
        fields = [
            'Full_name',
            'email',
            'phone_number',
            'company',
            'lead_class',
            'notes',
            'address',
        ]


contact_router = Router()


@contact_router.get("/index", response=list[ContactSchema], auth=django_auth)
def contact_list(request):
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

    return contacts


@contact_router.post("/add", response=ContactSchema, auth=django_auth)
def create_contact(request, payload: ContactCreateSchema):
    contact = Contact.objects.create(
        Full_name=payload.Full_name,
        email=payload.email,
        phone_number=payload.phone_number,
        company=payload.company,
        lead_class=payload.lead_class or 'New',
        notes=payload.notes,
        address=payload.address,
    )
    return contact

@contact_router.get("/moreinfo/{contact_id}", response=ContactSchema, auth=django_auth)
def contact_detail(request, contact_id: int):
    contact = get_object_or_404(Contact, pk=contact_id)
    return contact

@contact_router.post("/update/{contact_id}", response=ContactSchema, auth=django_auth)
def edit_contact(request, contact_id: int, payload: ContactCreateSchema):
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
        return contact
    except Contact.DoesNotExist:
        from ninja.errors import HttpError
        raise HttpError(404, 'Contact not found')

@contact_router.delete("/delete/{contact_id}", response=dict, auth=django_auth)
def delete_contact(request, contact_id: int):
    try:
        contact = get_object_or_404(Contact, pk=contact_id)
        contact_name = contact.Full_name if contact.Full_name else 'Unnamed Contact'
        contact.delete()
        return {'success': True, 'message': f'Contact {contact_name} deleted successfully'}
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(500, str(e))


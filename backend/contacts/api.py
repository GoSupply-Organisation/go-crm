"""API endpoints for contact management in Go CRM.

This module provides Django Ninja API endpoints for creating, reading,
updating, and deleting contacts. It includes filtering, searching, and
sorting capabilities.
"""

from ninja import ModelSchema, Router
from ninja.security import django_auth
from .models import Contact
from django.db.models import Q
from django.shortcuts import get_object_or_404


class ContactSchema(ModelSchema):
    """Schema for Contact model serialization.

    This schema defines which fields are included when serializing
    Contact objects for API responses.
    """

    class Meta:
        """Meta configuration for ContactSchema.

        Attributes:
            model: The Django model to serialize.
            fields: List of fields to include in serialization.
        """
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
    """Schema for creating new contacts.

    This schema validates input data when creating a new contact.
    Excludes id and created_at as they are auto-generated.
    """

    class Meta:
        """Meta configuration for ContactCreateSchema.

        Attributes:
            model: The Django model for validation.
            fields: List of fields required for contact creation.
        """
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
    """Retrieve a list of contacts with optional filtering and sorting.

    This endpoint returns all contacts with support for filtering by lead
    classification, searching by name/company/email/phone, and sorting by
    specified fields.

    Args:
        request: Django request object containing GET parameters.

    Query Parameters:
        lead_class: Optional filter by lead classification.
        search: Optional search term for name, company, email, or phone.
        sort_by: Field to sort by (default: 'Full_name').

    Returns:
        list[ContactSchema]: List of filtered and sorted contacts.

    Authentication:
        Requires valid Django session authentication.
    """
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
    """Create a new contact in the CRM.

    This endpoint creates a new Contact object with the provided data.

    Args:
        request: Django request object.
        payload: ContactCreateSchema containing contact data.

    Returns:
        ContactSchema: The created contact object.

    Authentication:
        Requires valid Django session authentication.
    """
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
    """Retrieve detailed information about a specific contact.

    Args:
        request: Django request object.
        contact_id: Primary key of the contact to retrieve.

    Returns:
        ContactSchema: The requested contact object.

    Raises:
        Http404: If no contact with the given ID exists.

    Authentication:
        Requires valid Django session authentication.
    """
    contact = get_object_or_404(Contact, pk=contact_id)
    return contact


@contact_router.put("/update/{contact_id}", response=ContactSchema, auth=django_auth)
def edit_contact(request, contact_id: int, payload: ContactCreateSchema):
    """Update an existing contact.

    This endpoint updates all fields of a contact with the provided data.

    Args:
        request: Django request object.
        contact_id: Primary key of the contact to update.
        payload: ContactCreateSchema containing updated contact data.

    Returns:
        ContactSchema: The updated contact object.

    Raises:
        HttpError: If contact with given ID does not exist (404).

    Authentication:
        Requires valid Django session authentication.
    """
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
    """Delete a contact from the CRM.

    Args:
        request: Django request object.
        contact_id: Primary key of the contact to delete.

    Returns:
        dict: Dictionary containing success status and message.

    Raises:
        HttpError: If deletion fails with error code 500.

    Authentication:
        Requires valid Django session authentication.
    """
    try:
        contact = get_object_or_404(Contact, pk=contact_id)
        contact_name = contact.Full_name if contact.Full_name else 'Unnamed Contact'
        contact.delete()
        return {'success': True, 'message': f'Contact {contact_name} deleted successfully'}
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(500, str(e))

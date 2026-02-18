"""API endpoints for AI-powered lead generation and research.

This module provides Django Ninja API endpoints for the Super Researcher,
including automated lead generation, lead management, and AI-powered research.
"""

from ninja import ModelSchema, Router, Schema
from ninja.security import django_auth
from .models import SuperResearcher
from .tasks import product_engine_research
from django.http import JsonResponse
from django.db.models import Q


class SuperResearcherSchema(ModelSchema):
    """Schema for SuperResearcher model serialization.

    This schema defines which fields are included when serializing
    SuperResearcher objects for API responses.
    """

    class Meta:
        """Meta configuration for SuperResearcherSchema.

        Attributes:
            model: The Django model to serialize.
            fields: List of fields to include in serialization.
        """
        model = SuperResearcher
        fields = [
            'id',
            'company',
            'website',
            'phone_number',
            'email',
            'full_name',
            'promoted',
            'is_active_lead',
            'lead_class',
            'notes',
            'address',
        ]


super_researcher_router = Router()


@super_researcher_router.get("/current-leads/", response=SuperResearcherSchema, auth=django_auth)
def get_current_lead(request):
    """Retrieve the most recently generated AI lead.

    This endpoint returns the first lead in the database, which represents
    the most recently generated AI lead.

    Args:
        request: Django request object.

    Returns:
        SuperResearcherSchema: The current lead or error message.

    Authentication:
        Requires valid Django session authentication.
    """
    leads = SuperResearcher.objects.all()
    if leads:
        lead = leads.first()
        return lead
    else:
        return JsonResponse({"message": "No leads found"})


@super_researcher_router.get("/generate-leads/", response=dict, auth=django_auth)
def periodic_lead_generation(request):
    """Generate AI-powered leads through automated research.

    This endpoint triggers the product-engine research pipeline to discover new leads:
    1. Runs the Celery research task with the default prompt
    2. Executes reliability and urgency analysis
    3. Saves results to Weaviate vector database

    Args:
        request: Django request object.

    Returns:
        dict: Dictionary containing success status, task ID, and message
              or error details if generation fails.

    Authentication:
        Requires valid Django session authentication.
    """
    try:
        # Trigger the Celery task asynchronously
        task = product_engine_research.delay()

        print(f"Started product-engine research task (ID: {task.id})")
        return {
            'success': True,
            'task_id': task.id,
            'message': 'Research pipeline started. Check Celery logs for progress.'
        }

    except Exception as e:
        error_msg = f"Failed to start research pipeline: {e}"
        print(error_msg)
        return {
            'success': False,
            'error': str(e),
            'message': 'Research pipeline failed to start'
        }


@super_researcher_router.post("/delete-leads/", response=dict, auth=django_auth)
def delete_lead(request, id: int):
    """Delete a Super Researcher lead.

    Args:
        request: Django request object.
        id: Primary key of the lead to delete.

    Returns:
        dict: Dictionary containing success status and message.

    Authentication:
        Requires valid Django session authentication.
    """
    try:
        lead = SuperResearcher.objects.get(id=id)
        lead.delete()
        return {"success": True, "message": f"Lead with id {id} deleted successfully."}
    except SuperResearcher.DoesNotExist:
        return {"success": False, "message": f"Lead with id {id} does not exist."}


@super_researcher_router.get("/list-leads/", response=list[SuperResearcherSchema], auth=django_auth)
def list_leads(request):
    """Retrieve a list of AI-generated leads with filtering.

    This endpoint returns all AI-generated leads with support for
    filtering by lead classification, searching, and sorting.

    Args:
        request: Django request object containing GET parameters.

    Query Parameters:
        lead_class: Optional filter by lead classification.
        search: Optional search term for name, company, email, or phone.
        sort_by: Field to sort by (default: 'full_name').

    Returns:
        list[SuperResearcherSchema]: List of filtered and sorted leads.

    Authentication:
        Requires valid Django session authentication.
    """
    lead_class = request.GET.get('lead_class')
    search_query = request.GET.get('search')
    sort_by = request.GET.get('sort_by', 'full_name')

    leads = SuperResearcher.objects.all()

    if lead_class:
        leads = leads.filter(lead_class=lead_class)

    if search_query:
        leads = leads.filter(
            Q(full_name__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )

    leads = leads.order_by(sort_by)

    return leads

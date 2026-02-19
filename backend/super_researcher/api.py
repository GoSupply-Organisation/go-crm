"""API endpoints for AI-powered lead generation and research.

This module provides Django Ninja API endpoints for the Super Researcher,
including automated lead generation, lead management, and AI-powered research.
"""
import asyncio
from .prompting import question
from .product_engine import run_pipeline
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
            'result',
            'data',
            'created_at',
            'source_url',
        ]


super_researcher_router = Router()


@super_researcher_router.get("/current-leads/", response=SuperResearcherSchema, auth=django_auth)
def get_current_lead(request):
    """Retrieve the most recently generated AI lead.

    This endpoint returns the most recent lead in the database,
    which represents the most recently generated AI lead.

    Args:
        request: Django request object.

    Returns:
        SuperResearcherSchema: The current lead or error message.

    Authentication:
        Requires valid Django session authentication.
    """
    lead = SuperResearcher.objects.order_by('-created_at').first()
    if lead:
        return lead
    else:
        return JsonResponse({"message": "No leads found"})


def periodic_lead_generation(request):
    """Generate AI-powered leads through automated research.

    This endpoint triggers the product-engine research pipeline to discover new leads:
    1. Runs the Celery research task with the default prompt
    2. Executes reliability and urgency analysis
    3. Saves results to Weaviate vector database and SuperResearcher model

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


@super_researcher_router.post("/generate-leads/", response=dict, auth=django_auth)
def generate_leads(request):
    """Generate AI-powered leads through automated research and save to database.

    This endpoint triggers the product-engine research pipeline:
    1. Runs reliability and urgency analysis via web search
    2. Saves scraped results to SuperResearcher model with JSONField
    3. Returns count of leads generated

    Args:
        request: Django request object.

    Returns:
        dict: Dictionary containing success status, leads count, and message
              or error details if generation fails.

    Authentication:
        Requires valid Django session authentication.
    """

    try:
        # Run the pipeline with the default search query
        result = asyncio.run(run_pipeline(question))

        # Extract urgency output (contains the main data to save)
        urgency_output = result.get('urgency', [])
        reliability_output = result.get('reliability', {})

        # Map reliability scores to URLs for easy lookup
        reliability_map = {
            r_item['url']: r_item['score']
            for r_item in reliability_output.get('rankings', [])
        }

        # Save each result as a SuperResearcher lead
        leads_created = 0
        leads_updated = 0

        for item in urgency_output:
            url = item.get('url')
            urgency_score = item.get('urgency_score', 0)
            reliability_score = reliability_map.get(url, 0)

            # Check if lead already exists by source_url
            existing_lead = SuperResearcher.objects.filter(source_url=url).first()

            # Prepare combined data as JSON
            data = {
                'title': item.get('title', 'No Title'),
                'snippet': item.get('snippet', ''),
                'date': item.get('date', 'N/A'),
                'urgency_score': urgency_score,
                'reliability_score': reliability_score,
                'top_urgency_indicators': item.get('top_urgency_indicators', []),
                'search_query': result.get('search_query', question),
            }

            if existing_lead:
                # Update existing lead with new research data
                existing_lead.data = data
                existing_lead.save()
                leads_updated += 1
            else:
                # Determine result type based on content
                result_type = 'company'  # Default to company

                # Create new lead
                SuperResearcher.objects.create(
                    result=result_type,
                    data=data,
                    source_url=url,
                )
                leads_created += 1

        return {
            'success': True,
            'leads_created': leads_created,
            'leads_updated': leads_updated,
            'total_leads': leads_created + leads_updated,
            'message': f'Successfully generated {leads_created} new leads and updated {leads_updated} existing leads.'
        }

    except Exception as e:
        error_msg = f"Failed to generate leads: {e}"
        print(error_msg)
        return {
            'success': False,
            'error': str(e),
            'message': 'Lead generation failed'
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
    filtering by result type and searching in the data JSONField.

    Args:
        request: Django request object containing GET parameters.

    Query Parameters:
        result: Optional filter by result type (contact/company).
        search: Optional search term for title, url, or snippet in data.
        sort_by: Field to sort by (default: '-created_at').

    Returns:
        list[SuperResearcherSchema]: List of filtered and sorted leads.

    Authentication:
        Requires valid Django session authentication.
    """
    result_type = request.GET.get('result')
    search_query = request.GET.get('search')
    sort_by = request.GET.get('sort_by', '-created_at')

    leads = SuperResearcher.objects.all()

    if result_type:
        leads = leads.filter(result=result_type)

    if search_query:
        leads = leads.filter(
            Q(data__title__icontains=search_query) |
            Q(data__snippet__icontains=search_query) |
            Q(source_url__icontains=search_query)
        )

    leads = leads.order_by(sort_by)

    return leads

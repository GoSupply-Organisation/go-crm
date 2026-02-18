
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import SuperResearcher
from django.http import JsonResponse
from django.shortcuts import render
from .tasks import product_engine_research
from django.shortcuts import get_object_or_404

def get_super_researcher_contacts(request):
    """Retrieves all Super Researcher contacts.
    
    Fetches all Super Researcher contacts regardless of promotion status
    and returns them as JSON data for display or processing.
    
    Args:
        request: Django request object. Both POST and GET requests are processed.
    
    Returns:
        JsonResponse: JSON containing 'super_contacts' list with contact data.
    """
    if request.method == "POST" or request.method == "GET":
        super_contacts = SuperResearcher.objects.all()
        return JsonResponse({'super_contacts': list(super_contacts.values())})

@require_POST
@csrf_exempt
def generate_ai_leads(request):
    """
    Trigger AI lead generation via Celery task.
    Returns JSON response with task status.
    """
    try:
        # Start the Celery task
        task = product_engine_research.delay()

        return JsonResponse({
            'success': True,
            'task_id': task.id,
            'message': 'AI research pipeline started successfully',
            'status': 'processing'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to start AI research pipeline'
        }, status=500)
    

def add_super_researcher_contact(request):
    """Creates a new Super Researcher contact.
    
    Processes form data to create a new Super Researcher contact with company,
    website, phone number, email, and full name. Sets promoted flag to False.
    
    Args:
        request: Django request object containing form data on POST.
    
    Returns:
        HttpResponse: Renders add_super.html with success message on POST,
                     or renders the form on GET.
    """
    if request.method == "POST":
        company = request.POST.get("company")
        website = request.POST.get("website")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        full_name = request.POST.get("full_name")

        super_contact = SuperResearcher.objects.create(
            company=company,
            website=website,
            phone_number=phone_number,
            email=email,
            full_name=full_name,
            promoted=False
        )
        return render(request, "add_super.html", {'success': True, 'message': 'Super Researcher contact added successfully'})
    else:
        return render(request, "add_super.html")
    

def promote_super_researcher_contact(request, contact_id):
    """Marks a Super Researcher contact as promoted.
    
    Updates the 'promoted' flag of a Super Researcher contact to True,
    indicating it has been moved to the next stage in the lead pipeline.
    
    Args:
        request: Django request object. Only POST requests are processed.
        contact_id: Primary key of the SuperResearcher contact to promote.
    
    Returns:
        JsonResponse: Success status and message indicating if the promotion
                     was successful or if an error occurred.
    """
    if request.method == "POST":
        contact = get_object_or_404(SuperResearcher, pk=contact_id)
        if contact == None:
            return JsonResponse({'success': False, 'error': 'Contact not found'})
        if contact:
            contact.promoted = True
            contact.save()
            return JsonResponse({'success': True, 'message': 'Contact promoted successfully'})
    
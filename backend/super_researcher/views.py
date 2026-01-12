
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import SuperResearcher
from django.http import JsonResponse
from django.shortcuts import render
from .tasks import run_researcher
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
        # Parse request body for custom prompt (optional)
        try:
            data = json.loads(request.body)
            custom_prompt = data.get('prompt', None)
        except (json.JSONDecodeError, AttributeError):
            custom_prompt = None

        # Default research prompt
        default_prompt = """
        Find high-quality B2B leads for a sales CRM system. Look for:
        1. Company name and website
        2. Contact person (full name)
        3. Email address
        4. Phone number
        5. Physical address

        Format each lead as a separate block with clear field labels:
        Company: [company name]
        Website: [website URL]
        Contact: [full name]
        Email: [email address]
        Phone: [phone number]
        Address: [full address]

        Find 5-10 high-quality leads from various industries.
        """

        # Use custom prompt if provided, otherwise use default
        research_prompt = custom_prompt if custom_prompt else default_prompt

        # Start the Celery task
        task = run_researcher.delay(research_prompt)

        return JsonResponse({
            'success': True,
            'task_id': task.id,
            'message': 'AI lead generation started successfully',
            'status': 'processing'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to start AI lead generation'
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
    
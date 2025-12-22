
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import SuperResearcher
from django.http import JsonResponse
from .tasks import run_researcher

def return_ai_researcher(request):
    if request.method == 'GET':
        leads = SuperResearcher.objects.all()
        if leads.exists():
            return JsonResponse({
                'status': 'success',
                'data': [
                    {
                        'company': lead.company,
                        'website': lead.website,
                        'phone_number': lead.phone_number,
                        'email': lead.email,
                        'full_name': lead.full_name,
                        'address': lead.address,
                        'promoted': lead.promoted,
                        'is_active_lead': lead.is_active_lead,
                        'lead_class': lead.lead_class,
                        'notes': lead.notes,
                    } for lead in leads
                ]
            })

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
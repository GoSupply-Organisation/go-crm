from ninja import ModelSchema, Router, Schema
from ninja.security import django_auth  
from .models import SuperResearcher
from openai import OpenAI
import json
from .engine.prompting import prompt, structure_prompt
from decouple import config
from .tasks import run_researcher
from django.http import JsonResponse
from django.db.models import Q

class SuperResearcherSchema(ModelSchema):
    class Meta:
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
def get_current_lead():
    if lead:
        lead = SuperResearcher.objects.all().first()
    else: return JsonResponse({"message": "No leads found"})
    return lead

@super_researcher_router.get("/generate-leads/", response=list[SuperResearcherSchema], auth=django_auth)
def periodic_lead_generation():
    """
    Periodic task that automatically generates AI leads every 5 minutes.
    This task is designed to run without external arguments.
    """
    client = OpenAI(api_key=config("OPENAI_API_KEY"))
    model = "gpt-5-nano"  # Correct model name
    print("Starting periodic AI lead generation...")

    try:
        # Step 1: Run the research task with the default prompt
        research_result = run_researcher(prompt)

        if research_result['return_code'] != 0:
            error_msg = f"Research failed: {research_result['stderr']}"
            print(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'message': 'Research step failed'
            }

        # Step 2: Use GPT to structure the data
        structured_response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": structure_prompt},
                {"role": "user", "content": research_result['stdout']}
            ],
            response_format={"type": "json_object"}
        )

        # Step 3: Parse the JSON response
        lead_data = json.loads(structured_response.choices[0].message.content)

        # Step 4: Save to database
        lead = SuperResearcher.objects.create(
            company=lead_data.get('company'),
            website=lead_data.get('website'),
            phone_number=lead_data.get('phone_number'),
            email=lead_data.get('email'),
            full_name=lead_data.get('full_name'),
            promoted=lead_data.get('promoted', False),
            is_active_lead=lead_data.get('is_active_lead', False),
            lead_class=lead_data.get('lead_class', 'New'),
            notes=lead_data.get('notes'),
            address=lead_data.get('address')
        )

        print(f"Successfully created lead: {lead.company}")
        return {
            'success': True,
            'lead_id': lead.id,
            'company': lead.company,
            'message': 'Lead generated and saved successfully'
        }

    except Exception as e:
        error_msg = f"Failed to start periodic lead generation: {e}"
        print(error_msg)
        return {
            'success': False,
            'error': str(e),
            'message': 'Periodic lead generation failed'
        }

@super_researcher_router.post("/delete-leads/", response=dict, auth=django_auth)
def delete_lead(id: int):
    try:
        lead = SuperResearcher.objects.get(id=id)
        lead.delete()
        return {"success": True, "message": f"Lead with id {id} deleted successfully."}
    except SuperResearcher.DoesNotExist:
        return {"success": False, "message": f"Lead with id {id} does not exist."}

@super_researcher_router.post("/update-leads/", response=SuperResearcherSchema, auth=django_auth)
def contact_list(request):
    lead_class = request.GET.get('lead_class')
    search_query = request.GET.get('search')
    sort_by = request.GET.get('sort_by', 'Full_name')

    leads = SuperResearcher.objects.all()

    if lead_class:
        leads = leads.filter(lead_class=lead_class)

    if search_query:
        leads = leads.filter(
            Q(Full_name__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )

    leads = leads.order_by(sort_by)

    return leads
from django.shortcuts import render
from .scrap import main
from .models import apex_research
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
# Create your views here.


def apex_home(request):
    tenders = main()
    context = {
        'tenders': tenders
    }
    return render(request, 'apex/apex_home.html', context)


def promote_apex_research_contact(request, contact_id):
    """Marks an Apex Research contact as promoted.
    
    Updates the 'promoted' flag of an Apex Research contact to True,
    indicating it has been moved to the next stage in the lead pipeline.
    
    Args:
        request: Django request object. Only POST requests are processed.
        contact_id: Primary key of the apex_research contact to promote.
    
    Returns:
        JsonResponse: Success status and message indicating if the promotion
                     was successful or if an error occurred.
    """
    if request.method == "POST":
        contact = get_object_or_404(apex_research, pk=contact_id)
        if contact == None:
            return JsonResponse({'success': False, 'error': 'Contact not found'})
        if contact:
            contact.promoted = True
            contact.save()
            return JsonResponse({'success': True, 'message': 'Contact promoted successfully'})



def add_apex_research_contact(request):
    """Creates a new Apex Research contact.
    
    Processes form data to create a new Apex Research contact with company,
    website, phone number, email, and full name. Sets promoted flag to False.
    
    Args:
        request: Django request object containing form data on POST.
    
    Returns:
        HttpResponse: Renders add_apex.html with success message on POST,
                     or renders the form on GET.
    """
    if request.method == "POST":
        company = request.POST.get("company")
        website = request.POST.get("website")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        full_name = request.POST.get("full_name")

        apex_contact = apex_research.objects.create(
            company=company,
            website=website,
            phone_number=phone_number,
            email=email,
            full_name=full_name,
            promoted=False
        )
        return render(request, "add_apex.html", {'success': True, 'message': 'Apex Research contact added successfully'})
    else:
        return render(request, "add_apex.html")


def get_apex_research_contacts(request):
    """Retrieves all non-promoted Apex Research contacts.
    
    Fetches all Apex Research contacts that have not been marked as promoted
    and returns them as JSON data for display or processing.
    
    Args:
        request: Django request object. Both POST and GET requests are processed.
    
    Returns:
        JsonResponse: JSON containing 'apex_contacts' list with contact data.
    """
    if request.method == "POST" or request.method == "GET":
        apex_contacts = apex_research.objects.filter(promoted=False)
        return JsonResponse({'apex_contacts': list(apex_contacts.values())})

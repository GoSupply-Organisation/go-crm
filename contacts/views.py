from django.core.mail import send_mail
from django.http import JsonResponse

from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404   
from .models import Contact, EnquiryLog
from .forms import ContactForm
from django.template.loader import get_template
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
# Create your views here.

# Renders the main index page with a list of the contacts
def index_func(request):
    contacts = Contact.objects.all()
    return render(request, 'index.html', {'contacts': contacts})

# Get more info about a specific contact like as seen below
def more_info(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id)
    
    if request.method == 'POST':
        # Handle the inline editing form submission
        contact.Full_name = request.POST.get('Full_name', contact.Full_name)
        contact.email = request.POST.get('email', contact.email)
        contact.lead_class = request.POST.get('lead_class', contact.lead_class)
        contact.phone_number = request.POST.get('phone_number', contact.phone_number)
        contact.address = request.POST.get('address', contact.address)
        contact.company = request.POST.get('company', contact.company)
        contact.notes = request.POST.get('notes', contact.notes)
        
        try:
            contact.save()
            # Return success response for AJAX or redirect
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Contact updated successfully'})
            else:
                return redirect('more_contact_info', contact_id=contact_id)
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'more_contact_info.html', {'contact': contact})

# Manually adding a contact
def adding_contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)  # Don't save to DB yet
            contact.created_at = timezone.now()  # Set current timestamp
            contact.save()  # Now save to DB
            return redirect('/index')  # Replace with your desired URL name
    else:
        form = ContactForm()
    return render(request, 'adding_contact.html', {'form': form})

# Updating an existing contact
def update_contact(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id)
    
    if request.method == "POST":
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact updated successfully!')
            return redirect('/index')  # Redirect back to the main page
    else:
        form = ContactForm(instance=contact)
    
    return render(request, 'update_contact.html', {
        'form': form, 
        'contact': contact
    })

# Deleting a contact
@csrf_protect
def delete_contact(request, contact_id):
    if request.method == 'POST':
        try:
            contact = get_object_or_404(Contact, id=contact_id)
            contact_name = contact.Full_name
            if contact_name == '':
                contact_name = 'Unnamed Contact'
            contact.delete()
            return JsonResponse({'success': True, 'message': f'Contact {contact_name} deleted successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    

def render_email(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id)
    return render(request, "email.html", {'contact': contact})

def email_email(request, contact_id):
    if request.method == "POST":
        try:
            contact = get_object_or_404(Contact, pk=contact_id)
            
            # Validate required fields
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            from_email = request.POST.get('from_email')
            
            if not all([subject, message, from_email]):
                return JsonResponse({
                    'success': False, 
                    'error': 'All fields are required'
                })
            
            # Send email
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[contact.email],
                fail_silently=False,
            )
            return JsonResponse({
                'success': True, 
                'message': 'Email sent successfully'
            })
            
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Email sending error: {str(e)}")
            
            return JsonResponse({
                'success': False, 
                'error': f'Failed to send email: {str(e)}'
            })
    else: 
        return JsonResponse({
            'success': False, 
            'error': 'Invalid request method'
        }) 



    
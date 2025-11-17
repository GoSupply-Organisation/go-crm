from sms import send_sms
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404   
from .models import Contact, sent_emails, sent_sms
from .forms import ContactForm
from django.template.loader import get_template
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q


# Create your views here.

def index_func(request):
    # Get parameters with defaults
    lead_class = request.GET.get('lead_class')
    search_query = request.GET.get('search')
    sort_by = request.GET.get('sort_by', 'Full_name')
    
    # Start with all contacts
    contacts = Contact.objects.all()
    
    # FILTERING: Reduce which records we see
    if lead_class:
        contacts = contacts.filter(lead_class=lead_class)
    
    if search_query:
        contacts = contacts.filter(
            Q(Full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    # SORTING: Change order of records (doesn't affect which records)
    contacts = contacts.order_by(sort_by)
    
    # Pass to template
    return render(request, 'index.html', {
        'contacts': contacts,
        'leads': contacts,
        'current_filter': lead_class,
        'search_query': search_query,
        'sort_by': sort_by,
        'lead_classifications': Contact.LEAD_CLASSIFICATIONS
    })

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
    
    return render(request, 'more_contact_info.html', {'contact': contact,
                                                      "LEAD_CLASSIFICATIONS": Contact.LEAD_CLASSIFICATIONS,
                                                      'send_emails': sent_emails.objects.filter(contact=contact).order_by('-sent_at')})

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
# in prod move this to the actual company number and move it to Mailgun
    if request.method == "POST":
        try:
            contact = get_object_or_404(Contact, pk=contact_id)
            recip_email = contact.email
            
            # Validate required fields
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            from_email = recip_email
            
            if not all([subject, message]):
                return JsonResponse({
                    'success': False, 
                    'error': 'Subject and message are required'
                })
            
            # Send email
            sent = send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[contact.email],
                fail_silently=False,
            )

            emails = sent_emails.objects.create(
                contact=contact,
                subject=subject,
                message=message,
                sent_at=timezone.now(),
                from_email=from_email,
                sent_by=request.user if request.user.is_authenticated else None
            )
            if sent == True: 
                print("Email sent successfully")
                print("Shifting from new to Contacted")
                up_dog = contact.lead_class
                if up_dog == "New":
                    contact.lead_class = "Contacted"
                    contact.save()
            # No need to call emails.save() after objects.create()
            print("Saved the sent email to the database")

            return JsonResponse({
                'success': True, 
                'message': 'Text sent successfully',
                'redirect': '/index'  # Include redirect URL in the JSON response
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

def render_sms(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id)
    return render(request, "message.html", {'contact': contact})

def sms_sms(request, contact_id):
    company_number = "0424854899"
    contact = get_object_or_404(Contact, pk=contact_id)
    
    if request.method == 'POST':
        try:
            recip_number = contact.phone_number
            body = request.POST.get('body')
            sent_at = timezone.now()
            
            if not all([body, recip_number]):
                return JsonResponse({
                    'success': False, 
                    'error': 'Need body and number'
                })
                
            sms = send_sms(
                body=body,
                originator=company_number,
                recipients=[recip_number]
            )

            sms_record = sent_sms.objects.create(
                contact=contact,
                body=body,
                sent_at=sent_at
            )
            
            if sms:
                print("SMS sent successfully")
                print("Shifting from new to Contacted")
                up_dog = contact.lead_class
                if up_dog == "New":
                    contact.lead_class = "Contacted"
                    contact.save()
            
            print("Saved the sent SMS to the database")
            return JsonResponse({
                'success': True, 
                'message': 'Text sent successfully',
                'redirect': '/index'
            })

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"SMS sending error: {str(e)}")
            
            return JsonResponse({
                'success': False, 
                'error': f'Failed to send SMS: {str(e)}'
            })
    
    else:  # Handle GET request
        return render(request, "message.html", {'contact': contact})
    

def ahhh(request):
    # Cant think of a better name right now
    # This just returns all the sent messages for the page
    emails = sent_emails.objects.all().order_by('-sent_at')  # Order by most recent first
    # The key in the context dictionary must match the variable name in the template
    return render(request, 'index.html', {'emails': emails})



def contact_detail(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id)
    sent_emails = sent_emails.objects.filter(contact=contact).order_by('-sent_at')
    
    if request.method == 'POST':
        # Handle form submission
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Contact updated successfully'})
            return redirect('contact_detail', contact_id=contact.id)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': form.errors})
    else:
        form = ContactForm(instance=contact)
    
    context = {
        'contact': contact,
        'sent_emails': sent_emails,
        'form': form,
    }
    return render(request, 'contact_detail.html', context)
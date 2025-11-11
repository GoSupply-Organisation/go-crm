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

# Main page
def index_func(request):
    contacts = Contact.objects.all()
    return render(request, 'index.html', {'contacts': contacts})

def inquire(request, contact_id):
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
                return redirect('inquire_contact', contact_id=contact_id)
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'more_contact_info.html', {'contact': contact})

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
    

def enquire_contact(request, contact_id):
    contact = Contact.objects.get(id=contact_id)
    return render(request, 'enquire.html', {'contact': contact})

def send_enquiry(request):
    if request.method == 'POST':
        try:
            contact_id = request.POST.get('contact_id')
            enquiry_type = request.POST.get('enquiry_type')
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            custom_message = request.POST.get('custom_message', '')
            send_email_flag = request.POST.get('send_email') == 'on'
            send_sms_flag = request.POST.get('send_sms') == 'on'
            
            contact = Contact.objects.get(id=contact_id)
            
            # Combine the main message with custom message
            full_message = message
            if custom_message:
                full_message += f"\n\nAdditional Notes:\n{custom_message}"
            
            results = {
                'email_sent': False,
                'sms_sent': False
            }
            
            # Send email
            if send_email_flag and contact.email:
                try:
                    send_mail(
                        subject,
                        full_message,
                        'noreply@yourcompany.com',  # Update with your email
                        [contact.email],
                        fail_silently=False,
                    )
                    results['email_sent'] = True
                except Exception as e:
                    return JsonResponse({'success': False, 'error': f'Email sending failed: {str(e)}'})
            
            # Send SMS (you'll need to integrate with an SMS service like Twilio)
            if send_sms_flag and contact.phone_number:
                try:
                    # Example with Twilio (you'll need to install twilio package)
                    # from twilio.rest import Client
                    # client = Client(account_sid, auth_token)
                    # message = client.messages.create(
                    #     body=full_message,
                    #     from_='+1234567890',
                    #     to=contact.phone
                    # )
                    # results['sms_sent'] = True
                    
                    # For now, we'll just log it since SMS integration requires external service
                    print(f"SMS would be sent to {contact.phone_number}: {full_message}")
                    results['sms_sent'] = True
                    
                except Exception as e:
                    return JsonResponse({'success': False, 'error': f'SMS sending failed: {str(e)}'})
            
            # Log the enquiry
            EnquiryLog.objects.create(
                contact=contact,
                enquiry_type=enquiry_type,
                subject=subject,
                message=full_message,
                email_sent=results['email_sent'],
                sms_sent=results['sms_sent']
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Enquiry sent successfully! Email: {"Yes" if results["email_sent"] else "No"}, SMS: {"Yes" if results["sms_sent"] else "No"}'
            })
            
        except Contact.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Contact not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
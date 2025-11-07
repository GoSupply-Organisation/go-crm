from django.shortcuts import render, redirect, get_object_or_404   
from .models import Contact
from django.template.loader import get_template
# Create your views here.

# Gives you the list of all contacts will intergrate this into the main e-com main

def contact_list(request):
    try:
        template = get_template('base.html')
        print("✅ FOUND: base.html")
    except Exception as e:
        print("❌ NOT FOUND: base.html", e)

    contacts = Contact.objects.all()
    return render(request, 'contacts/contact_list.html', {'contacts': contacts})

# Creates contacts will add more features as we go on
def contact_create(request):
    if request.method == "POST":
        contact = Contact(
        first_name = request.POST.get('first_name'),  # ✅ USE PARENTHESES
        last_name = request.POST.get('last_name'),
        email = request.POST.get('email'),
        phone = request.POST.get('phone'))
        contact.save
        return redirect('contact_list')
    return render(request, 'contacts/contact_create.html')

# Updates the contacts on our end
def contact_update(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == "POST":
        contact.first_name = request.POST.get['first_name']
        contact.last_name = request.POST.get['last_name']
        contact.email = request.POST.get['email']
        contact.phone = request.POST.get['phone']
        contact.save()
        return redirect('contact_list')
    return render(request, 'contacts/contact_update.html', {'contact': contact})


# Deletes contacts from our database    
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == "POST":
        contact.delete()
        return redirect('contact_list')
    return render(request, 'contacts/contact_delete.html', {'contact': contact})    
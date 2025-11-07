from django.shortcuts import render, redirect, get_object_or_404   
from .models import Contact
# Create your views here.


def contact_list(request):
    contacts = Contact.objects.all()
    return render(request, 'contacts/contact_list.html', {'contacts': contacts})


def contact_create(request):
    if request.method == "POST":
        contact = Contact(
        first_name = request.POST.get['first_name'],
        last_name = request.POST.get['last_name'],
        email = request.POST.get['email'],
        phone = request.POST.get['phone'])
        contact.save
        return redirect('contact_list')
    return render(request, 'contacts/contact_form.html')


def contact_update(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == "POST":
        contact.first_name = request.POST.get['first_name']
        contact.last_name = request.POST.get['last_name']
        contact.email = request.POST.get['email']
        contact.phone = request.POST.get['phone']
        contact.save()
        return redirect('contact_list')
    return render(request, 'contacts/contact_form.html', {'contact': contact})
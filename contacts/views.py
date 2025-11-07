from django.shortcuts import render, redirect, get_object_or_404   
from .models import Contact
from .forms import ContactForm
from django.template.loader import get_template
# Create your views here.

# Main page
def index(request):
    contacts = Contact.objects.all()
    return render(request, 'index.html', {'contacts': contacts})


def adding_contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('')
    else:
        form = ContactForm()
    return render(request, 'adding_contact.html', {'form': form})
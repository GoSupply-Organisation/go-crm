from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['Full_name', 'lead_class', 'email', 'phone_number', "notes", "address", "company"]
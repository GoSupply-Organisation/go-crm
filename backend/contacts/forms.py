from django import forms
from .models import Contact
from apex.models import apex_research
from super_researcher.models import SuperResearcher
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['Full_name', "company", 'lead_class', 'email', 'phone_number', "notes", "address", ]


class ApexForm(forms.ModelForm):
    class Meta:
        model = apex_research
        fields = ["company", "website", "phone_number", "email", "full_name", "promoted"]

class SuperResearcherForm(forms.ModelForm):
    class Meta:
        model = SuperResearcher
        fields = ["company", "website", "phone_number", "email", "full_name", "promoted"]
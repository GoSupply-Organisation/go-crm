# forms.py
from django import forms
from .models import Todo

class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'description', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'What needs to be done?',
                'id': 'id_title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Add details, notes, or context...',
                'id': 'id_description'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-input',
                'id': 'id_priority'
            }),
        }
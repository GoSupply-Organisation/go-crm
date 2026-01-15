# models.py
from django.db import models
from user.models import CustomUser

class Todo(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.title
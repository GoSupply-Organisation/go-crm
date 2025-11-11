from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    Full_name = models.CharField(max_length=60)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-set on creation
        # New classification field with predefined choices
    LEAD_CLASSIFICATIONS = [
        ('New', 'New Lead'),
        ('Growing Interest', 'Growing Interest'),
        ('Leading', 'Leading'),
        ('Dying', 'Dying'),
        ('Converted', 'Converted'),
        ('Cold', 'Cold'),
    ]
    lead_class = models.CharField(
        max_length=20,
        choices=LEAD_CLASSIFICATIONS,
        default='new',
        blank=True,
        null=True,
    )
    notes = models.CharField(max_length=500, blank=True)
    address = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=100, blank=True)

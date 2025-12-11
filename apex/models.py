from django.db import models

# Create your models here.
class apex_research(models.Model):
    company = models.CharField(max_length=200,null= True)
    website = models.URLField(max_length=200, null= True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=200, null= True)
    full_name = models.CharField(max_length=200, null= True)
    promoted = models.BooleanField(default=False)
    is_active_lead = models.BooleanField(default=False)
    LEAD_CLASSIFICATIONS = [
        ('New', 'New Lead'),
        ('Contacted', 'Contacted'),
        ('Growing Interest', 'Growing Interest'),
        ('Leading', 'Leading'),
        ('Dying', 'Dying'),
        ('Converted', 'Converted'),
        ('Cold', 'Cold'),
    ]
    lead_class = models.CharField(
        max_length=20,
        choices=LEAD_CLASSIFICATIONS,
        default='New',
    )

    notes = models.CharField(max_length=500, blank=True)
    address = models.CharField(max_length=200, blank=True)

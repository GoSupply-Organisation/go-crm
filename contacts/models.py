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



class EnquiryLog(models.Model):
    ENQUIRY_TYPES = [
        ('product_info', 'Product Information'),
        ('pricing', 'Pricing Inquiry'),
        ('demo', 'Request Demo'),
        ('support', 'Technical Support'),
        ('partnership', 'Partnership Opportunity'),
        ('custom', 'Custom Message'),
    ]
    
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    enquiry_type = models.CharField(max_length=20, choices=ENQUIRY_TYPES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Enquiry for {self.contact.Full_name} - {self.get_enquiry_type_display()}"
from django.db import models
from user.models import CustomUser
from apex.models import apex_research
from super_researcher.models import SuperResearcher
# Create your models here.
class Contact(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    Full_name = models.CharField(max_length=60, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-set on creation
        # New classification field with predefined choices
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
    company = models.CharField(max_length=100, blank=True)


class sent_emails(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.CharField(null=True, blank=True, max_length=2000)
    sent_at = models.DateTimeField(auto_now_add=True)
    from_email = models.EmailField(null=True, blank=True) 
    sent_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True) 

    def __str__(self):
        return f"Email to {self.contact.Full_name} on {self.sent_at.strftime('%Y-%m-%d %H:%M:%S')}"


class sent_sms(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    body = models.CharField(max_length=2000, blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def str__(self):
        return f"SMS to {self.send_to.Full_name} on {self.sent_at.strftime('%Y-%m-%d %H:%M:%S')}"
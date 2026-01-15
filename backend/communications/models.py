from django.db import models
from user.models import CustomUser
from contacts.models import Contact
# Create your models here.
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
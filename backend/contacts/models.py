"""Contact management models for Go CRM.

This module defines the Contact model which represents customer and lead
information in the CRM system. Contacts are linked to users and can be
classified by their stage in the sales funnel.
"""

from django.db import models
from user.models import CustomUser

# Create your models here.


class Contact(models.Model):
    """Model representing a contact or lead in the CRM system.

    A Contact contains information about a potential or existing customer
    including their contact details, company information, and current
    lead classification status. Contacts can be associated with a
    CustomUser for ownership tracking.

    Attributes:
        user: The user who owns this contact. Can be null for unassigned contacts.
        Full_name: The full name of the contact person.
        email: Unique email address for the contact.
        phone_number: Optional phone number for the contact.
        created_at: Timestamp when the contact was created.
        lead_class: Current classification of the lead in the sales funnel.
        notes: Optional notes about the contact.
        address: Optional physical address.
        company: Optional company or organization name.

    LEAD_CLASSIFICATIONS:
        Predefined choices for lead classification stages:
        - New: Newly created lead, not yet contacted
        - Contacted: Initial contact has been made
        - Growing Interest: Lead showing increased engagement
        - Leading: High-priority lead close to conversion
        - Dying: Lead losing interest or engagement
        - Converted: Successfully converted to customer
        - Cold: Inactive or unresponsive lead
    """

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

    def __str__(self):
        """Return string representation of the contact.

        Returns:
            str: The full name of the contact, or email if name is not set.
        """
        return self.Full_name if self.Full_name else self.email

    class Meta:
        """Meta options for Contact model.

        Attributes:
            ordering: Default ordering for queries by creation date.
        """
        ordering = ['-created_at']

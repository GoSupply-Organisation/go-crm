"""Super Researcher models for AI-powered lead generation.

This module defines the SuperResearcher model which represents AI-generated
leads and research results. These leads are created through automated
research processes and can be tracked through the sales pipeline.
"""

from django.db import models

# Create your models here.


class SuperResearcher(models.Model):
    """Model representing AI-generated leads and research results.

    A SuperResearcher record contains information about a company or lead
    that was discovered or enriched through the AI-powered research process.
    This model tracks the lead's company details, contact information, and
    current status in the sales funnel.

    Attributes:
        company: Name of the company.
        website: Company website URL.
        phone_number: Contact phone number.
        email: Contact email address.
        full_name: Name of the contact person.
        promoted: Whether this lead has been promoted to main contacts.
        is_active_lead: Whether this is an active lead being pursued.
        lead_class: Current classification in the sales funnel.
        notes: Additional notes about the lead.
        address: Physical address.

    LEAD_CLASSIFICATIONS:
        Predefined choices for lead classification stages:
        - New: Newly generated AI lead
        - Contacted: Initial contact has been made
        - Growing Interest: Lead showing increased engagement
        - Leading: High-priority lead close to conversion
        - Dying: Lead losing interest or engagement
        - Converted: Successfully converted to customer
        - Cold: Inactive or unresponsive lead
    """

    company = models.CharField(max_length=200, null=True)
    website = models.URLField(max_length=200, null=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=200, null=True)
    full_name = models.CharField(max_length=200, null=True)
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

    def __str__(self):
        """Return string representation of the lead.

        Returns:
            str: The company name, or full name if company not set.
        """
        return self.company if self.company else (self.full_name or 'Unnamed Lead')

    class Meta:
        """Meta options for SuperResearcher model.

        Attributes:
            ordering: Default ordering for queries by lead classification.
        """
        ordering = ['-lead_class', '-created_at']

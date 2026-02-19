"""Super Researcher models for AI-powered lead generation.

This module defines the SuperResearcher model which represents AI-generated
leads and research results. These leads are created through automated
research processes and can be tracked through the sales pipeline.
"""

from django.db import models

# Create your models here.


class SuperResearcher(models.Model):
    RESULT_TYPES = (
        ("contact", "Contact"),
        ("company", "Company"),
    )
    result = models.TextField(choices=RESULT_TYPES)
    data = models.JSONField(default = dict)
    created_at = models.DateTimeField(auto_now_add=True)
    source_url = models.URLField(blank=True) 

    def __str__(self):
        return f"{self.get_result_display()} - {self.id}"
"""Custom user authentication models for Go CRM.

This module defines the CustomUser model which extends Django's AbstractUser
to provide email-based authentication for the CRM system.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom user model extending Django's AbstractUser.

    This model provides email-based authentication by setting the email field
    as the USERNAME_FIELD. All other AbstractUser fields are inherited.

    Attributes:
        email: Unique email address used for authentication (USERNAME_FIELD).
        username: Required field inherited from AbstractUser.
        All other Django AbstractUser fields: first_name, last_name, etc.

    Note:
        - email is the unique identifier for authentication
        - username is still required but can be auto-generated from email
    """

    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        """Return string representation of the user.

        Returns:
            str: The email address of the user.
        """
        return self.email

    class Meta:
        """Meta options for CustomUser model.

        Attributes:
            verbose_name: Human-readable name for the model.
            verbose_name_plural: Human-readable plural name.
        """
        verbose_name = 'User'
        verbose_name_plural = 'Users'

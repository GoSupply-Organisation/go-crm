"""Todo task management models for Go CRM.

This module defines the Todo model which represents tasks and
actionable items in the CRM system. Todos can be prioritized
and tracked for completion.
"""

from django.db import models
from user.models import CustomUser


class Todo(models.Model):
    """Model representing a task or actionable item in the CRM.

    A Todo contains information about a task including its title,
    description, priority level, and completion status. Todos
    are associated with a user who created them.

    Attributes:
        title: Title/name of the todo task.
        description: Detailed description of the task.
        date: Timestamp when the todo was created.
        completed: Whether the task has been completed.
        priority: Priority level of the task (low, medium, high).
        created_by: User who created this todo.

    PRIORITY_CHOICES:
        Predefined choices for priority levels:
        - low: Low priority task
        - medium: Medium priority task (default)
        - high: High priority task
    """

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        """Return string representation of the todo.

        Returns:
            str: The title of the todo task.
        """
        return self.title

    class Meta:
        """Meta options for Todo model.

        Attributes:
            ordering: Default ordering for queries by date (newest first).
        """
        ordering = ['-date']

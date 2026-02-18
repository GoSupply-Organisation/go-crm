"""API endpoints for todo task management.

This module provides Django Ninja API endpoints for creating, reading,
updating, and deleting todos. It includes filtering, statistics,
and completion tracking.
"""

from ninja import NinjaAPI, ModelSchema, Router, Schema
from ninja.security import django_auth
from .models import Todo
from django.shortcuts import get_object_or_404
from typing import List, Optional


# Schemas
class TodoSchema(ModelSchema):
    """Schema for Todo model serialization.

    This schema defines which fields are included when serializing
    Todo objects for API responses.
    """

    class Meta:
        """Meta configuration for TodoSchema.

        Attributes:
            model: The Django model to serialize.
            fields: List of fields to include in serialization.
        """
        model = Todo
        fields = [
            'id',
            'title',
            'description',
            'date',
            'completed',
            'priority',
            'created_by',
        ]


class TodoCreateSchema(ModelSchema):
    """Schema for creating new todos.

    This schema validates input data when creating a new todo.
    Excludes id, date, and completed as they are auto-generated.
    """

    class Meta:
        """Meta configuration for TodoCreateSchema.

        Attributes:
            model: The Django model for validation.
            fields: List of fields required for todo creation.
        """
        model = Todo
        fields = [
            'title',
            'description',
            'priority',
        ]


class TodoUpdateSchema(Schema):
    """Schema for updating existing todos.

    This schema allows partial updates to todo fields.
    All fields are optional to support partial updates.
    """

    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None


todo_router = Router()


@todo_router.get("/index", response=List[TodoSchema], auth=django_auth)
def todo_list(request):
    """Retrieve a list of all todos ordered by date.

    This endpoint returns all todos in the system, ordered by
    creation date with the newest first.

    Args:
        request: Django request object.

    Returns:
        List[TodoSchema]: List of all todos ordered by date.

    Authentication:
        Requires valid Django session authentication.
    """
    todos = Todo.objects.order_by("-date")
    return todos


@todo_router.get("/stats", response=dict)
def todo_stats(request):
    """Retrieve todo statistics.

    This endpoint returns summary statistics about todos including
    total count, pending count, and completed count.

    Args:
        request: Django request object.

    Returns:
        dict: Dictionary containing:
            - total: Total number of todos
            - pending: Number of incomplete todos
            - completed: Number of completed todos
    """
    total_count = Todo.objects.count()
    pending_count = Todo.objects.filter(completed=False).count()
    completed_count = Todo.objects.filter(completed=True).count()

    return {
        'total': total_count,
        'pending': pending_count,
        'completed': completed_count
    }


@todo_router.post("/add", response=TodoSchema, auth=django_auth)
def create_todo(request, payload: TodoCreateSchema):
    """Create a new todo task.

    This endpoint creates a new Todo object with the provided data.
    The created_by field is automatically set to the authenticated user.

    Args:
        request: Django request object.
        payload: TodoCreateSchema containing todo data.

    Returns:
        TodoSchema: The created todo object.

    Authentication:
        Requires valid Django session authentication.
    """
    todo = Todo.objects.create(
        title=payload.title,
        description=payload.description or '',
        priority=payload.priority or 'medium',
        created_by=request.auth
    )

    return todo


@todo_router.get("/moreinfo/{todo_id}", response=TodoSchema, auth=django_auth)
def todo_detail(request, todo_id: int):
    """Retrieve detailed information about a specific todo.

    Args:
        request: Django request object.
        todo_id: Primary key of the todo to retrieve.

    Returns:
        TodoSchema: The requested todo object.

    Raises:
        Http404: If no todo with the given ID exists.

    Authentication:
        Requires valid Django session authentication.
    """
    todo = get_object_or_404(Todo, pk=todo_id)
    return todo


@todo_router.post("/update/{todo_id}", response=TodoSchema, auth=django_auth)
def update_todo(request, todo_id: int, payload: TodoUpdateSchema):
    """Update an existing todo.

    This endpoint supports partial updates to todo fields. Only
    provided fields will be updated; others remain unchanged.

    Args:
        request: Django request object.
        todo_id: Primary key of the todo to update.
        payload: TodoUpdateSchema containing updated todo data.

    Returns:
        TodoSchema: The updated todo object.

    Raises:
        HttpError: If todo with given ID does not exist (404).

    Authentication:
        Requires valid Django session authentication.
    """
    try:
        todo = Todo.objects.get(pk=todo_id)
        if payload.title is not None:
            todo.title = payload.title
        if payload.description is not None:
            todo.description = payload.description
        if payload.priority is not None:
            todo.priority = payload.priority
        todo.save()
        return todo
    except Todo.DoesNotExist:
        from ninja.errors import HttpError
        raise HttpError(404, 'Todo not found')


@todo_router.delete("/delete/{todo_id}", response=dict, auth=django_auth)
def delete_todo(request, todo_id: int):
    """Delete a todo task.

    Args:
        request: Django request object.
        todo_id: Primary key of the todo to delete.

    Returns:
        dict: Dictionary containing success status and message.

    Raises:
        HttpError: If deletion fails with error code 500.

    Authentication:
        Requires valid Django session authentication.
    """
    try:
        todo = get_object_or_404(Todo, pk=todo_id)
        todo_title = todo.title if todo.title else 'Unnamed Todo'
        todo.delete()
        return {'success': True, 'message': f'Todo {todo_title} deleted successfully'}
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(500, str(e))


@todo_router.post("/toggle/{todo_id}", response=TodoSchema, auth=django_auth)
def toggle_todo(request, todo_id: int):
    """Toggle the completion status of a todo.

    This endpoint switches the completed status of a todo from
    false to true, or from true to false.

    Args:
        request: Django request object.
        todo_id: Primary key of the todo to toggle.

    Returns:
        TodoSchema: The updated todo object with toggled status.

    Raises:
        HttpError: If operation fails with error code 500.

    Authentication:
        Requires valid Django session authentication.
    """
    try:
        todo = get_object_or_404(Todo, pk=todo_id)
        todo.completed = not todo.completed
        todo.save()
        return todo
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(500, str(e))

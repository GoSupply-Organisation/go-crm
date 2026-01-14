from ninja import NinjaAPI, ModelSchema, Router 
from ninja.security import django_auth
from .models import Todo
from django.shortcuts import get_object_or_404
from typing import List

# Schemas
class TodoSchema(ModelSchema):
    class Meta:
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
    class Meta:
        model = Todo
        fields = [
            'title',
            'description',
            'priority',
        ]

todo_router = Router()


@todo_router.get("/index", response=List[TodoSchema])
def todo_list(request):
    """Get all todos ordered by date (newest first)"""
    todos = Todo.objects.order_by("-date")
    return todos

@todo_router.get("/stats", response=dict)
def todo_stats(request):
    """Get todo statistics (total, pending, completed)"""
    total_count = Todo.objects.count()
    pending_count = Todo.objects.filter(completed=False).count()
    completed_count = Todo.objects.filter(completed=True).count()

    return {
        'total': total_count,
        'pending': pending_count,
        'completed': completed_count
    }

@todo_router.post("/add", response=TodoSchema)
def create_todo(request, payload: TodoCreateSchema):
    """Create a new todo"""
    todo = Todo.objects.create(
        title=payload.title,
        description=payload.description or '',
        priority=payload.priority or 'medium',
        created_by=request.auth
    )

    return todo

@todo_router.get("/moreinfo/{todo_id}", response=TodoSchema)
def todo_detail(request, todo_id: int):
    """Get a single todo by ID"""
    todo = get_object_or_404(Todo, pk=todo_id)
    return todo

@todo_router.post("/update/{todo_id}", response=TodoSchema)
def update_todo(request, todo_id: int, payload: TodoCreateSchema):
    """Update an existing todo"""
    try:
        todo = Todo.objects.get(pk=todo_id)
        todo.title = payload.title
        todo.description = payload.description
        todo.priority = payload.priority
        todo.save()
        return todo
    except Todo.DoesNotExist:
        from ninja.errors import HttpError
        raise HttpError(404, 'Todo not found')

@todo_router.delete("/delete/{todo_id}", response=dict)
def delete_todo(request, todo_id: int):
    """Delete a todo"""
    try:
        todo = get_object_or_404(Todo, pk=todo_id)
        todo_title = todo.title if todo.title else 'Unnamed Todo'
        todo.delete()
        return {'success': True, 'message': f'Todo {todo_title} deleted successfully'}
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(500, str(e))

@todo_router.post("/toggle/{todo_id}", response=TodoSchema)
def toggle_todo(request, todo_id: int):
    """Toggle todo completion status"""
    try:
        todo = get_object_or_404(Todo, pk=todo_id)
        todo.completed = not todo.completed
        todo.save()
        return todo
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(500, str(e))
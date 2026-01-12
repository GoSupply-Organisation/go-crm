# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
import json
import json
from datetime import datetime

from .forms import TodoForm
from .models import Todo

@login_required
def index(request):
    item_list = Todo.objects.order_by("-date")
    
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.created_by = request.user
            todo.save()
            messages.success(request, "Task added successfully!")
            return redirect('todo')
    
    form = TodoForm()
    
    # Calculate stats
    total_count = item_list.count()
    pending_count = item_list.filter(completed=False).count()
    completed_count = item_list.filter(completed=True).count()
    
    page = {
        "forms": form,
        "list": item_list,
        "title": "TODO LIST",
        "total_count": total_count,
        "pending_count": pending_count,
        "completed_count": completed_count,
    }
    return render(request, 'todo/index.html', page)

def remove(request, item_id):
    item = get_object_or_404(Todo, id=item_id)
    item.delete()
    messages.info(request, "Task removed!")
    return redirect('todo')

@require_POST
def toggle_task(request, item_id):
    try:
        item = get_object_or_404(Todo, id=item_id)
        item.completed = not item.completed
        item.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# API Endpoints for frontend integration
@login_required
def get_todos(request):
    """Get all todos as JSON"""
    try:
        todos = Todo.objects.order_by("-date")
        todos_data = []
        for todo in todos:
            todos_data.append({
                'id': todo.id,
                'title': todo.title,
                'description': todo.description,
                'priority': todo.priority,
                'completed': todo.completed,
                'created_at': todo.date.isoformat(),
                'updated_at': todo.date.isoformat(),  # Using date as updated_at for now
            })
        return JsonResponse({'success': True, 'todos': todos_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def create_todo(request):
    """Create a new todo"""
    try:
        data = json.loads(request.body)

        todo = Todo.objects.create(
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', 'medium'),
            created_by=request.user if request.user.is_authenticated else None
        )

        todo_data = {
            'id': todo.id,
            'title': todo.title,
            'description': todo.description,
            'priority': todo.priority,
            'completed': todo.completed,
            'created_at': todo.date.isoformat(),
            'updated_at': todo.date.isoformat(),
        }

        return JsonResponse({'success': True, 'todo': todo_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def update_todo(request, todo_id):
    """Update an existing todo"""
    try:
        todo = get_object_or_404(Todo, id=todo_id)
        data = json.loads(request.body)

        todo.title = data.get('title', todo.title)
        todo.description = data.get('description', todo.description)
        todo.priority = data.get('priority', todo.priority)
        if 'completed' in data:
            todo.completed = data['completed']

        todo.save()

        todo_data = {
            'id': todo.id,
            'title': todo.title,
            'description': todo.description,
            'priority': todo.priority,
            'completed': todo.completed,
            'created_at': todo.date.isoformat(),
            'updated_at': todo.date.isoformat(),
        }

        return JsonResponse({'success': True, 'todo': todo_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def delete_todo_api(request, todo_id):
    """Delete a todo via API"""
    try:
        todo = get_object_or_404(Todo, id=todo_id)
        todo.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_todo_stats(request):
    """Get todo statistics"""
    try:
        total_count = Todo.objects.count()
        pending_count = Todo.objects.filter(completed=False).count()
        completed_count = Todo.objects.filter(completed=True).count()

        return JsonResponse({
            'success': True,
            'stats': {
                'total': total_count,
                'pending': pending_count,
                'completed': completed_count
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
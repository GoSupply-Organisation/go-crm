# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

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
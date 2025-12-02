from django.shortcuts import render
from .models import Task
from django.utils import timezone
from django.http import JsonResponse

# Create your views here.
def add_task(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        created_at = timezone.now()
        created_by = request.user
        task = Task(title=title, description=description, created_at=created_at, created_by=created_by)
        task.save()
        return JsonResponse({"status": "success", "task_id": task.id})



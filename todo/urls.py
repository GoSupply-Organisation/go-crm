from django.urls import path
from .views import *

urlpatterns = [
    path("add_task/", add_task, name="add_task"),
    
]
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="todo"),
    path('del/<str:item_id>', views.remove, name="del"),
    path('toggle-task/<str:item_id>/', views.toggle_task, name="toggle_task"),

    # AJAX Endpoints
    path('get/', views.get_todos, name="get_todos"),
    path('create/', views.create_todo, name="create_todo"),
    path('update/<int:todo_id>/', views.update_todo, name="update_todo"),
    path('delete/<int:todo_id>/', views.delete_todo_api, name="delete_todo_api"),
    path('stats/', views.get_todo_stats, name="get_todo_stats"),
]
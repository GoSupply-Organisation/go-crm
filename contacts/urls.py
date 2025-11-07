from django.urls import path
from .views import *

urlpatterns = [
    path('', contact_list, name='contact_list'),
    path('create/', contact_create, name='contact_create'),
    path('update/<int:pk>/', contact_update, name='contact_update'),
    path('delete/<int:pk>/', contact_delete, name='contact_delete'),
]
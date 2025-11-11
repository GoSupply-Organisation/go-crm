from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='home'),
    path('add/', adding_contact, name='adding_contact'),
    path('update/<int:contact_id>/', update_contact, name='update_contact'),  # Added contact_id parameter
    path('delete/<int:contact_id>/', delete_contact, name='delete_contact'),  # Added contact_id parameter
]
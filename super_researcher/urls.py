from django.urls import path
from . import views

app_name = 'super_researcher'

urlpatterns = [
    path('ai-leads/', views.return_ai_researcher, name='ai_leads'),
    path('generate-leads/', views.generate_ai_leads, name='generate_ai_leads'),
]
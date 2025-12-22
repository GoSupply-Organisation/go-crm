from django.urls import path
from . import views

urlpatterns = [
    path('apex_test/', views.promote_apex_research_contact, name='apex_test_'),
    path("add_apex/", views.add_apex_research_contact, name="add_apex"),
    path("render-apex/", views.get_apex_research_contacts, name="render_apex"),]
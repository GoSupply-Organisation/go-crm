from django.urls import path
from .views import *

urlpatterns = [
    path('index/', index_func, name='home'),
    path('add/', adding_contact, name='adding_contact'),
    path('update/<int:contact_id>/', update_contact, name='update_contact'),  # Added contact_id parameter
    path('delete/<int:contact_id>/', delete_contact, name='delete_contact'),  # Added contact_id parameter
    path('moreinfo/<int:contact_id>/', more_info, name='moreinfo_contact'),
    path('email/<int:contact_id>/', render_email, name='render_email'),
    path('send-email/<int:contact_id>/', email_email, name='email_email'),
    path('already_sent_emails/', ahhh, name='already_sent_emails'),
    path('contact/<int:contact_id>/', contact_detail, name='api_contact_detail'),

]
from django.urls import path
from .views import *

urlpatterns = [
    # Renders the index page with the list of contacts
    path('index/', index_func, name='home'),

    # Paths for adding, updating, deleting, and viewing more info about contacts
    path('add/', adding_contact, name='adding_contact'),

    # Updates to include update contact by id
    path('update/<int:contact_id>/', update_contact, name='update_contact'),  # Added contact_id parameter

    # Delete contact by id
    path('delete/<int:contact_id>/', delete_contact, name='delete_contact'),  # Added contact_id parameter

    # More info about contact by id
    path('moreinfo/<int:contact_id>/', more_info, name='moreinfo_contact'),
    
    # Not entirely sure
    path('contact/<int:contact_id>/', contact_detail, name='api_contact_detail'),

    # Renders and allows emails to be sent
    path('email/<int:contact_id>/', render_email, name='render_email'),
    path('send-email/<int:contact_id>/', email_email, name='email_email'),
    path('already_sent_emails/', ahhh, name='already_sent_emails'),

    # Renders and allows SMS to be sent
    path('email/<int:contact_id>/', render_sms, name='render_email'),
    path("send-sms/<int:contact_id>/", sms_sms, name="send_sms"),

    

]
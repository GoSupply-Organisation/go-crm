from django.urls import path
from .views import *

urlpatterns = [
    # Renders the index page with the list of contacts
    path('index/', contact_list_view, name='home'),

    # Paths for adding, updating, deleting, and viewing more info about contacts
    path('add/', create_contact_view, name='adding_contact'),

    # Updates to include update contact by id
    path('update/<int:contact_id>/', edit_contact_view, name='update_contact'),

    # Delete contact by id
    path('delete/<int:contact_id>/', delete_contact_view, name='delete_contact'),

    # More info about contact by id
    path('moreinfo/<int:contact_id>/', contact_detail_view, name='moreinfo_contact'),
    
    # Displays detailed contact information and handles quick edit
    path('contact/<int:contact_id>/', contact_detail_form_view, name='api_contact_detail'),

    # Renders and allows emails to be sent
    path('email/<int:contact_id>/', compose_email_view, name='render_email'),
    path('send-email/<int:contact_id>/', send_email_view, name='email_email'),
    path('already_sent_emails/', sent_emails_history_view, name='already_sent_emails'),

    # Renders and allows SMS to be sent
    path('email/<int:contact_id>/', compose_sms_view, name='render_sms'),
    path('send-sms/<int:contact_id>/', send_sms_message_view, name='send_sms'),


    # Tracks communication logs
    path("reachout/", get_communication_logs, name="reachout"),

    # Promote Apex and Super contacts with ID

    # Staged leads - shows promoted contacts from both databases
    path("staged-leads/", get_staged_leads, name="staged_leads"),

    # Promote staged leads to active leads
    path("promote-to-active/", convert_staged_leads_to_active, name="promote_to_active"),

    # Active leads view - shows contacts with is_active_lead=True
    path("active-leads/", get_active_leads, name="active_leads_view")


]
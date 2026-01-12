from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Contact, sent_emails
# Register your models here.
admin.site.register(Contact)
admin.site.register(sent_emails)
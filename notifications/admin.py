# notifications/admin.py
from django.contrib import admin
from .models import Notification, AuditLog

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'sujet', 'lu', 'email_envoye', 'date_creation']
    list_filter = ['type', 'lu', 'email_envoye']
    search_fields = ['user__email', 'sujet', 'message']
    date_hierarchy = 'date_creation'

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'description', 'timestamp']
    list_filter = ['action']
    search_fields = ['user__email', 'description']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
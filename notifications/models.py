# notifications/models.py
from django.db import models
from django.conf import settings

class Notification(models.Model):
    TYPE_CHOICES = [
        ('MFA', 'Code MFA'),
        ('RESERVATION', 'Nouvelle reservation'),
        ('VALIDATION', 'Validation de reservation'),
        ('FACTURE', 'Facture generee'),
        ('ALERTE', 'Alerte'),
        ('CONCESSION', 'Echeance de concession'),
        ('EXHUMATION', 'Demande d\'exhumation'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    sujet = models.CharField(max_length=200)
    message = models.TextField()
    lu = models.BooleanField(default=False)
    email_envoye = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_lecture = models.DateTimeField(null=True, blank=True)
    lien = models.CharField(max_length=500, blank=True)
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.user.email}"
    
    def marquer_lu(self):
        self.lu = True
        self.date_lecture = models.DateTimeField(auto_now=True)
        self.save()
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-date_creation']

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Creation'),
        ('UPDATE', 'Modification'),
        ('DELETE', 'Suppression'),
        ('LOGIN', 'Connexion'),
        ('LOGOUT', 'Deconnexion'),
        ('STATUS_CHANGE', 'Changement de statut'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.user} - {self.timestamp}"
    
    class Meta:
        verbose_name = 'Journal d\'audit'
        verbose_name_plural = 'Journaux d\'audit'
        ordering = ['-timestamp']
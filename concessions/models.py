# concessions/models.py
from django.db import models
from django.conf import settings
from reservations.models import Reservation

class Concession(models.Model):
    TYPE_CHOICES = [
        ('TEMPORAIRE', 'Temporaire'),
        ('PERPETUELLE', 'Perpetuelle'),
        ('RENOUVELABLE', 'Renouvelable'),
    ]
    
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='concession')
    type_concession = models.CharField(max_length=20, choices=TYPE_CHOICES, default='TEMPORAIRE')
    duree_annees = models.IntegerField(default=5)
    date_debut = models.DateField()
    date_fin = models.DateField()
    renouvelable = models.BooleanField(default=True)
    date_renouvellement = models.DateField(null=True, blank=True)
    actif = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Concession {self.id} - {self.reservation.caveau}"
    
    class Meta:
        verbose_name = 'Concession'
        verbose_name_plural = 'Concessions'
        ordering = ['-date_debut']

class Exhumation(models.Model):
    STATUT_CHOICES = [
        ('DEMANDE', 'Demande en cours'),
        ('APPROUVEE', 'Approuvee'),
        ('REFUSEE', 'Refusee'),
        ('REALISEE', 'Realisee'),
    ]
    
    concession = models.ForeignKey(Concession, on_delete=models.CASCADE, related_name='exhumations')
    date_demande = models.DateField(auto_now_add=True)
    date_prevue = models.DateField()
    date_realisation = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='DEMANDE')
    motif = models.TextField()
    autorisation_pdf = models.FileField(upload_to='exhumations/autorisations/', null=True, blank=True)
    proces_verbal = models.TextField(blank=True)
    approuve_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='exhumations_approuvees')
    date_approbation = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Exhumation {self.id} - {self.concession.reservation.caveau}"
    
    class Meta:
        verbose_name = 'Exhumation'
        verbose_name_plural = 'Exhumations'
        ordering = ['-date_demande']
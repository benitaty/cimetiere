# reservations/models.py
from django.db import models
from django.conf import settings
from terrains.models import Caveau

class Reservation(models.Model):
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente de validation'),
        ('VALIDE', 'Valide'),
        ('ANNULE', 'Annule'),
    ]
    
    caveau = models.ForeignKey(Caveau, on_delete=models.CASCADE, related_name='reservations')
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    date_debut = models.DateField()
    date_fin = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    date_reservation = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    valide_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservations_validees')
    notes = models.TextField(blank=True)
    cree_par = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='reservations_crees'
    )
    
    def __str__(self):
        return f"Reservation {self.id} - {self.caveau}"
    
    class Meta:
        verbose_name = 'Reservation'
        verbose_name_plural = 'Reservations'

class Defunt(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='defunts')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField(null=True, blank=True)
    date_deces = models.DateField()
    date_enterrement = models.DateField(null=True, blank=True)
    lieu_naissance = models.CharField(max_length=200, blank=True, null=True)  # <-- null=True ajoute
    profession = models.CharField(max_length=100, blank=True, null=True)       # <-- null=True ajoute
    observations = models.TextField(blank=True, null=True)                    # <-- null=True ajoute
    
    def __str__(self):
        return f"{self.nom} {self.prenom}"
    
    class Meta:
        verbose_name = 'Defunt'
        verbose_name_plural = 'Defunts'
        ( )
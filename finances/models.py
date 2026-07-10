# finances/models.py
from django.db import models
from django.conf import settings
from reservations.models import Reservation

class Facture(models.Model):
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente de paiement'),
        ('PAYEE', 'Payee'),
        ('PARTIELLE', 'Partiellement payee'),
        ('ANNULEE', 'Annulee'),
    ]
    
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='facture')
    numero_facture = models.CharField(max_length=50, unique=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_emission = models.DateTimeField(auto_now_add=True)
    date_echeance = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    pdf_fichier = models.FileField(upload_to='factures/', null=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Facture {self.numero_facture}"
    
    def reste_a_payer(self):
        return self.montant_total - self.montant_paye
    
    class Meta:
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'
        ordering = ['-date_emission']

class Paiement(models.Model):
    MOYEN_CHOICES = [
        ('MOBILE_MONEY', 'Mobile Money'),
        ('AIRTEL_MONEY', 'Airtel Money'),
        ('ESPECES', 'Especes'),
        ('VIREMENT', 'Virement bancaire'),
    ]
    
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='paiements')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    moyen = models.CharField(max_length=20, choices=MOYEN_CHOICES)
    reference = models.CharField(max_length=100, unique=True)
    date_paiement = models.DateTimeField(auto_now_add=True)
    statut = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Paiement {self.reference} - {self.montant}€"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from django.db.models import Sum
        total_paye = self.facture.paiements.filter(statut=True).aggregate(Sum('montant'))['montant__sum'] or 0
        self.facture.montant_paye = total_paye
        if total_paye >= self.facture.montant_total:
            self.facture.statut = 'PAYEE'
        elif total_paye > 0:
            self.facture.statut = 'PARTIELLE'
        self.facture.save()
    
    class Meta:
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-date_paiement']
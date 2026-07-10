from django.contrib import admin

# Register your models here.
from django.contrib import admin

# Register your models here.
# finances/admin.py
from django.contrib import admin
from .models import Facture, Paiement

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ['numero_facture', 'reservation', 'montant_total', 'montant_paye', 'statut', 'date_echeance']
    list_filter = ['statut']
    search_fields = ['numero_facture', 'reservation__client__email']
    readonly_fields = ['montant_paye']
    date_hierarchy = 'date_emission'

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ['reference', 'facture', 'montant', 'moyen', 'date_paiement', 'statut']
    list_filter = ['moyen', 'statut']
    search_fields = ['reference']
    date_hierarchy = 'date_paiement'
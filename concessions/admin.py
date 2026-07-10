from django.contrib import admin

# Register your models here.
# concessions/admin.py
from django.contrib import admin
from .models import Concession, Exhumation

@admin.register(Concession)
class ConcessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'reservation', 'type_concession', 'date_debut', 'date_fin', 'actif']
    list_filter = ['type_concession', 'actif']
    search_fields = ['reservation__caveau__numero']
    date_hierarchy = 'date_debut'

@admin.register(Exhumation)
class ExhumationAdmin(admin.ModelAdmin):
    list_display = ['id', 'concession', 'date_demande', 'date_prevue', 'statut']
    list_filter = ['statut']
    search_fields = ['concession__reservation__caveau__numero']
    date_hierarchy = 'date_demande'
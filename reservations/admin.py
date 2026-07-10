from django.contrib import admin

# Register your models here.
# reservations/admin.py
from django.contrib import admin
from .models import Reservation, Defunt

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['id', 'caveau', 'client', 'date_debut', 'date_fin', 'statut']
    list_filter = ['statut']
    search_fields = ['caveau__numero', 'client__email']
    date_hierarchy = 'date_reservation'

@admin.register(Defunt)
class DefuntAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'date_deces', 'reservation']
    search_fields = ['nom', 'prenom']
    date_hierarchy = 'date_deces'

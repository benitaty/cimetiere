# terrains/models.py
from django.db import models

class Zone(models.Model):
    nom = models.CharField(max_length=100)
    superficie = models.FloatField()
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        verbose_name = 'Zone'
        verbose_name_plural = 'Zones'

class Bloc(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='blocs')
    nom = models.CharField(max_length=50)
    nombre_caveaux = models.IntegerField(default=0)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.zone.nom} - {self.nom}"
    
    class Meta:
        verbose_name = 'Bloc'
        verbose_name_plural = 'Blocs'

class Caveau(models.Model):
    STATUT_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('RESERVE', 'Reserve'),
        ('OCCUPE', 'Occupe'),
    ]
    
    bloc = models.ForeignKey(Bloc, on_delete=models.CASCADE, related_name='caveaux')
    numero = models.CharField(max_length=20)
    longitude = models.FloatField(default=0)
    latitude = models.FloatField(default=0)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='DISPONIBLE')
    longueur = models.FloatField(default=2.5)
    largeur = models.FloatField(default=1.0)
    superficie = models.FloatField(default=2.5)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Caveau {self.numero} - {self.bloc.nom}"
    
    class Meta:
        verbose_name = 'Caveau'
        verbose_name_plural = 'Caveaux'
        unique_together = ['bloc', 'numero']
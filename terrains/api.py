# terrains/api.py
from ninja import Router, Schema
from typing import List
from .models import Zone, Bloc, Caveau

router = Router()

# Schemas
class CaveauSchema(Schema):
    id: int
    numero: str
    longitude: float
    latitude: float
    statut: str
    superficie: float

class BlocSchema(Schema):
    id: int
    nom: str
    zone: str
    nombre_caveaux: int

@router.get("/caveaux", response=List[CaveauSchema])
def list_caveaux(request):
    """Liste de tous les caveaux"""
    return Caveau.objects.all()

@router.get("/caveaux/disponibles", response=List[CaveauSchema])
def caveaux_disponibles(request):
    """Liste des caveaux disponibles"""
    return Caveau.objects.filter(statut='DISPONIBLE')

@router.get("/blocs", response=List[BlocSchema])
def list_blocs(request):
    """Liste de tous les blocs"""
    return Bloc.objects.all()

@router.get("/statistiques")
def stats_caveaux(request):
    """Statistiques des caveaux"""
    total = Caveau.objects.count()
    disponibles = Caveau.objects.filter(statut='DISPONIBLE').count()
    reserves = Caveau.objects.filter(statut='RESERVE').count()
    occupes = Caveau.objects.filter(statut='OCCUPE').count()
    
    return {
        "total": total,
        "disponibles": disponibles,
        "reserves": reserves,
        "occupes": occupes,
        "taux_occupation": round((occupes / total * 100) if total > 0 else 0, 2)
    }
# concessions/api.py
from ninja import Router, Schema
from typing import List, Optional
from datetime import date, datetime
from django.shortcuts import get_object_or_404
from .models import Concession, Exhumation
from reservations.models import Reservation
from django.contrib.auth import get_user_model

User = get_user_model()
router = Router()

# ============ SCHEMAS ============
class ConcessionCreateSchema(Schema):
    reservation_id: int
    type_concession: str  # TEMPORAIRE, PERPETUELLE, RENOUVELABLE
    duree_annees: Optional[int] = 5
    date_debut: date
    date_fin: date
    renouvelable: Optional[bool] = True

class ConcessionSchema(Schema):
    id: int
    reservation_id: int
    type_concession: str
    duree_annees: int
    date_debut: date
    date_fin: date
    renouvelable: bool
    actif: bool

class ExhumationCreateSchema(Schema):
    concession_id: int
    date_prevue: date
    motif: str

class ExhumationSchema(Schema):
    id: int
    concession_id: int
    date_demande: str
    date_prevue: date
    date_realisation: Optional[str] = None
    statut: str
    motif: str
    autorisation_pdf: Optional[str] = None
    proces_verbal: Optional[str] = None

# ============ ENDPOINTS CONCESSIONS ============
@router.post("/concessions", response={201: dict, 400: dict, 404: dict})
def creer_concession(request, payload: ConcessionCreateSchema):
    """Creer une nouvelle concession pour une reservation"""
    try:
        # Verifier que la reservation existe et est validee
        reservation = get_object_or_404(Reservation, id=payload.reservation_id)
        
        if reservation.statut != 'VALIDE':
            return 400, {"error": "La reservation doit etre validee avant de creer une concession"}
        
        # Verifier qu'une concession n'existe pas deja
        if hasattr(reservation, 'concession'):
            return 400, {"error": "Une concession existe deja pour cette reservation"}
        
        # Creer la concession
        concession = Concession.objects.create(
            reservation=reservation,
            type_concession=payload.type_concession,
            duree_annees=payload.duree_annees,
            date_debut=payload.date_debut,
            date_fin=payload.date_fin,
            renouvelable=payload.renouvelable,
            actif=True
        )
        
        return 201, {
            "message": "Concession creee avec succes",
            "concession_id": concession.id,
            "type": concession.get_type_concession_display()
        }
        
    except Exception as e:
        return 400, {"error": str(e)}

@router.get("/concessions", response=List[ConcessionSchema])
def list_concessions(request):
    """Liste de toutes les concessions"""
    concessions = Concession.objects.all().select_related('reservation', 'reservation__caveau')
    return [
        {
            "id": c.id,
            "reservation_id": c.reservation.id,
            "type_concession": c.type_concession,
            "duree_annees": c.duree_annees,
            "date_debut": c.date_debut,
            "date_fin": c.date_fin,
            "renouvelable": c.renouvelable,
            "actif": c.actif
        }
        for c in concessions
    ]

@router.get("/concessions/{concession_id}", response=ConcessionSchema)
def get_concession(request, concession_id: int):
    """Details d'une concession"""
    concession = get_object_or_404(Concession, id=concession_id)
    return {
        "id": concession.id,
        "reservation_id": concession.reservation.id,
        "type_concession": concession.type_concession,
        "duree_annees": concession.duree_annees,
        "date_debut": concession.date_debut,
        "date_fin": concession.date_fin,
        "renouvelable": concession.renouvelable,
        "actif": concession.actif
    }

@router.put("/concessions/{concession_id}/renouveler")
def renouveler_concession(request, concession_id: int):
    """Renouveler une concession"""
    concession = get_object_or_404(Concession, id=concession_id)
    
    if not concession.renouvelable:
        return 400, {"error": "Cette concession n'est pas renouvelable"}
    
    if not concession.actif:
        return 400, {"error": "Cette concession n'est pas active"}
    
    # Prolonger la date de fin de la duree
    from datetime import timedelta
    concession.date_fin = concession.date_fin + timedelta(days=concession.duree_annees * 365)
    concession.date_renouvellement = date.today()
    concession.save()
    
    return {
        "message": "Concession renouvelee avec succes",
        "concession_id": concession.id,
        "nouvelle_date_fin": concession.date_fin.isoformat()
    }

# ============ ENDPOINTS EXHUMATIONS ============
@router.post("/exhumations", response={201: dict, 400: dict})
def creer_exhumation(request, payload: ExhumationCreateSchema):
    """Demander une exhumation"""
    try:
        concession = get_object_or_404(Concession, id=payload.concession_id)
        
        if not concession.actif:
            return 400, {"error": "La concession n'est pas active"}
        
        # Verifier qu'il n'y a pas de demande en cours
        existing = Exhumation.objects.filter(
            concession=concession,
            statut__in=['DEMANDE', 'APPROUVEE']
        ).first()
        
        if existing:
            return 400, {"error": "Une demande d'exhumation est deja en cours"}
        
        exhumation = Exhumation.objects.create(
            concession=concession,
            date_prevue=payload.date_prevue,
            motif=payload.motif,
            statut='DEMANDE'
        )
        
        return 201, {
            "message": "Demande d'exhumation creee avec succes",
            "exhumation_id": exhumation.id,
            "statut": "DEMANDE - En attente d'approbation"
        }
        
    except Exception as e:
        return 400, {"error": str(e)}

@router.get("/exhumations", response=List[ExhumationSchema])
def list_exhumations(request):
    """Liste de toutes les exhumations"""
    exhumations = Exhumation.objects.all().select_related('concession', 'concession__reservation')
    return [
        {
            "id": e.id,
            "concession_id": e.concession.id,
            "date_demande": e.date_demande.isoformat(),
            "date_prevue": e.date_prevue,
            "date_realisation": e.date_realisation.isoformat() if e.date_realisation else None,
            "statut": e.statut,
            "motif": e.motif,
            "autorisation_pdf": e.autorisation_pdf.url if e.autorisation_pdf else None,
            "proces_verbal": e.proces_verbal
        }
        for e in exhumations
    ]

@router.get("/exhumations/en-attente", response=List[ExhumationSchema])
def exhumations_en_attente(request):
    """Liste des exhumations en attente d'approbation"""
    exhumations = Exhumation.objects.filter(statut='DEMANDE').select_related('concession')
    return [
        {
            "id": e.id,
            "concession_id": e.concession.id,
            "date_demande": e.date_demande.isoformat(),
            "date_prevue": e.date_prevue,
            "date_realisation": None,
            "statut": e.statut,
            "motif": e.motif,
            "autorisation_pdf": None,
            "proces_verbal": None
        }
        for e in exhumations
    ]

@router.put("/exhumations/{exhumation_id}/approuver")
def approuver_exhumation(request, exhumation_id: int):
    """Approuver une demande d'exhumation"""
    exhumation = get_object_or_404(Exhumation, id=exhumation_id)
    
    if exhumation.statut != 'DEMANDE':
        return 400, {"error": "Cette demande ne peut pas etre approuvee"}
    
    exhumation.statut = 'APPROUVEE'
    exhumation.date_approbation = datetime.now()
    exhumation.save()
    
    return {
        "message": "Demande d'exhumation approuvee avec succes",
        "exhumation_id": exhumation.id,
        "statut": "APPROUVEE"
    }

@router.put("/exhumations/{exhumation_id}/realiser")
def realiser_exhumation(request, exhumation_id: int):
    """Marquer une exhumation comme realisee"""
    exhumation = get_object_or_404(Exhumation, id=exhumation_id)
    
    if exhumation.statut != 'APPROUVEE':
        return 400, {"error": "Cette exhumation doit etre approuvee avant d'etre realisee"}
    
    exhumation.statut = 'REALISEE'
    exhumation.date_realisation = date.today()
    exhumation.save()
    
    return {
        "message": "Exhumation realisee avec succes",
        "exhumation_id": exhumation.id,
        "statut": "REALISEE"
    }
# finances/api.py
from django.http import HttpResponse
from .pdf_generator import generer_facture_pdf
from ninja import Router, Schema
from typing import List, Optional
from datetime import date, datetime
from django.shortcuts import get_object_or_404
from .models import Facture, Paiement
from reservations.models import Reservation
from django.contrib.auth import get_user_model
from .airtel_service import simuler_paiement_airtel
import uuid

User = get_user_model()
router = Router()

# ============ SCHEMAS ============
class FactureCreateSchema(Schema):
    reservation_id: int
    montant_total: float
    date_echeance: date
    notes: Optional[str] = ""

class FactureSchema(Schema):
    id: int
    numero_facture: str
    reservation_id: int
    montant_total: float
    montant_paye: float
    date_emission: str
    date_echeance: date
    statut: str
    notes: Optional[str] = None

class PaiementCreateSchema(Schema):
    facture_id: int
    montant: float
    moyen: str
    reference: str
    notes: Optional[str] = ""

class PaiementSchema(Schema):
    id: int
    facture_id: int
    montant: float
    moyen: str
    reference: str
    date_paiement: str
    statut: bool
    notes: Optional[str] = None

class PaiementAirtelSchema(Schema):
    facture_id: int
    numero_telephone: str

# ============ ENDPOINTS FACTURES ============
@router.post("/factures", response={201: dict, 400: dict, 404: dict})
def creer_facture(request, payload: FactureCreateSchema):
    try:
        reservation = get_object_or_404(Reservation, id=payload.reservation_id)
        if reservation.statut != 'VALIDE':
            return 400, {"error": "La reservation doit etre validee pour generer une facture"}
        if hasattr(reservation, 'facture'):
            return 400, {"error": "Une facture existe deja pour cette reservation"}
        
        numero_facture = f"FACT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        facture = Facture.objects.create(
            reservation=reservation,
            numero_facture=numero_facture,
            montant_total=payload.montant_total,
            montant_paye=0,
            date_echeance=payload.date_echeance,
            statut='EN_ATTENTE',
            notes=payload.notes
        )
        return 201, {
            "message": "Facture creee avec succes",
            "facture_id": facture.id,
            "numero_facture": facture.numero_facture,
            "montant_total": str(facture.montant_total)
        }
    except Exception as e:
        return 400, {"error": str(e)}

@router.get("/factures", response=List[FactureSchema])
def list_factures(request):
    factures = Facture.objects.all().select_related('reservation')
    return [
        {
            "id": f.id,
            "numero_facture": f.numero_facture,
            "reservation_id": f.reservation.id,
            "montant_total": f.montant_total,
            "montant_paye": f.montant_paye,
            "date_emission": f.date_emission.isoformat(),
            "date_echeance": f.date_echeance,
            "statut": f.statut,
            "notes": f.notes
        }
        for f in factures
    ]

@router.get("/factures/{facture_id}", response=FactureSchema)
def get_facture(request, facture_id: int):
    facture = get_object_or_404(Facture, id=facture_id)
    return {
        "id": facture.id,
        "numero_facture": facture.numero_facture,
        "reservation_id": facture.reservation.id,
        "montant_total": facture.montant_total,
        "montant_paye": facture.montant_paye,
        "date_emission": facture.date_emission.isoformat(),
        "date_echeance": facture.date_echeance,
        "statut": facture.statut,
        "notes": facture.notes
    }

@router.get("/factures/en-attente", response=List[FactureSchema])
def factures_en_attente(request):
    factures = Facture.objects.filter(statut='EN_ATTENTE').select_related('reservation')
    return [
        {
            "id": f.id,
            "numero_facture": f.numero_facture,
            "reservation_id": f.reservation.id,
            "montant_total": f.montant_total,
            "montant_paye": f.montant_paye,
            "date_emission": f.date_emission.isoformat(),
            "date_echeance": f.date_echeance,
            "statut": f.statut,
            "notes": f.notes
        }
        for f in factures
    ]

# ============ ENDPOINTS PAIEMENTS ============
@router.post("/paiements", response={201: dict, 400: dict})
def creer_paiement(request, payload: PaiementCreateSchema):
    try:
        facture = get_object_or_404(Facture, id=payload.facture_id)
        if facture.statut == 'PAYEE':
            return 400, {"error": "Cette facture est deja payee"}
        if Paiement.objects.filter(reference=payload.reference).exists():
            return 400, {"error": "Cette reference de paiement existe deja"}
        paiement = Paiement.objects.create(
            facture=facture,
            montant=payload.montant,
            moyen=payload.moyen,
            reference=payload.reference,
            statut=True,
            notes=payload.notes
        )
        return 201, {
            "message": "Paiement enregistre avec succes",
            "paiement_id": paiement.id,
            "montant": str(paiement.montant),
            "nouveau_statut_facture": facture.statut
        }
    except Exception as e:
        return 400, {"error": str(e)}

@router.get("/paiements", response=List[PaiementSchema])
def list_paiements(request):
    paiements = Paiement.objects.all().select_related('facture')
    return [
        {
            "id": p.id,
            "facture_id": p.facture.id,
            "montant": p.montant,
            "moyen": p.moyen,
            "reference": p.reference,
            "date_paiement": p.date_paiement.isoformat(),
            "statut": p.statut,
            "notes": p.notes
        }
        for p in paiements
    ]

@router.get("/paiements/{paiement_id}", response=PaiementSchema)
def get_paiement(request, paiement_id: int):
    paiement = get_object_or_404(Paiement, id=paiement_id)
    return {
        "id": paiement.id,
        "facture_id": paiement.facture.id,
        "montant": paiement.montant,
        "moyen": paiement.moyen,
        "reference": paiement.reference,
        "date_paiement": paiement.date_paiement.isoformat(),
        "statut": paiement.statut,
        "notes": paiement.notes
    }

@router.get("/factures/{facture_id}/paiements", response=List[PaiementSchema])
def paiements_par_facture(request, facture_id: int):
    facture = get_object_or_404(Facture, id=facture_id)
    paiements = facture.paiements.all()
    return [
        {
            "id": p.id,
            "facture_id": p.facture.id,
            "montant": p.montant,
            "moyen": p.moyen,
            "reference": p.reference,
            "date_paiement": p.date_paiement.isoformat(),
            "statut": p.statut,
            "notes": p.notes
        }
        for p in paiements
    ]

# ============ PAIEMENT AIRTEL ============
@router.post("/paiements-airtel")
def paiement_airtel(request, payload: PaiementAirtelSchema):
    """Effectuer un paiement via Airtel Money (simulation)"""
    try:
        facture = get_object_or_404(Facture, id=payload.facture_id)
        
        if facture.statut == 'PAYEE':
            return 400, {"error": "Cette facture est deja payee"}
        
        resultat = simuler_paiement_airtel(payload.numero_telephone, float(facture.montant_total - facture.montant_paye))
        
        if resultat["status"] == "success":
            paiement = Paiement.objects.create(
                facture=facture,
                montant=facture.montant_total - facture.montant_paye,
                moyen='AIRTEL_MONEY',
                reference=resultat["transaction_id"],
                statut=True,
                notes=f"Paiement via Airtel Money - {payload.numero_telephone}"
            )
            
            return {
                "message": "Paiement effectue avec succes",
                "paiement_id": paiement.id,
                "transaction_id": resultat["transaction_id"],
                "montant": str(paiement.montant),
                "nouveau_statut_facture": facture.statut
            }
        else:
            return 400, {"error": resultat["message"]}
            
    except Exception as e:
        return 400, {"error": str(e)}
@router.get("/factures/{facture_id}/pdf",auth=None)
def telecharger_facture_pdf(request, facture_id: int):
    """Télécharger la facture au format PDF"""
    facture = get_object_or_404(Facture, id=facture_id)
    pdf_content = generer_facture_pdf(facture)
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{facture.numero_facture}.pdf"'
    return response  
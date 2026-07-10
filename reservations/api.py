# reservations/api.py
from django.views.decorators.csrf import csrf_exempt
from ninja import Router, Schema
from typing import List, Optional
from datetime import date, timedelta
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Reservation, Defunt
from terrains.models import Caveau
from concessions.models import Concession
from finances.models import Facture
from notifications.models import Notification
from notifications.email_service import (
    envoyer_confirmation_reservation,
    envoyer_facture_avec_expediteur
)
from finances.pdf_generator import generer_facture_pdf
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()
router = Router()

# ============ SCHEMAS ============
class DefuntSchema(Schema):
    id: Optional[int] = None
    nom: str
    prenom: str
    date_naissance: Optional[date] = None
    date_deces: date
    date_enterrement: Optional[date] = None
    lieu_naissance: Optional[str] = None
    profession: Optional[str] = None
    observations: Optional[str] = ""

class ReservationCreateSchema(Schema):
    caveau_id: int
    client_email: str
    date_debut: date
    date_fin: date
    defunts: List[DefuntSchema]

class ReservationSchema(Schema):
    id: int
    caveau: str
    client: str
    date_debut: date
    date_fin: date
    statut: str
    date_reservation: str
    date_validation: Optional[str] = None

# ============ ENDPOINTS ============
@csrf_exempt
@router.post("/reservations", response={201: dict, 400: dict, 404: dict})
def creer_reservation(request, payload: ReservationCreateSchema):
    try:
        caveau = get_object_or_404(Caveau, id=payload.caveau_id)

        if caveau.statut != 'DISPONIBLE':
            return 400, {"error": "Ce caveau n'est pas disponible"}

        try:
            client = User.objects.get(email=payload.client_email)
            cree_par = request.user if request.user.is_authenticated else None
        except User.DoesNotExist:
            return 404, {"error": "Client non trouve"}

        reservation = Reservation.objects.create(
            caveau=caveau,
            client=client,
            date_debut=payload.date_debut,
            date_fin=payload.date_fin,
            cree_par=cree_par,
            statut='EN_ATTENTE'
        )

        for defunt_data in payload.defunts:
            Defunt.objects.create(
                reservation=reservation,
                **defunt_data.dict()
            )

        caveau.statut = 'RESERVE'
        caveau.save()

        envoyer_confirmation_reservation(reservation)

        admins = User.objects.filter(role='ADMIN')
        for admin in admins:
            Notification.objects.create(
                user=admin,
                type='RESERVATION',
                sujet=f"Nouvelle reservation en attente - Caveau {caveau.numero}",
                message=f"Une nouvelle reservation a ete creee par {client.nom} {client.prenom}. En attente de validation.",
                lien=f"/admin/reservations/reservation/{reservation.id}/change/"
            )

        return 201, {
            "message": "Reservation creee avec succes",
            "reservation_id": reservation.id,
            "statut": "EN_ATTENTE - En attente de validation"
        }

    except Exception as e:
        return 400, {"error": str(e)}

@router.get("/reservations", response=List[ReservationSchema])
def list_reservations(request):
    reservations = Reservation.objects.all().select_related('caveau', 'client')
    return [
        {
            "id": r.id,
            "caveau": r.caveau.numero,
            "client": r.client.email,
            "date_debut": r.date_debut,
            "date_fin": r.date_fin,
            "statut": r.statut,
            "date_reservation": r.date_reservation.isoformat(),
            "date_validation": r.date_validation.isoformat() if r.date_validation else None
        }
        for r in reservations
    ]

@router.get("/reservations/en-attente", response=List[ReservationSchema])
def reservations_en_attente(request):
    reservations = Reservation.objects.filter(statut='EN_ATTENTE').select_related('caveau', 'client')
    return [
        {
            "id": r.id,
            "caveau": r.caveau.numero,
            "client": r.client.email,
            "date_debut": r.date_debut,
            "date_fin": r.date_fin,
            "statut": r.statut,
            "date_reservation": r.date_reservation.isoformat(),
            "date_validation": None
        }
        for r in reservations
    ]

# ===== ENDPOINT VALIDATION AVEC CODES DE REPONSE DECLARES =====
@router.put("/reservations/{reservation_id}/valider", response={200: dict, 400: dict, 403: dict})
def valider_reservation(request, reservation_id: int):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    if reservation.statut != 'EN_ATTENTE':
        return 400, {"error": "Cette reservation ne peut pas etre validee"}

    # Récupérer l'admin connecté
    admin = request.user
    if not admin.is_authenticated or admin.role != 'ADMIN':
        return 403, {"error": "Vous devez etre connecte en tant qu'admin"}

    if not admin.email_expediteur:
        return 400, {"error": "Veuillez configurer votre email d'expedition dans votre profil"}

    # Mettre à jour le statut
    reservation.statut = 'VALIDE'
    reservation.date_validation = date.today()
    reservation.save()

    caveau = reservation.caveau
    caveau.statut = 'OCCUPE'
    caveau.save()

    # Créer la concession
    concession = Concession.objects.create(
        reservation=reservation,
        type_concession='TEMPORAIRE',
        duree_annees=5,
        date_debut=date.today(),
        date_fin=date.today() + timedelta(days=5*365),
        renouvelable=True,
        actif=True
    )

    # Créer la facture
    numero_facture = f"FACT-{date.today().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    montant_total = 150000

    facture = Facture.objects.create(
        reservation=reservation,
        numero_facture=numero_facture,
        montant_total=montant_total,
        montant_paye=0,
        date_echeance=date.today() + timedelta(days=30),
        statut='EN_ATTENTE',
        notes="Facture generee automatiquement"
    )

    # Générer et envoyer la facture PDF
    pdf_content = generer_facture_pdf(facture)
    envoyer_facture_avec_expediteur(
        facture=facture,
        pdf_content=pdf_content,
        expediteur_email=admin.email_expediteur
    )

    # Notification aux admins
    admins = User.objects.filter(role='ADMIN')
    for admin_user in admins:
        Notification.objects.create(
            user=admin_user,
            type='RESERVATION',
            sujet=f"Nouvelle reservation validee - Caveau {caveau.numero}",
            message=f"La reservation de {reservation.client.nom} {reservation.client.prenom} a ete validee. Concession creee automatiquement.",
            lien=f"/admin/reservations/reservation/{reservation.id}/change/"
        )

    return {
        "message": "Reservation validee avec succes",
        "reservation_id": reservation.id,
        "concession_id": concession.id,
        "facture_id": facture.id,
        "numero_facture": facture.numero_facture,
        "montant": str(montant_total),
        "facture_envoyee_depuis": admin.email_expediteur
    }
@router.get("/historique")
def historique_reservations(request):
    if not request.user.is_authenticated or request.user.role != 'ADMIN':
        return 403, {"error": "Accès réservé aux administrateurs"}
    from .models import Reservation
    reservations = Reservation.objects.select_related('caveau', 'client', 'valide_par', 'cree_par').all()
    return [
        {
            "id": r.id,
            "caveau": r.caveau.numero,
            "client": f"{r.client.nom} {r.client.prenom}",
            "client_email": r.client.email,
            "date_debut": r.date_debut,
            "date_fin": r.date_fin,
            "statut": r.statut,
            "cree_par": f"{r.cree_par.nom} {r.cree_par.prenom}" if r.cree_par else "Client",
            "valide_par": f"{r.valide_par.nom} {r.valide_par.prenom}" if r.valide_par else "Non validé",
            "date_reservation": r.date_reservation.isoformat(),
            "date_validation": r.date_validation.isoformat() if r.date_validation else None,
        }
        for r in reservations
    ]
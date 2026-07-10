# notifications/api.py
from ninja import Router, Schema
from typing import List, Optional
from datetime import datetime
from django.shortcuts import get_object_or_404
from .models import Notification, AuditLog
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()
router = Router()

# ============ SCHEMAS ============
class NotificationSchema(Schema):
    id: int
    user_id: int
    user_email: str
    type: str
    sujet: str
    message: str
    lu: bool
    email_envoye: bool
    date_creation: str
    date_lecture: Optional[str] = None
    lien: Optional[str] = None

class NotificationCreateSchema(Schema):
    user_id: int
    type: str
    sujet: str
    message: str
    lien: Optional[str] = ""

class AuditLogSchema(Schema):
    id: int
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str
    description: str
    ip_address: Optional[str] = None
    timestamp: str

class AuditLogCreateSchema(Schema):
    action: str
    description: str
    ip_address: Optional[str] = None

# ============ ENDPOINTS NOTIFICATIONS ============
@router.get("/notifications", response=List[NotificationSchema])
def list_notifications(request):
    """Liste de toutes les notifications"""
    notifications = Notification.objects.all().select_related('user')
    return [
        {
            "id": n.id,
            "user_id": n.user.id,
            "user_email": n.user.email,
            "type": n.type,
            "sujet": n.sujet,
            "message": n.message,
            "lu": n.lu,
            "email_envoye": n.email_envoye,
            "date_creation": n.date_creation.isoformat(),
            "date_lecture": n.date_lecture.isoformat() if n.date_lecture else None,
            "lien": n.lien
        }
        for n in notifications
    ]

@router.get("/notifications/{user_id}/user", response=List[NotificationSchema])
def notifications_par_utilisateur(request, user_id: int):
    """Notifications d'un utilisateur"""
    user = get_object_or_404(User, id=user_id)
    notifications = user.notifications.all()
    return [
        {
            "id": n.id,
            "user_id": n.user.id,
            "user_email": n.user.email,
            "type": n.type,
            "sujet": n.sujet,
            "message": n.message,
            "lu": n.lu,
            "email_envoye": n.email_envoye,
            "date_creation": n.date_creation.isoformat(),
            "date_lecture": n.date_lecture.isoformat() if n.date_lecture else None,
            "lien": n.lien
        }
        for n in notifications
    ]

@router.get("/notifications/non-lues", response=List[NotificationSchema])
def notifications_non_lues(request):
    """Notifications non lues"""
    notifications = Notification.objects.filter(lu=False).select_related('user')
    return [
        {
            "id": n.id,
            "user_id": n.user.id,
            "user_email": n.user.email,
            "type": n.type,
            "sujet": n.sujet,
            "message": n.message,
            "lu": n.lu,
            "email_envoye": n.email_envoye,
            "date_creation": n.date_creation.isoformat(),
            "date_lecture": None,
            "lien": n.lien
        }
        for n in notifications
    ]

@router.put("/notifications/{notification_id}/lu")
def marquer_lu(request, notification_id: int):
    """Marquer une notification comme lue"""
    notification = get_object_or_404(Notification, id=notification_id)
    notification.marquer_lu()
    return {"message": "Notification marquee comme lue", "notification_id": notification.id}

@router.post("/notifications", response={201: dict, 400: dict})
def creer_notification(request, payload: NotificationCreateSchema):
    """Creer une notification"""
    try:
        user = get_object_or_404(User, id=payload.user_id)
        
        notification = Notification.objects.create(
            user=user,
            type=payload.type,
            sujet=payload.sujet,
            message=payload.message,
            lu=False,
            email_envoye=False,
            lien=payload.lien
        )
        
        return 201, {
            "message": "Notification creee avec succes",
            "notification_id": notification.id
        }
        
    except Exception as e:
        return 400, {"error": str(e)}

# ============ ENDPOINTS AUDIT LOG ============
@router.get("/audit", response=List[AuditLogSchema])
def list_audit(request):
    """Journal d'audit complet"""
    logs = AuditLog.objects.all().select_related('user')
    return [
        {
            "id": log.id,
            "user_id": log.user.id if log.user else None,
            "user_email": log.user.email if log.user else None,
            "action": log.action,
            "description": log.description,
            "ip_address": log.ip_address,
            "timestamp": log.timestamp.isoformat()
        }
        for log in logs
    ]

@router.get("/audit/{user_id}", response=List[AuditLogSchema])
def audit_par_utilisateur(request, user_id: int):
    """Journal d'audit d'un utilisateur"""
    user = get_object_or_404(User, id=user_id)
    logs = user.auditlog_set.all()
    return [
        {
            "id": log.id,
            "user_id": log.user.id if log.user else None,
            "user_email": log.user.email if log.user else None,
            "action": log.action,
            "description": log.description,
            "ip_address": log.ip_address,
            "timestamp": log.timestamp.isoformat()
        }
        for log in logs
    ]

@router.post("/audit", response={201: dict, 400: dict})
def ajouter_audit(request, payload: AuditLogCreateSchema):
    """Ajouter une entree dans le journal d'audit"""
    try:
        user = None
        if request.user and hasattr(request.user, 'id'):
            user = request.user
        
        audit = AuditLog.objects.create(
            user=user,
            action=payload.action,
            description=payload.description,
            ip_address=payload.ip_address or request.META.get('REMOTE_ADDR', '')
        )
        
        return 201, {
            "message": "Entree d'audit ajoutee avec succes",
            "audit_id": audit.id
        }
        
    except Exception as e:
        return 400, {"error": str(e)}

# ============ ALERTES ADMIN ============
@router.get("/alertes")
def alertes_admin(request):
    """Alertes pour l'administrateur"""
    from reservations.models import Reservation
    from finances.models import Facture
    
    # Alertes
    alertes = []
    
    # 1. Reservations en attente
    attente_count = Reservation.objects.filter(statut='EN_ATTENTE').count()
    if attente_count > 0:
        alertes.append({
            "type": "RESERVATION_EN_ATTENTE",
            "message": f"{attente_count} reservation(s) en attente de validation",
            "niveau": "important"
        })
    
    # 2. Factures impayees
    impayees = Facture.objects.filter(statut='EN_ATTENTE').count()
    if impayees > 0:
        alertes.append({
            "type": "FACTURES_IMPAYEES",
            "message": f"{impayees} facture(s) en attente de paiement",
            "niveau": "important"
        })
    
    # 3. Concessions qui expirent bientot
    from datetime import date, timedelta
    from concessions.models import Concession
    
    soon = date.today() + timedelta(days=30)
    expirations = Concession.objects.filter(date_fin__lte=soon, actif=True).count()
    if expirations > 0:
        alertes.append({
            "type": "CONCESSIONS_EXPIRATION",
            "message": f"{expirations} concession(s) arrivent a expiration dans 30 jours",
            "niveau": "moyen"
        })
    
    return {"alertes": alertes}
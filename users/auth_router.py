# users/auth_router.py
from ninja import Router, Schema
from typing import List, Optional
from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import get_object_or_404
from users.mfa_service import envoyer_otp_utilisateur, verifier_otp, nettoyer_otp

User = get_user_model()
router = Router()

# ============ SCHEMAS ============
class UserSchema(Schema):
    id: int
    email: str
    nom: str
    prenom: str
    role: str

class LoginSchema(Schema):
    email: str
    password: str

class VerifyOTPSchema(Schema):
    email: str
    code: str

class ConfigEmailSchema(Schema):
    email_expediteur: str
    mot_de_passe_expediteur: str

class RenvoyerOTPSchema(Schema):
    email: str

# ============ ENDPOINTS PUBLICS (sans auth) ============

@router.get("/users", response=List[UserSchema], auth=None)
def list_users(request):
    """Liste de tous les utilisateurs (public)"""
    return User.objects.all()

@router.get("/users/{user_id}", response=UserSchema, auth=None)
def get_user(request, user_id: int):
    """Details d'un utilisateur (public)"""
    return get_object_or_404(User, id=user_id)

@router.post("/signin", auth=None)
def signin(request, payload: LoginSchema):
    """Etape 1: Connexion -> envoi OTP par email"""
    try:
        user = User.objects.get(email=payload.email)
    except User.DoesNotExist:
        return {"error": "Utilisateur non trouve"}

    if not user.check_password(payload.password):
        return {"error": "Mot de passe incorrect"}

    envoyer_otp_utilisateur(user)
    return {
        "message": "Code OTP envoye par email",
        "email": user.email,
        "otp_envoye": True,
        "expire_dans": "5 minutes"
    }

@router.post("/signin/verifier-otp", auth=None)
def verifier_otp_endpoint(request, payload: VerifyOTPSchema):
    """Etape 2: Verification du code OTP et création de session"""
    try:
        user = User.objects.get(email=payload.email)
    except User.DoesNotExist:
        return {"error": "Utilisateur non trouve"}

    if verifier_otp(user, payload.code):
        nettoyer_otp(user)

        # Création de la session Django
        login(request, user)

        return {
            "message": "Authentification reussie",
            "email": user.email,
            "nom": user.nom,
            "prenom": user.prenom,
            "role": user.role,
            "authenticated": True,
            "user_id": user.id,
            "email_expediteur": user.email_expediteur or None
        }
    else:
        return {"error": "Code OTP invalide ou expire"}

@router.post("/signin/renvoyer-otp", auth=None)
def renvoyer_otp(request, payload: RenvoyerOTPSchema):
    """Renvoyer un nouveau code OTP"""
    try:
        user = User.objects.get(email=payload.email)
    except User.DoesNotExist:
        return {"error": "Utilisateur non trouve"}

    envoyer_otp_utilisateur(user)
    return {
        "message": "Nouveau code OTP envoye par email",
        "expire_dans": "5 minutes"
    }

# ============ ENDPOINTS PROTEGES (session requise) ============

@router.post("/admin/configurer-email")
def configurer_email_expediteur(request, payload: ConfigEmailSchema):
    """Configurer l'email d'expedition de l'admin connecte"""
    if not request.user or not request.user.is_authenticated:
        return {"error": "Vous devez etre connecte"}

    if request.user.role != 'ADMIN':
        return {"error": "Acces reserve aux administrateurs"}

    user = request.user
    user.email_expediteur = payload.email_expediteur
    user.mot_de_passe_expediteur = payload.mot_de_passe_expediteur
    user.save()

    return {
        "message": "Email d'expedition configure avec succes",
        "email_expediteur": user.email_expediteur
    }

@router.get("/admin/email-config")
def get_email_config(request):
    """Recuperer la configuration email de l'admin connecte"""
    if not request.user or not request.user.is_authenticated:
        return {"error": "Vous devez etre connecte"}

    if request.user.role != 'ADMIN':
        return {"error": "Acces reserve aux administrateurs"}

    return {
        "email_expediteur": request.user.email_expediteur or None,
        "configured": bool(request.user.email_expediteur)
    }

@router.post("/logout")
def logout_user(request):
    """Deconnexion -> suppression de la session"""
    if request.user.is_authenticated:
        logout(request)
        return {"message": "Deconnexion reussie"}
    return {"error": "Vous n'etes pas connecte"}
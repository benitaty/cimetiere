# users/users_router.py
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
class CreateUserSchema(Schema):
    email: str
    password: str
    nom: str
    prenom: str
    role: str = "CLIENT"

class RegisterSchema(Schema):
    email: str
    password: str
    nom: str
    prenom: str

# ============ ROUTES PUBLIQUES (sans auth) ============
@router.post("/signin", auth=None)
def signin(request, payload: LoginSchema):
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
    try:
        user = User.objects.get(email=payload.email)
    except User.DoesNotExist:
        return {"error": "Utilisateur non trouve"}
    if verifier_otp(user, payload.code):
        nettoyer_otp(user)
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
    try:
        user = User.objects.get(email=payload.email)
    except User.DoesNotExist:
        return {"error": "Utilisateur non trouve"}
    envoyer_otp_utilisateur(user)
    return {"message": "Nouveau code OTP envoye par email", "expire_dans": "5 minutes"}

# ============ ROUTES PROTÉGÉES (session requise) ============
@router.get("/", response=List[UserSchema])
def list_users(request):
    """Liste de tous les utilisateurs (accessible uniquement aux admins)"""
    # La vérification se fait via l'authentification par session
    return User.objects.all()

@router.get("/{user_id}", response=UserSchema)
def get_user(request, user_id: int):
    return get_object_or_404(User, id=user_id)

@router.post("/admin/configurer-email")
def configurer_email_expediteur(request, payload: ConfigEmailSchema):
    if not request.user or not request.user.is_authenticated:
        return {"error": "Vous devez etre connecte"}
    if request.user.role != 'ADMIN':
        return {"error": "Acces reserve aux administrateurs"}
    user = request.user
    user.email_expediteur = payload.email_expediteur
    user.mot_de_passe_expediteur = payload.mot_de_passe_expediteur
    user.save()
    return {"message": "Email d'expedition configure avec succes", "email_expediteur": user.email_expediteur}

@router.get("/admin/email-config")
def get_email_config(request):
    if not request.user or not request.user.is_authenticated:
        return {"error": "Vous devez etre connecte"}
    if request.user.role != 'ADMIN':
        return {"error": "Acces reserve aux administrateurs"}
    return {"email_expediteur": request.user.email_expediteur or None, "configured": bool(request.user.email_expediteur)}

@router.post("/logout")
def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        return {"message": "Deconnexion reussie"}
    return {"error": "Vous n'etes pas connecte"}

# ============ MODIFICATION DES RÔLES (admin uniquement) ============
@router.put("/{user_id}/role")
def update_user_role(request, user_id: int, role: str):
    if not request.user.is_authenticated or request.user.role != 'ADMIN':
        return 403, {"error": "Permission denied"}
    user = get_object_or_404(User, id=user_id)
    if role not in ['ADMIN', 'AGENT', 'SECRETARIAT', 'CLIENT']:
        return 400, {"error": "Invalid role"}
    user.role = role
    user.save()
    return {"message": "Role updated", "role": user.role}
@router.post("/")
def create_user(request, payload: CreateUserSchema):
    if not request.user.is_authenticated or request.user.role != 'ADMIN':
        return 403, {"error": "Permission denied"}
    
    if User.objects.filter(email=payload.email).exists():
        return 400, {"error": "Un utilisateur avec cet email existe déjà"}
    
    user = User.objects.create_user(
        email=payload.email,
        password=payload.password,
        nom=payload.nom,
        prenom=payload.prenom,
        role=payload.role
    )
    return {"message": "Utilisateur créé avec succès", "user_id": user.id}

# ============ SUPPRESSION D'UN UTILISATEUR (admin uniquement) ============
@router.delete("/{user_id}")
def delete_user(request, user_id: int):
    if not request.user.is_authenticated or request.user.role != 'ADMIN':
        return 403, {"error": "Permission denied"}
    
    if request.user.id == user_id:
        return 400, {"error": "Vous ne pouvez pas supprimer votre propre compte"}
    
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return {"message": "Utilisateur supprimé avec succès"}

@router.post("/signup", auth=None)  # <-- utilisez un chemin unique
def register_client(request, payload: RegisterSchema):
    if User.objects.filter(email=payload.email).exists():
        return 400, {"error": "Cet email est déjà utilisé."}
    user = User.objects.create_user(
        email=payload.email,
        password=payload.password,
        nom=payload.nom,
        prenom=payload.prenom,
        role='CLIENT'
    )
    return {"message": "Compte créé avec succès.", "user_id": user.id}
# users/api.py
from ninja import Router, Schema
from typing import List
from pydantic import BaseModel
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from .mfa_service import envoyer_otp_utilisateur, verifier_otp, nettoyer_otp
from .models import User as UserModel

User = get_user_model()
router = Router()

# ============================================================
# AUTHENTIFICATION (OTP)
# ============================================================

class SigninSchema(BaseModel):
    email: str
    password: str

class VerifyOTPSchema(BaseModel):
    email: str
    code: str

class RenvoyerOTPSchema(BaseModel):
    email: str

@router.post("/signin", auth=None)
def signin(request, payload: SigninSchema):
    try:
        user = User.objects.get(email=payload.email)
    except User.DoesNotExist:
        return {"error": "Utilisateur non trouve"}
    if not user.check_password(payload.password):
        return {"error": "Mot de passe incorrect"}
    envoyer_otp_utilisateur(user)
    return {"message": "Code OTP envoye par email", "email": user.email, "otp_envoye": True, "expire_dans": "5 minutes"}

@router.post("/signin/verifier-otp", auth=None)
def verifier_otp_endpoint(request, payload: VerifyOTPSchema):
    try:
        user = User.objects.get(email=payload.email)
    except User.DoesNotExist:
        return {"error": "Utilisateur non trouve"}
    if verifier_otp(user, payload.code):
        nettoyer_otp(user)
        login(request, user)
        return {"message": "Authentification reussie", "email": user.email, "nom": user.nom, "prenom": user.prenom, "role": user.role, "authenticated": True, "user_id": user.id}
    return {"error": "Code OTP invalide ou expire"}

@router.post("/signin/renvoyer-otp", auth=None)
def renvoyer_otp(request, payload: RenvoyerOTPSchema):
    try:
        user = User.objects.get(email=payload.email)
    except User.DoesNotExist:
        return {"error": "Utilisateur non trouve"}
    envoyer_otp_utilisateur(user)
    return {"message": "Nouveau code OTP envoye par email", "expire_dans": "5 minutes"}


# ============================================================
# GESTION DES UTILISATEURS (CRUD)
# ============================================================

class UserSchema(Schema):
    id: int
    email: str
    nom: str
    prenom: str
    role: str
    is_active: bool

class UserCreateSchema(Schema):
    email: str
    nom: str
    prenom: str
    password: str
    role: str = "CLIENT"

class UserUpdateRoleSchema(Schema):
    role: str

@router.get("/", response=List[UserSchema])
def list_users(request):
    """Liste de tous les utilisateurs"""
    users = UserModel.objects.all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "nom": u.nom,
            "prenom": u.prenom,
            "role": u.role,
            "is_active": u.is_active,
        }
        for u in users
    ]

@router.post("/", response={201: dict, 400: dict})
def create_user(request, payload: UserCreateSchema):
    """Créer un nouvel utilisateur"""
    if UserModel.objects.filter(email=payload.email).exists():
        return 400, {"error": "Cet email est déjà utilisé"}
    
    user = UserModel.objects.create_user(
        email=payload.email,
        password=payload.password,
        nom=payload.nom,
        prenom=payload.prenom,
        role=payload.role,
    )
    return 201, {
        "message": "Utilisateur créé avec succès",
        "id": user.id,
        "email": user.email,
    }

@router.put("/{user_id}/role")
def update_user_role(request, user_id: int, payload: UserUpdateRoleSchema):
    """Changer le rôle d'un utilisateur"""
    try:
        user = UserModel.objects.get(id=user_id)
        user.role = payload.role
        user.save()
        return {"message": "Rôle mis à jour avec succès"}
    except UserModel.DoesNotExist:
        return 404, {"error": "Utilisateur non trouvé"}

@router.delete("/{user_id}")
def delete_user(request, user_id: int):
    """Supprimer un utilisateur"""
    try:
        user = UserModel.objects.get(id=user_id)
        user.delete()
        return {"message": "Utilisateur supprimé avec succès"}
    except UserModel.DoesNotExist:
        return 404, {"error": "Utilisateur non trouvé"}
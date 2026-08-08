# ============================================================
# GESTION DES UTILISATEURS (CRUD)
# ============================================================

from ninja import Router, Schema
from typing import List
from django.contrib.auth import get_user_model
from .models import User as UserModel

# Schémas pour la gestion des utilisateurs
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
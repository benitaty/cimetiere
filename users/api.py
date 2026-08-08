# users/api.py
from ninja import Router
from pydantic import BaseModel
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from .mfa_service import envoyer_otp_utilisateur, verifier_otp, nettoyer_otp

User = get_user_model()
router = Router()

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
# public/api.py
from ninja import Router, Schema
from django.contrib.auth import get_user_model

User = get_user_model()
router = Router()

class RegisterSchema(Schema):
    email: str
    password: str
    nom: str
    prenom: str

@router.post("/register", auth=None)
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
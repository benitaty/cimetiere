# users/mfa_service.py
import random
import string
from datetime import timedelta
from django.utils import timezone
from notifications.email_service import envoyer_mfa_code

def generer_code_otp():
    return ''.join(random.choices(string.digits, k=6))

def envoyer_otp_utilisateur(user, from_email=None):
    otp_code = generer_code_otp()
    user.mfa_code = otp_code
    user.mfa_code_created_at = timezone.now()
    user.save()

    # AFFICHAGE FORCE DANS LE TERMINAL
    print("="*50)
    print(f"🔐 CODE OTP POUR {user.email} : {otp_code}")
    print("="*50)

    # Envoi réel (si SMTP configuré, ça part en email)
    envoyer_mfa_code(user.email, otp_code, from_email)
    return otp_code

def verifier_otp(user, code_saisi):
    if not user.mfa_code or not user.mfa_code_created_at:
        return False
    expiration = user.mfa_code_created_at + timedelta(minutes=5)
    if timezone.now() > expiration:
        return False
    return user.mfa_code == code_saisi

def nettoyer_otp(user):
    user.mfa_code = None
    user.mfa_code_created_at = None
    user.save()
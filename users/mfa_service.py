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
    
    # 1. Sauvegarder le code en base AVANT l'envoi
    user.mfa_code = otp_code
    user.mfa_code_created_at = timezone.now()
    user.save()
    print(f"✅ Code sauvegardé en base : {otp_code}")
    
    # 2. Envoyer l'email
    envoyer_mfa_code(user.email, otp_code, from_email)
    
    print("="*50)
    print(f"🔐 CODE OTP POUR {user.email} : {otp_code}")
    print("="*50)
    
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
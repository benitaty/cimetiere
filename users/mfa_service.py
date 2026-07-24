# users/mfa_service.py
import random
import string
from datetime import timedelta
from django.utils import timezone
from notifications.email_service import envoyer_mfa_code
from django.core.mail import send_mail
from django.conf import settings

def generer_code_otp():
    return ''.join(random.choices(string.digits, k=6))

def envoyer_otp_utilisateur(user, from_email=None):
    otp_code = generer_code_otp()
    user.mfa_code = otp_code
    user.mfa_code_created_at = timezone.now()
    user.save()
    
    # Envoi direct par email (sans passer par email_service)
    sujet = "Code d'authentification - Cimetiere"
    message = f"Bonjour,\n\nVotre code d'authentification est : {otp_code}\n\nCe code est valable 5 minutes.\n\nCordialement,\nL'equipe du Cimetiere"
    expediteur = from_email or settings.DEFAULT_FROM_EMAIL
    
    try:
        send_mail(
            subject=sujet,
            message=message,
            from_email=expediteur,
            recipient_list=[user.email],
            fail_silently=False,
        )
        print(f"✅ Email OTP envoyé à {user.email} - Code : {otp_code}")
    except Exception as e:
        print(f"❌ Erreur envoi OTP : {e}")
    
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
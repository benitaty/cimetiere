# users/mfa_service.py
import random
import string
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

def generer_code_otp():
    return ''.join(random.choices(string.digits, k=6))

def envoyer_otp_utilisateur(user, from_email=None):
    print(f"🔍 Début de envoyer_otp_utilisateur pour {user.email}")
    otp_code = generer_code_otp()
    user.mfa_code = otp_code
    user.mfa_code_created_at = timezone.now()
    user.save()
    print(f"✅ Code sauvegardé : {otp_code}")

    sujet = "Code d'authentification - Cimetiere"
    message = f"Bonjour,\n\nVotre code d'authentification est : {otp_code}\n\nCe code est valable 5 minutes.\n\nCordialement,\nL'equipe du Cimetiere"

    try:
        print(f"📧 Tentative d'envoi à {user.email} avec send_mail")
        send_mail(
            subject=sujet,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        print("✅ send_mail a réussi")
    except Exception as e:
        print(f"❌ Erreur send_mail : {e}")

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
# -*- coding: utf-8 -*-
# notifications/email_service.py
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def envoyer_email(sujet, message, destinataire, html_message=None, from_email=None):
    """
    Envoie un email simple ou HTML
    Si from_email est fourni, il est utilise comme expediteur
    Sinon, utilise DEFAULT_FROM_EMAIL
    """
    try:
        expediteur = from_email or settings.DEFAULT_FROM_EMAIL
        send_mail(
            subject=sujet,
            message=message,
            from_email=expediteur,
            recipient_list=[destinataire],
            html_message=html_message or message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Erreur envoi email : {e}")
        return False

def envoyer_email_avec_pj(sujet, message, destinataire, pieces_jointes=None, from_email=None):
    """
    Envoie un email avec des pieces jointes (PDF, images, etc.)
    """
    try:
        expediteur = from_email or settings.DEFAULT_FROM_EMAIL
        email = EmailMessage(
            subject=sujet,
            body=message,
            from_email=expediteur,
            to=[destinataire],
        )
        
        # Ajouter les pieces jointes si presentes
        if pieces_jointes:
            for nom_fichier, contenu, mime_type in pieces_jointes:
                email.attach(nom_fichier, contenu, mime_type)
        
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Erreur envoi email avec PJ : {e}")
        return False

def envoyer_confirmation_reservation(reservation, from_email=None):
    """
    Envoie un email de confirmation au client apres creation d'une reservation
    """
    client = reservation.client
    caveau = reservation.caveau
    
    sujet = f"Confirmation de reservation - Caveau {caveau.numero}"
    
    message_plain = f"""
    Bonjour {client.prenom} {client.nom},
    
    Votre reservation pour le caveau {caveau.numero} a bien ete creee.
    
    Details :
    - Caveau : {caveau.numero}
    - Bloc : {caveau.bloc.nom}
    - Date de debut : {reservation.date_debut}
    - Date de fin : {reservation.date_fin}
    - Statut : En attente de validation
    
    Vous recevrez un email des que votre reservation sera validee par l'administration.
    
    Cordialement,
    L'equipe du Cimetiere
    """
    
    message_html = f"""
    <h2>Confirmation de reservation</h2>
    <p>Bonjour <strong>{client.prenom} {client.nom}</strong>,</p>
    <p>Votre reservation pour le caveau <strong>{caveau.numero}</strong> a bien ete creee.</p>
    <h3>Details :</h3>
    <ul>
        <li><strong>Caveau :</strong> {caveau.numero}</li>
        <li><strong>Bloc :</strong> {caveau.bloc.nom}</li>
        <li><strong>Date de debut :</strong> {reservation.date_debut}</li>
        <li><strong>Date de fin :</strong> {reservation.date_fin}</li>
        <li><strong>Statut :</strong> En attente de validation</li>
    </ul>
    <p>Vous recevrez un email des que votre reservation sera validee par l'administration.</p>
    <p>Cordialement,<br>L'equipe du Cimetiere</p>
    """
    
    return envoyer_email(sujet, message_plain, client.email, message_html, from_email)

def envoyer_validation_reservation(reservation, from_email=None):
    """
    Envoie un email au client quand la reservation est validee
    """
    client = reservation.client
    caveau = reservation.caveau
    
    sujet = f"Reservation validee - Caveau {caveau.numero}"
    
    message = f"""
    Bonjour {client.prenom} {client.nom},
    
    Votre reservation pour le caveau {caveau.numero} a ete validee par l'administration.
    
    Details :
    - Caveau : {caveau.numero}
    - Bloc : {caveau.bloc.nom}
    - Date de validation : {reservation.date_validation}
    
    Vous pouvez maintenant proceder au paiement.
    
    Cordialement,
    L'equipe du Cimetiere
    """
    
    return envoyer_email(sujet, message, client.email, from_email=from_email)

def envoyer_facture_email(facture, pdf_content, from_email=None):
    """
    Envoie une facture en PDF au client
    Utilise from_email si fourni (pour l'Option 1)
    """
    client = facture.reservation.client
    sujet = f"Facture {facture.numero_facture}"
    
    message = f"""
    Bonjour {client.prenom} {client.nom},
    
    Veuillez trouver ci-joint votre facture {facture.numero_facture}.
    
    Montant total : {facture.montant_total} FCFA
    Date d'echeance : {facture.date_echeance}
    
    Cordialement,
    L'equipe du Cimetiere
    """
    
    # Utiliser l'expediteur fourni ou celui par defaut
    expediteur = from_email or settings.DEFAULT_FROM_EMAIL
    
    try:
        email = EmailMessage(
            subject=sujet,
            body=message,
            from_email=expediteur,
            to=[client.email],
        )
        
        # Attacher le PDF
        email.attach(
            f"facture_{facture.numero_facture}.pdf",
            pdf_content,
            'application/pdf'
        )
        
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Erreur envoi facture : {e}")
        return False

def envoyer_facture_avec_expediteur(facture, pdf_content, expediteur_email, expediteur_password=None):
    """
    Envoie une facture depuis un expediteur specifique (Gmail)
    Utilise les identifiants fournis pour l'authentification SMTP
    Note: Cette fonction est utile si chaque admin a son propre compte Gmail
    """
    # Pour utiliser un expediteur different, on doit creer une connexion SMTP personnalisee
    # Mais avec django.core.mail, on peut simplement specifier from_email
    # Cependant, Gmail exige que l'expediteur soit authentifie sur le serveur SMTP.
    # Si vous utilisez un compte Gmail different, vous devez utiliser des identifiants distincts.
    
    # Solution simplifiee : utiliser from_email sans changer le backend SMTP
    # (le backend SMTP utilise les identifiants configures dans settings.py)
    # Pour changer completement d'expediteur avec Gmail, il faut creer une connexion SMTP separee
    
    # Pour l'instant, on utilise la fonction standard avec from_email

    return envoyer_facture_email(facture, pdf_content, expediteur_email)

def envoyer_mfa_code(email, code, from_email=None):
    """
    Envoie un code MFA/OTP par email
    """
    sujet = "Code d'authentification - Cimetiere"
    
    message_plain = f"""
    Bonjour,
    
    Votre code d'authentification est : {code}
    
    Ce code est valable 5 minutes.
    
    Si vous n'avez pas demande ce code, ignorez cet email.
    
    Cordialement,
    L'equipe du Cimetiere
    """
    
    message_html = f"""
    <h2>Code d'authentification</h2>
    <p>Bonjour,</p>
    <p>Votre code d'authentification est :</p>
    <h1 style="font-size: 36px; color: #1a237e; text-align: center;">{code}</h1>
    <p>Ce code est valable <strong>5 minutes</strong>.</p>
    <p>Si vous n'avez pas demande ce code, ignorez cet email.</p>
    <p>Cordialement,<br>L'equipe du Cimetiere</p>
    """
    
    return envoyer_email(sujet, message_plain, email, message_html, from_email)

# Alias pour la compatibilite avec le code existant
def envoyer_code_mfa(email, code, from_email=None):
    """
    Alias de envoyer_mfa_code pour la compatibilite
    """
    return envoyer_mfa_code(email, code, from_email)

def envoyer_notification_admin(admin, sujet, message, from_email=None):
    """
    Envoie une notification a un administrateur
    """
    return envoyer_email(sujet, message, admin.email, from_email=from_email)
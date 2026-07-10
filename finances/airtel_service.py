# finances/airtel_service.py
import random
import uuid
from datetime import datetime

def simuler_paiement_airtel(numero_telephone, montant):
    """
    Simule un paiement Airtel Money
    
    Args:
        numero_telephone (str): Numero de telephone (ex: 0612345678)
        montant (float): Montant a payer
    
    Returns:
        dict: Resultat du paiement
    """
    # Generer un ID de transaction unique
    transaction_id = f"AIRTEL-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    
    # Simulation aleatoire (95% de succes)
    success = random.random() < 0.95
    
    if success:
        return {
            "status": "success",
            "transaction_id": transaction_id,
            "message": "Paiement Airtel Money reussi",
            "montant": montant,
            "numero": numero_telephone,
            "date": datetime.now().isoformat(),
            "reference": transaction_id
        }
    else:
        return {
            "status": "failed",
            "message": "Paiement Airtel Money echoue. Veuillez reessayer.",
            "transaction_id": transaction_id
        }

def verifier_paiement(transaction_id):
    """
    Verifie le statut d'un paiement (simulation)
    """
    # Simulation: toujours reussi pour les tests
    return {
        "status": "completed",
        "transaction_id": transaction_id,
        "message": "Paiement verifie avec succes"
    }
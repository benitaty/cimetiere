# frontend/utils/charts_loader.py
import matplotlib.pyplot as plt
import io
import base64
import requests

API_URL = "http://127.0.0.1:8000/api"

def get_reservations_data(session):
    try:
        response = session.get(f"{API_URL}/reservations/reservations", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []

def get_finances_data(session):
    try:
        response = session.get(f"{API_URL}/finances/factures", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []

def get_caveaux_stats(session):
    try:
        response = session.get(f"{API_URL}/terrains/statistiques", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception:
        return {}

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return img_base64

def generer_graphique_reservations(session):
    reservations = get_reservations_data(session)
    if not reservations:
        return None
    mois = {}
    for r in reservations:
        date_str = r.get('date_reservation', '')[:7]
        if date_str:
            mois[date_str] = mois.get(date_str, 0) + 1
    if not mois:
        return None
    sorted_months = sorted(mois.keys())
    counts = [mois[m] for m in sorted_months]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(sorted_months, counts, marker='o', linestyle='-', color='blue', linewidth=2)
    ax.set_title('Évolution des réservations', fontsize=14, fontweight='bold')
    ax.set_xlabel('Mois')
    ax.set_ylabel('Nombre de réservations')
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig_to_base64(fig)

def generer_graphique_statuts_caveaux(session):
    stats = get_caveaux_stats(session)
    if not stats:
        return None
    labels = ['Disponibles', 'Réservés', 'Occupés']
    sizes = [stats.get('disponibles', 0), stats.get('reserves', 0), stats.get('occupes', 0)]
    if sum(sizes) == 0:
        return None
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['#28a745','#fd7e14','#dc3545'], startangle=90)
    ax.set_title('Répartition des caveaux', fontsize=14, fontweight='bold')
    ax.axis('equal')
    plt.tight_layout()
    return fig_to_base64(fig)

def generer_graphique_revenus(session):
    factures = get_finances_data(session)
    if not factures:
        return None
    payees = [f for f in factures if f.get('statut') == 'PAYEE']
    if not payees:
        return None
    mois = {}
    for f in payees:
        date_str = f.get('date_emission', '')[:7]
        if date_str:
            montant = float(f.get('montant_total', 0))
            mois[date_str] = mois.get(date_str, 0) + montant
    if not mois:
        return None
    sorted_months = sorted(mois.keys())
    amounts = [mois[m] for m in sorted_months]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(sorted_months, amounts, color='#4CAF50', width=0.6)
    ax.set_title('Revenus par mois (factures payées)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Mois')
    ax.set_ylabel('Montant (FCFA)')
    ax.grid(True, linestyle='--', alpha=0.6, axis='y')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig_to_base64(fig)
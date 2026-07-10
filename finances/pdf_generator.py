# finances/pdf_generator.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO
import os
from datetime import datetime

def generer_facture_pdf(facture):
    """
    Genere une facture PDF pour une facture donnee
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Styles personnalises
    style_titre = ParagraphStyle(
        'Titre',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontSize=20,
        textColor=colors.HexColor('#1a237e'),
    )
    
    style_sous_titre = ParagraphStyle(
        'SousTitre',
        parent=styles['Heading2'],
        alignment=TA_CENTER,
        fontSize=14,
        textColor=colors.grey,
    )
    
    # Elements du PDF
    elements = []
    
    # En-tete
    elements.append(Paragraph("CIMETIERE - FACTURE", style_titre))
    elements.append(Paragraph(f"Numero: {facture.numero_facture}", style_sous_titre))
    elements.append(Spacer(1, 0.5*inch))
    
    # Informations client
    reservation = facture.reservation
    client = reservation.client
    elements.append(Paragraph(f"Client: {client.nom} {client.prenom}", styles['Normal']))
    elements.append(Paragraph(f"Email: {client.email}", styles['Normal']))
    elements.append(Paragraph(f"Telephone: {client.telephone or 'Non renseigne'}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Informations caveau
    caveau = reservation.caveau
    elements.append(Paragraph(f"Caveau: {caveau.numero}", styles['Normal']))
    elements.append(Paragraph(f"Bloc: {caveau.bloc.nom}", styles['Normal']))
    elements.append(Paragraph(f"Periode: {reservation.date_debut} au {reservation.date_fin}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Tableau des montants
    data = [
        ['Description', 'Montant'],
        [f"Occupation caveau {caveau.numero}", f"{facture.montant_total} FCFA"],
        ['Total', f"{facture.montant_total} FCFA"],
    ]
    
    if facture.montant_paye > 0:
        data.append(['Montant paye', f"{facture.montant_paye} FCFA"])
        data.append(['Reste a payer', f"{facture.montant_total - facture.montant_paye} FCFA"])
    
    table = Table(data, colWidths=[4*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8eaf6')),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Pied de page
    elements.append(Paragraph("Merci de votre confiance.", styles['Normal']))
    elements.append(Paragraph(f"Date d'emission: {facture.date_emission.strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Paragraph(f"Date d'echeance: {facture.date_echeance.strftime('%d/%m/%Y')}", styles['Normal']))
    
    if facture.statut == 'PAYEE':
        elements.append(Paragraph("FACTURE PAYEE", ParagraphStyle('Payee', parent=styles['Normal'], textColor=colors.green, fontSize=16)))
    else:
        elements.append(Paragraph("FACTURE EN ATTENTE DE PAIEMENT", ParagraphStyle('Attente', parent=styles['Normal'], textColor=colors.red, fontSize=16)))
    
    # Generer le PDF
    doc.build(elements)
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content

def generer_certificat_concession(concession):
    """
    Genere un certificat de concession PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    style_titre = ParagraphStyle('Titre', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=24, textColor=colors.HexColor('#1a237e'))
    
    elements = []
    elements.append(Paragraph("CERTIFICAT DE CONCESSION", style_titre))
    elements.append(Spacer(1, 0.5*inch))
    
    reservation = concession.reservation
    client = reservation.client
    caveau = reservation.caveau
    
    elements.append(Paragraph(f"Concession numero: {concession.id}", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Titulaire: {client.nom} {client.prenom}", styles['Normal']))
    elements.append(Paragraph(f"Caveau: {caveau.numero} - {caveau.bloc.nom}", styles['Normal']))
    elements.append(Paragraph(f"Type: {concession.get_type_concession_display()}", styles['Normal']))
    elements.append(Paragraph(f"Date debut: {concession.date_debut}", styles['Normal']))
    elements.append(Paragraph(f"Date fin: {concession.date_fin}", styles['Normal']))
    elements.append(Paragraph(f"Renouvelable: {'Oui' if concession.renouvelable else 'Non'}", styles['Normal']))
    
    if concession.renouvelable:
        elements.append(Paragraph("Cette concession est renouvelable.", styles['Normal']))
    
    doc.build(elements)
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content
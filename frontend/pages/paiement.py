# frontend/pages/paiement.py
import flet as ft
import requests
import webbrowser

class PaiementPage:
    def __init__(self, page: ft.Page, session, go_back):
        self.page = page
        self.session = session
        self.go_back = go_back
        self.factures = []
        self.status = ft.Text("", size=14, color=ft.Colors.RED_700)
        self.liste_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

        # En-tête
        header_row = ft.Row(
            [
                ft.Text("💰 Gestion des paiements", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Retour",
                    icon="arrow_back",
                    on_click=lambda e: self.go_back(),
                    width=120,
                    height=40,
                    bgcolor=ft.Colors.GREY_300,
                    color=ft.Colors.BLACK,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )

        form = ft.Column(
            [header_row, ft.Divider(height=15), self.liste_container, self.status],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            expand=True,
        )

        card = ft.Card(
            content=ft.Container(
                content=form,
                padding=20,
                width=900,
                bgcolor=ft.Colors.WHITE,
                border_radius=20,
                height=600,
            ),
            elevation=20,
            width=900,
        )

        self.content = ft.Container(
            content=card,
            alignment=ft.Alignment.CENTER,
            expand=True,
            gradient=ft.LinearGradient(colors=[ft.Colors.BLUE_50, ft.Colors.WHITE]),
        )

        self.charger_factures()

    def get_content(self):
        return self.content

    def charger_factures(self):
        try:
            response = self.session.get("http://127.0.0.1:8000/api/finances/factures", timeout=5)
            if response.status_code == 200:
                self.factures = response.json()
                self.afficher_factures()
            else:
                self.status.value = f"⚠️ Erreur API: {response.status_code}"
                self.status.color = ft.Colors.RED_700
        except Exception as e:
            self.status.value = f"❌ Erreur: {e}"
            self.status.color = ft.Colors.RED_700
        self.page.update()

    def afficher_factures(self):
        self.liste_container.controls.clear()

        if not self.factures:
            self.liste_container.controls.append(
                ft.Text("Aucune facture trouvée.", size=16, color=ft.Colors.GREY_600)
            )
            return

        factures_impayees = [f for f in self.factures if f['statut'] in ['EN_ATTENTE', 'PARTIELLE']]

        if not factures_impayees:
            self.liste_container.controls.append(
                ft.Text("✅ Toutes les factures sont payées !", size=16, color=ft.Colors.GREEN_700)
            )
            return

        for f in factures_impayees:
            info_row = ft.Row(
                [
                    ft.Text(f"#{f['id']}", width=40, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Rés: {f['reservation_id']}", width=80),
                    ft.Text(f"{f['montant_total']} FCFA", width=100),
                    ft.Text(f"Payé: {f['montant_paye']} FCFA", width=120),
                    ft.Text(f"Échéance: {f['date_echeance']}", width=120),
                    ft.Container(
                        content=ft.Text(f['statut'], size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.ORANGE_700,
                        padding=8,
                        border_radius=12,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=8,
                wrap=True,
            )

            telephone_field = ft.TextField(
                label="Numéro Airtel",
                width=160,
                height=40,
                hint_text="0612345678",
                border=ft.InputBorder.OUTLINE,
                border_color=ft.Colors.BLUE_200,
                focused_border_color=ft.Colors.BLUE_700,
                text_style=ft.TextStyle(size=12),
            )

            btn_payer = ft.ElevatedButton(
                "💳 Payer",
                icon="payments",
                on_click=lambda e, fid=f['id'], tel_field=telephone_field: self.effectuer_paiement(fid, tel_field.value),
                width=110,
                height=40,
                bgcolor=ft.Colors.GREEN_700,
                color=ft.Colors.WHITE,
            )

            # Bouton PDF (corrigé : utilisation de ElevatedButton au lieu de IconButton)
            btn_pdf = ft.ElevatedButton(
                "📄 PDF",
                icon="picture_as_pdf",
                on_click=lambda e, fid=f['id']: self.telecharger_pdf(fid),
                width=80,
                height=40,
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
                style=ft.ButtonStyle(text_style=ft.TextStyle(size=12)),
            )

            ligne = ft.Container(
                content=ft.Row(
                    [info_row, telephone_field, btn_payer, btn_pdf],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=10,
                    wrap=True,
                ),
                padding=10,
                bgcolor=ft.Colors.WHITE,
                border_radius=8,
                shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.GREY_200),
            )
            self.liste_container.controls.append(ligne)

        self.page.update()

    def telecharger_pdf(self, facture_id):
        url = f"http://127.0.0.1:8000/api/finances/factures/{facture_id}/pdf"
        webbrowser.open(url)
        self.status.value = f"📄 Téléchargement de la facture #{facture_id} en cours..."
        self.status.color = ft.Colors.BLUE_700
        self.page.update()

    def effectuer_paiement(self, facture_id, telephone):
        if not telephone or len(telephone) < 9:
            self.status.value = "⚠️ Numéro de téléphone invalide."
            self.status.color = ft.Colors.RED_700
            self.page.update()
            return

        try:
            response = self.session.post(
                "http://127.0.0.1:8000/api/finances/paiements-airtel",
                json={"facture_id": facture_id, "numero_telephone": telephone},
                timeout=10,
            )
            if response.status_code == 200:
                data = response.json()
                self.status.value = f"✅ Paiement effectué ! Transaction: {data.get('transaction_id', 'N/A')}"
                self.status.color = ft.Colors.GREEN_700
                self.charger_factures()
            else:
                error = response.json().get("error", "Erreur inconnue")
                self.status.value = f"❌ Erreur: {error}"
                self.status.color = ft.Colors.RED_700
        except Exception as e:
            self.status.value = f"❌ Erreur: {e}"
            self.status.color = ft.Colors.RED_700
        self.page.update()
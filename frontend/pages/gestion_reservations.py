# frontend/pages/gestion_reservations.py
import flet as ft
import requests
from datetime import datetime

class GestionReservationsPage:
    def __init__(self, page: ft.Page, session, go_back):
        self.page = page
        self.session = session
        self.go_back = go_back
        self.reservations = []
        self.status = ft.Text("", size=14, color=ft.Colors.RED_700)
        self.liste_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

        # --- En-tête avec bouton Retour ---
        header_row = ft.Row(
            [
                ft.Text("📋 Gestion des réservations", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Retour",
                    icon="arrow_back",
                    on_click=lambda e: self.go_back(),
                    width=120,
                    height=40,
                    bgcolor=ft.Colors.GREY_300,
                    color=ft.Colors.BLACK,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        text_style=ft.TextStyle(weight=ft.FontWeight.W_500),
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )

        # --- Formulaire principal ---
        form = ft.Column(
            [
                header_row,
                ft.Divider(height=15, thickness=1, color=ft.Colors.GREY_300),
                self.liste_container,
                self.status,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            expand=True,
        )

        # --- Carte ---
        card = ft.Card(
            content=ft.Container(
                content=form,
                padding=20,
                width=850,
                bgcolor=ft.Colors.WHITE,
                border_radius=20,
                height=600,
            ),
            elevation=20,
            width=850,
        )

        self.content = ft.Container(
            content=card,
            alignment=ft.Alignment.CENTER,
            expand=True,
            gradient=ft.LinearGradient(
                colors=[ft.Colors.BLUE_50, ft.Colors.WHITE],
            ),
        )

        self.charger_reservations()

    def get_content(self):
        return self.content

    def charger_reservations(self):
        try:
            response = self.session.get(
                "http://127.0.0.1:8000/api/reservations/reservations",
                timeout=5,
            )
            if response.status_code == 200:
                self.reservations = response.json()
                self.afficher_reservations()
            else:
                self.status.value = f"⚠️ Erreur API: {response.status_code}"
                self.status.color = ft.Colors.RED_700
        except Exception as e:
            self.status.value = f"❌ Erreur: {e}"
            self.status.color = ft.Colors.RED_700
        self.page.update()

    def afficher_reservations(self):
        self.liste_container.controls.clear()

        if not self.reservations:
            self.liste_container.controls.append(
                ft.Text("Aucune réservation trouvée.", size=16, color=ft.Colors.GREY_600)
            )
            return

        for r in self.reservations:
            statut = r.get('statut', 'INCONNU')
            couleur_statut = {
                'EN_ATTENTE': ft.Colors.ORANGE_700,
                'VALIDE': ft.Colors.GREEN_700,
                'ANNULE': ft.Colors.RED_700,
            }.get(statut, ft.Colors.GREY_700)

            # --- Ligne d'informations (largeurs ajustées) ---
            info_row = ft.Row(
                [
                    ft.Text(f"ID: {r['id']}", width=45, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Cav: {r['caveau']}", width=100),
                    ft.Text(f"Client: {r['client']}", width=180),
                    ft.Text(f"Début: {r['date_debut']}", width=100),
                    ft.Text(f"Fin: {r['date_fin']}", width=100),
                    ft.Container(
                        content=ft.Text(statut, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        bgcolor=couleur_statut,
                        padding=8,
                        border_radius=12,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=8,
                wrap=True,
            )

            # --- Bouton Valider ---
            if statut == 'EN_ATTENTE':
                btn_valider = ft.ElevatedButton(
                    "✅ Valider",
                    icon="check_circle",
                    on_click=lambda e, rid=r['id']: self.valider_reservation(rid),
                    width=100,
                    height=35,
                    bgcolor=ft.Colors.GREEN_700,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=12),
                    ),
                )
            else:
                btn_valider = ft.Container(width=100)

            # --- Ligne complète ---
            ligne = ft.Container(
                content=ft.Row(
                    [info_row, btn_valider],
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

    def valider_reservation(self, reservation_id):
        try:
            response = self.session.put(
                f"http://127.0.0.1:8000/api/reservations/reservations/{reservation_id}/valider",
                timeout=10,
            )
            if response.status_code == 200:
                self.status.value = f"✅ Réservation #{reservation_id} validée ! Facture envoyée."
                self.status.color = ft.Colors.GREEN_700
                self.charger_reservations()  # recharge la liste
            else:
                error = response.json().get("error", "Erreur inconnue")
                self.status.value = f"❌ Erreur: {error}"
                self.status.color = ft.Colors.RED_700
        except Exception as e:
            self.status.value = f"❌ Erreur: {e}"
            self.status.color = ft.Colors.RED_700
        self.page.update()
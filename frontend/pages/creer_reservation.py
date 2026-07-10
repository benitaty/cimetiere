# frontend/pages/creer_reservation.py
import flet as ft
import requests
import re

class CreerReservationPage:
    def __init__(self, page: ft.Page, session, go_back):
        self.page = page
        self.session = session
        self.go_back = go_back
        self.caveaux = []
        self.status = ft.Text("", size=14, color=ft.Colors.RED_700)

        # --- Champs ---
        self.caveau_dropdown = ft.Dropdown(
            label="Caveau",
            width=360,
            hint_text="Sélectionnez un caveau disponible",
            border=ft.InputBorder.OUTLINE,
            border_color=ft.Colors.BLUE_200,
            focused_border_color=ft.Colors.BLUE_700,
            bgcolor=ft.Colors.WHITE,
        )
        self.client_email = ft.TextField(
            label="Email du client",
            width=360,
            prefix_icon="email",
            border=ft.InputBorder.OUTLINE,
            border_color=ft.Colors.BLUE_200,
            focused_border_color=ft.Colors.BLUE_700,
            bgcolor=ft.Colors.WHITE,
            hint_text="ex: client@domaine.com",
        )
        self.date_debut = ft.TextField(
            label="Date de début",
            width=360,
            prefix_icon="calendar_today",
            border=ft.InputBorder.OUTLINE,
            border_color=ft.Colors.BLUE_200,
            focused_border_color=ft.Colors.BLUE_700,
            bgcolor=ft.Colors.WHITE,
            hint_text="YYYY-MM-DD",
        )
        self.date_fin = ft.TextField(
            label="Date de fin",
            width=360,
            prefix_icon="calendar_today",
            border=ft.InputBorder.OUTLINE,
            border_color=ft.Colors.BLUE_200,
            focused_border_color=ft.Colors.BLUE_700,
            bgcolor=ft.Colors.WHITE,
            hint_text="YYYY-MM-DD",
        )

        # --- Défunt ---
        self.defunt_nom = ft.TextField(
            label="Nom du défunt",
            width=360,
            border=ft.InputBorder.OUTLINE,
            border_color=ft.Colors.BLUE_200,
            focused_border_color=ft.Colors.BLUE_700,
            bgcolor=ft.Colors.WHITE,
        )
        self.defunt_prenom = ft.TextField(
            label="Prénom du défunt",
            width=360,
            border=ft.InputBorder.OUTLINE,
            border_color=ft.Colors.BLUE_200,
            focused_border_color=ft.Colors.BLUE_700,
            bgcolor=ft.Colors.WHITE,
        )
        self.defunt_date_deces = ft.TextField(
            label="Date de décès",
            width=360,
            prefix_icon="calendar_today",
            border=ft.InputBorder.OUTLINE,
            border_color=ft.Colors.BLUE_200,
            focused_border_color=ft.Colors.BLUE_700,
            bgcolor=ft.Colors.WHITE,
            hint_text="YYYY-MM-DD",
        )

        # --- Boutons ---
        self.btn_creer = ft.ElevatedButton(
            "Créer la réservation",
            icon="add",
            on_click=self.creer_reservation,
            width=360,
            height=45,
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=14),
                elevation=5,
            ),
        )
        self.btn_retour = ft.ElevatedButton(
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
        )

        # --- Formulaire ---
        form = ft.Column(
            [
                ft.Text("📝 Nouvelle réservation", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                ft.Text("Remplissez les informations ci-dessous.", size=13, color=ft.Colors.GREY_600),
                ft.Divider(height=15, thickness=1, color=ft.Colors.GREY_300),
                self.caveau_dropdown,
                self.client_email,
                self.date_debut,
                self.date_fin,
                ft.Text("Informations du défunt", size=14, weight=ft.FontWeight.W_600, color=ft.Colors.BLUE_700),
                self.defunt_nom,
                self.defunt_prenom,
                self.defunt_date_deces,
                self.btn_creer,
                self.status,
                ft.Row([self.btn_retour], alignment=ft.MainAxisAlignment.CENTER),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        )

        card = ft.Card(
            content=ft.Container(
                content=form,
                padding=30,
                width=450,
                bgcolor=ft.Colors.WHITE,
                border_radius=20,
                height=650,
            ),
            elevation=20,
            width=450,
        )

        self.content = ft.Container(
            content=card,
            alignment=ft.Alignment.CENTER,
            expand=True,
            gradient=ft.LinearGradient(colors=[ft.Colors.BLUE_50, ft.Colors.WHITE]),
        )

        self.charger_caveaux()

    def get_content(self):
        return self.content

    def charger_caveaux(self):
        try:
            response = self.session.get("http://127.0.0.1:8000/api/terrains/caveaux/disponibles", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if not data:
                    self.status.value = "ℹ️ Aucun caveau disponible."
                    self.status.color = ft.Colors.ORANGE_700
                    self.caveau_dropdown.options = []
                else:
                    options = []
                    for c in data:
                        bloc_info = c.get('bloc')
                        if isinstance(bloc_info, dict):
                            bloc_nom = bloc_info.get('nom', str(bloc_info.get('id', '')))
                        else:
                            bloc_nom = str(bloc_info) if bloc_info else 'N/A'
                        options.append(ft.dropdown.Option(
                            key=str(c["id"]),
                            text=f"{c['numero']} - Bloc {bloc_nom}"
                        ))
                    self.caveau_dropdown.options = options
                    if options:
                        self.status.value = ""
            else:
                self.status.value = f"⚠️ Erreur API: {response.status_code}"
                self.status.color = ft.Colors.RED_700
        except Exception as e:
            self.status.value = f"❌ Erreur: {e}"
            self.status.color = ft.Colors.RED_700
            print("Exception:", e)
        self.page.update()

    def est_date_valide(self, date_str):
        """Vérifie que la date est au format YYYY-MM-DD"""
        if not date_str:
            return False
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(pattern, date_str):
            return False
        try:
            from datetime import datetime
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def creer_reservation(self, e):
        # --- Récupération des valeurs ---
        caveau_id = self.caveau_dropdown.value
        client_email = self.client_email.value.strip()
        date_debut = self.date_debut.value.strip()
        date_fin = self.date_fin.value.strip()
        nom = self.defunt_nom.value.strip()
        prenom = self.defunt_prenom.value.strip()
        date_deces = self.defunt_date_deces.value.strip()

        # --- Validation ---
        if not all([caveau_id, client_email, date_debut, date_fin, nom, prenom, date_deces]):
            self.status.value = "⚠️ Tous les champs sont obligatoires."
            self.status.color = ft.Colors.RED_700
            self.page.update()
            return

        if not self.est_date_valide(date_debut):
            self.status.value = "⚠️ Date de début invalide (format YYYY-MM-DD)."
            self.status.color = ft.Colors.RED_700
            self.page.update()
            return

        if not self.est_date_valide(date_fin):
            self.status.value = "⚠️ Date de fin invalide (format YYYY-MM-DD)."
            self.status.color = ft.Colors.RED_700
            self.page.update()
            return

        if not self.est_date_valide(date_deces):
            self.status.value = "⚠️ Date de décès invalide (format YYYY-MM-DD)."
            self.status.color = ft.Colors.RED_700
            self.page.update()
            return

        # --- Construction du payload complet (avec tous les champs optionnels) ---
        payload = {
            "caveau_id": int(caveau_id),
            "client_email": client_email,
            "date_debut": date_debut,
            "date_fin": date_fin,
            "defunts": [
                {
                    "nom": nom,
                    "prenom": prenom,
                    "date_deces": date_deces,
                    "date_naissance": None,      # optionnel
                    "date_enterrement": None,    # optionnel
                    "lieu_naissance": "",        # optionnel
                    "profession": "",            # optionnel
                    "observations": "",          # optionnel
                }
            ],
        }

        try:
            response = self.session.post(
                "http://127.0.0.1:8000/api/reservations/reservations",
                json=payload,
                timeout=10,
            )

            # --- Affichage détaillé pour le débogage ---
            print("=== RÉPONSE API ===")
            print("STATUS:", response.status_code)
            print("HEADERS:", response.headers)
            print("BODY:", response.text)

            if response.status_code == 201:
                data = response.json()
                self.status.value = f"✅ Réservation créée (ID: {data['reservation_id']})"
                self.status.color = ft.Colors.GREEN_700
                self.page.update()
                import threading
                import time
                def redirect():
                    time.sleep(2)
                    self.go_back()
                threading.Thread(target=redirect, daemon=True).start()
            else:
                # Affichage du message d'erreur détaillé
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', error_data.get('detail', str(error_data)))
                except:
                    error_msg = response.text or f"Erreur {response.status_code}"
                self.status.value = f"❌ {error_msg}"
                self.status.color = ft.Colors.RED_700
                self.page.update()

        except requests.exceptions.ConnectionError:
            self.status.value = "❌ Impossible de contacter le serveur."
            self.status.color = ft.Colors.RED_700
            self.page.update()
        except Exception as ex:
            self.status.value = f"❌ Erreur : {ex}"
            self.status.color = ft.Colors.RED_700
            self.page.update()
            print("Exception:", ex)
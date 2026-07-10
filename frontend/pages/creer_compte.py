# frontend/pages/creer_compte.py
import flet as ft
import requests

class CreerComptePage:
    def __init__(self, page: ft.Page, session, go_back):
        self.page = page
        self.session = session
        self.go_back = go_back
        self.status = ft.Text("", size=14, color=ft.Colors.RED_700)

        # Champs du formulaire
        self.email = ft.TextField(label="Email", width=350, prefix_icon="email")
        self.password = ft.TextField(label="Mot de passe", password=True, width=350, prefix_icon="lock", can_reveal_password=True)
        self.nom = ft.TextField(label="Nom", width=350, prefix_icon="person")
        self.prenom = ft.TextField(label="Prénom", width=350, prefix_icon="person")

        # Boutons
        btn_creer = ft.ElevatedButton(
            "Créer mon compte",
            icon="person_add",
            on_click=self.creer_compte,
            width=350,
            height=50,
            bgcolor=ft.Colors.GREEN_700,
            color=ft.Colors.WHITE,
        )
        btn_retour = ft.TextButton(
            "Retour à la connexion",
            on_click=lambda e: self.go_back(),
        )

        # Layout
        form = ft.Column(
            [
                ft.Text("📝 Créer un compte client", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                ft.Divider(height=20),
                self.email,
                self.password,
                self.nom,
                self.prenom,
                btn_creer,
                self.status,
                btn_retour,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=18,
            expand=True,
        )

        card = ft.Card(
            content=ft.Container(
                content=form,
                padding=40,
                width=450,
                bgcolor=ft.Colors.WHITE,
                border_radius=20,
            ),
            elevation=15,
            width=450,
        )

        self.content = ft.Container(
            content=card,
            alignment=ft.Alignment.CENTER,
            expand=True,
            bgcolor=ft.Colors.BLUE_GREY_50,
        )

    def get_content(self):
        return self.content

    def creer_compte(self, e):
        email = self.email.value
        password = self.password.value
        nom = self.nom.value
        prenom = self.prenom.value

        if not all([email, password, nom, prenom]):
            self.status.value = "⚠️ Tous les champs sont obligatoires."
            self.status.color = ft.Colors.RED_700
            self.page.update()
            return

        try:
            response = self.session.post(
                "http://127.0.0.1:8000/api/public/register",
                json={"email": email, "password": password, "nom": nom, "prenom": prenom},
                timeout=10
            )
            print("Status:", response.status_code)
            print("Content:", response.text)  # pour déboguer

            if response.status_code == 200:
                data = response.json()
                self.status.value = "✅ Compte créé ! Vous pouvez vous connecter."
                self.status.color = ft.Colors.GREEN_700
                self.page.update()
                import threading
                import time
                def redirect():
                    time.sleep(2)
                    self.go_back()
                threading.Thread(target=redirect, daemon=True).start()
            else:
                # Essayer de récupérer le message d'erreur
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", "Erreur inconnue")
                except:
                    error_msg = response.text or f"Erreur {response.status_code}"
                self.status.value = f"❌ {error_msg}"
                self.status.color = ft.Colors.RED_700
                self.page.update()
        except Exception as ex:
            self.status.value = f"❌ Erreur : {ex}"
            self.status.color = ft.Colors.RED_700
            self.page.update()
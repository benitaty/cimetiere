# frontend/pages/login.py
import flet as ft
import requests

class LoginPage:
    def __init__(self, page: ft.Page, session, on_login_success, go_to_creer_compte):
        self.page = page
        self.session = session
        self.on_login_success = on_login_success
        self.go_to_creer_compte = go_to_creer_compte  # <-- NOUVEAU

        # --- CHAMPS ---
        self.email = ft.TextField(
            label="Adresse email",
            width=380,
            prefix_icon="email",
            border=ft.InputBorder.OUTLINE,
            border_color=ft.Colors.BLUE_200,
            focused_border_color=ft.Colors.BLUE_700,
            bgcolor=ft.Colors.WHITE,
            text_style=ft.TextStyle(size=16),
            hint_text="ex: nom@domaine.com",
            hint_style=ft.TextStyle(size=12, color=ft.Colors.GREY_400),
        )
        self.password = ft.TextField(
            label="Mot de passe",
            width=380,
            prefix_icon="lock",
            password=True,
            can_reveal_password=True,
            border=ft.InputBorder.OUTLINE,
            border_color=ft.Colors.BLUE_200,
            focused_border_color=ft.Colors.BLUE_700,
            bgcolor=ft.Colors.WHITE,
            text_style=ft.TextStyle(size=16),
        )
        self.otp_code = ft.TextField(
            label="Code OTP",
            width=380,
            prefix_icon="shield",
            visible=False,
            border=ft.InputBorder.OUTLINE,
            border_color=ft.Colors.BLUE_200,
            focused_border_color=ft.Colors.BLUE_700,
            bgcolor=ft.Colors.WHITE,
            text_style=ft.TextStyle(size=16),
            hint_text="Code à 6 chiffres",
            hint_style=ft.TextStyle(size=12, color=ft.Colors.GREY_400),
        )

        self.status = ft.Text("", size=14, color=ft.Colors.RED_700, weight=ft.FontWeight.W_500)

        # --- BOUTONS ---
        self.btn_login = ft.ElevatedButton(
            "Envoyer le code OTP",
            icon="send",
            on_click=self.send_otp,
            width=380,
            height=50,
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=16),
                shadow_color=ft.Colors.BLUE_900,
                elevation=5,
            ),
        )
        self.btn_verify = ft.ElevatedButton(
            "Vérifier le code OTP",
            icon="check_circle",
            on_click=self.verify_otp,
            visible=False,
            width=180,
            height=45,
            bgcolor=ft.Colors.GREEN_700,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=14),
                shadow_color=ft.Colors.GREEN_900,
                elevation=4,
            ),
        )
        self.btn_resend = ft.OutlinedButton(
            "Renvoyer",
            icon="refresh",
            on_click=self.resend_otp,
            visible=False,
            width=160,
            height=45,
            style=ft.ButtonStyle(
                color=ft.Colors.BLUE_700,
                side=ft.BorderSide(2, ft.Colors.BLUE_700),
                shape=ft.RoundedRectangleBorder(radius=10),
                text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=14),
                bgcolor=ft.Colors.BLUE_50,
            ),
        )

        # --- NOUVEAU BOUTON : Créer un compte client ---
        self.btn_creer_compte = ft.TextButton(
            "Créer un compte client",
            on_click=lambda e: self.go_to_creer_compte(),
            style=ft.ButtonStyle(color=ft.Colors.BLUE_700),
        )

        # --- EN-TÊTE ---
        header = ft.Column(
            [
                ft.Text("🏛️", size=80),
                ft.Text("CIMETIÈRE", size=36, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                ft.Text("Gestion des emplacements funéraires", size=16, color=ft.Colors.GREY_700),
                ft.Divider(height=20, thickness=1, color=ft.Colors.GREY_300),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        )

        # --- FORMULAIRE AVEC LE NOUVEAU BOUTON ---
        form = ft.Column(
            [
                self.email,
                self.password,
                self.btn_login,
                self.otp_code,
                ft.Row(
                    [self.btn_verify, self.btn_resend],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
                self.status,
                ft.Row(
                    [self.btn_creer_compte],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=18,
        )

        # --- CARTE PRINCIPALE ---
        card = ft.Card(
            content=ft.Container(
                content=form,
                padding=40,
                width=480,
                bgcolor=ft.Colors.WHITE,
                border_radius=20,
            ),
            elevation=20,
            width=480,
        )

        # --- CONTENEUR AVEC FOND DÉGRADÉ ---
        self.content = ft.Container(
            content=ft.Column(
                [header, card],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=30,
                expand=True,
            ),
            alignment=ft.Alignment.CENTER,
            expand=True,
            gradient=ft.LinearGradient(
                colors=[ft.Colors.BLUE_50, ft.Colors.WHITE],
            ),
        )

        self.email_for_otp = None

    def get_content(self):
        return self.content

    # ---------- MÉTHODES OTP (inchangées) ----------
    def send_otp(self, e):
        email = self.email.value
        password = self.password.value
        if not email or not password:
            self.status.value = "⚠️ Tous les champs sont obligatoires."
            self.status.color = ft.Colors.RED_700
            self.page.update()
            return

        try:
            response = self.session.post(
                "http://127.0.0.1:8000/api/users/signin",
                json={"email": email, "password": password},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("otp_envoye"):
                    self.status.value = "✅ Code OTP envoyé (consultez la console Django)."
                    self.status.color = ft.Colors.GREEN_700
                    self.email_for_otp = email
                    self.otp_code.visible = True
                    self.btn_verify.visible = True
                    self.btn_resend.visible = True
                    self.btn_login.visible = False
                    self.password.visible = False
                    self.page.update()
                else:
                    self.status.value = data.get("error", "Erreur inconnue")
                    self.status.color = ft.Colors.RED_700
                    self.page.update()
            else:
                error = response.json().get("error", "Erreur serveur")
                self.status.value = f"❌ {error}"
                self.status.color = ft.Colors.RED_700
                self.page.update()
        except Exception as ex:
            self.status.value = f"❌ Erreur : {ex}"
            self.status.color = ft.Colors.RED_700
            self.page.update()

    def verify_otp(self, e):
        code = self.otp_code.value
        if not code:
            self.status.value = "⚠️ Veuillez entrer le code OTP."
            self.status.color = ft.Colors.RED_700
            self.page.update()
            return

        try:
            response = self.session.post(
                "http://127.0.0.1:8000/api/users/signin/verifier-otp",
                json={"email": self.email_for_otp, "code": code},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("authenticated"):
                    self.status.value = "✅ Authentification réussie !"
                    self.status.color = ft.Colors.GREEN_700
                    self.page.update()
                    self.on_login_success(data)
                else:
                    self.status.value = data.get("error", "Code invalide ou expiré.")
                    self.status.color = ft.Colors.RED_700
                    self.page.update()
            else:
                error = response.json().get("error", "Erreur serveur")
                self.status.value = f"❌ {error}"
                self.status.color = ft.Colors.RED_700
                self.page.update()
        except Exception as ex:
            self.status.value = f"❌ Erreur : {ex}"
            self.status.color = ft.Colors.RED_700
            self.page.update()

    def resend_otp(self, e):
        if not self.email_for_otp:
            return
        self.status.value = "⏳ Envoi d'un nouveau code..."
        self.status.color = ft.Colors.BLUE_700
        self.page.update()
        try:
            response = self.session.post(
                "http://127.0.0.1:8000/api/users/signin/renvoyer-otp",
                json={"email": self.email_for_otp},
                timeout=10
            )
            if response.status_code == 200:
                self.status.value = "✅ Nouveau code OTP envoyé."
                self.status.color = ft.Colors.GREEN_700
                self.page.update()
            else:
                error = response.json().get("error", "Erreur")
                self.status.value = f"❌ {error}"
                self.status.color = ft.Colors.RED_700
                self.page.update()
        except Exception as ex:
            self.status.value = f"❌ Erreur : {ex}"
            self.status.color = ft.Colors.RED_700
            self.page.update()
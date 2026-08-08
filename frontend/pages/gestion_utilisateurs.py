# frontend/pages/gestion_utilisateurs.py
import flet as ft
import requests

API_URL = "https://cimetiere-backend-otr7.onrender.com/api"

class GestionUtilisateursPage:
    def __init__(self, page: ft.Page, session, go_back):
        self.page = page
        self.session = session
        self.go_back = go_back
        self.utilisateurs = []
        self.status = ft.Text("", size=14, color=ft.Colors.RED_700)
        self.liste_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

        # --- En-tête avec bouton Retour ---
        header_row = ft.Row(
            [
                ft.Text("👥 Gestion des utilisateurs", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
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

        # --- Bouton pour créer un utilisateur ---
        self.btn_creer = ft.ElevatedButton(
            "➕ Nouvel utilisateur",
            icon="person_add",
            on_click=self.afficher_formulaire_creation,
            width=200,
            height=40,
            bgcolor=ft.Colors.GREEN_700,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=13),
            ),
        )

        # --- Formulaire de création (caché par défaut) ---
        self.form_container = ft.Column(
            [
                ft.Text("📝 Créer un utilisateur", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                ft.TextField(
                    label="Email",
                    width=300,
                    prefix_icon="email",
                    border=ft.InputBorder.OUTLINE,
                    border_color=ft.Colors.BLUE_200,
                    focused_border_color=ft.Colors.BLUE_700,
                    bgcolor=ft.Colors.WHITE,
                ),
                ft.TextField(
                    label="Nom",
                    width=300,
                    prefix_icon="person",
                    border=ft.InputBorder.OUTLINE,
                    border_color=ft.Colors.BLUE_200,
                    focused_border_color=ft.Colors.BLUE_700,
                    bgcolor=ft.Colors.WHITE,
                ),
                ft.TextField(
                    label="Prénom",
                    width=300,
                    prefix_icon="person",
                    border=ft.InputBorder.OUTLINE,
                    border_color=ft.Colors.BLUE_200,
                    focused_border_color=ft.Colors.BLUE_700,
                    bgcolor=ft.Colors.WHITE,
                ),
                ft.TextField(
                    label="Mot de passe",
                    width=300,
                    prefix_icon="lock",
                    password=True,
                    can_reveal_password=True,
                    border=ft.InputBorder.OUTLINE,
                    border_color=ft.Colors.BLUE_200,
                    focused_border_color=ft.Colors.BLUE_700,
                    bgcolor=ft.Colors.WHITE,
                ),
                ft.Dropdown(
                    label="Rôle",
                    width=300,
                    options=[
                        ft.dropdown.Option("ADMIN", "Administrateur"),
                        ft.dropdown.Option("AGENT", "Agent de terrain"),
                        ft.dropdown.Option("SECRETARIAT", "Secrétariat"),
                        ft.dropdown.Option("CLIENT", "Client/Citoyen"),
                    ],
                    border=ft.InputBorder.OUTLINE,
                    border_color=ft.Colors.BLUE_200,
                    focused_border_color=ft.Colors.BLUE_700,
                    bgcolor=ft.Colors.WHITE,
                ),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "✅ Créer",
                            icon="check",
                            on_click=self.creer_utilisateur,
                            bgcolor=ft.Colors.GREEN_700,
                            color=ft.Colors.WHITE,
                        ),
                        ft.ElevatedButton(
                            "❌ Annuler",
                            icon="cancel",
                            on_click=self.cacher_formulaire,
                            bgcolor=ft.Colors.GREY_300,
                            color=ft.Colors.BLACK,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=15,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            visible=False,
        )

        # --- Formulaire principal ---
        form = ft.Column(
            [
                header_row,
                ft.Row([self.btn_creer], alignment=ft.MainAxisAlignment.CENTER),
                self.form_container,
                ft.Divider(height=15, thickness=1, color=ft.Colors.GREY_300),
                self.liste_container,
                self.status,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            expand=True,
        )

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
            gradient=ft.LinearGradient(colors=[ft.Colors.BLUE_50, ft.Colors.WHITE]),
        )

        self.charger_utilisateurs()

    def get_content(self):
        return self.content

    def charger_utilisateurs(self):
        try:
            response = self.session.get(f"{API_URL}/users/", timeout=30)
            if response.status_code == 200:
                self.utilisateurs = response.json()
                self.afficher_utilisateurs()
            else:
                self.status.value = f"⚠️ Erreur API: {response.status_code} - {response.text}"
                self.status.color = ft.Colors.RED_700
        except Exception as e:
            self.status.value = f"❌ Erreur: {e}"
            self.status.color = ft.Colors.RED_700
        self.page.update()

    def afficher_utilisateurs(self):
        self.liste_container.controls.clear()

        if not self.utilisateurs:
            self.liste_container.controls.append(
                ft.Text("Aucun utilisateur trouvé.", size=16, color=ft.Colors.GREY_600)
            )
            return

        for u in self.utilisateurs:
            user_id = u.get('id', 'N/A')
            email = u.get('email', 'N/A')
            nom = u.get('nom', 'N/A')
            prenom = u.get('prenom', 'N/A')
            role = u.get('role', 'INCONNU')

            couleur_role = {
                'ADMIN': ft.Colors.RED_700,
                'AGENT': ft.Colors.BLUE_700,
                'SECRETARIAT': ft.Colors.GREEN_700,
                'CLIENT': ft.Colors.ORANGE_700,
            }.get(role, ft.Colors.GREY_700)

            info_row = ft.Row(
                [
                    ft.Text(f"ID: {user_id}", width=60, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{nom} {prenom}", width=180),
                    ft.Text(email, width=200),
                    ft.Container(
                        content=ft.Text(role, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        bgcolor=couleur_role,
                        padding=8,
                        border_radius=12,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=8,
                wrap=True,
            )

            # ========== REMPLACEMENT PAR UNE ROW DE BOUTONS POUR LE RÔLE ==========
            def make_role_handler(uid, new_role):
                def handler(e):
                    self.changer_role(uid, new_role)
                return handler

            role_buttons = ft.Row(
                [
                    ft.OutlinedButton(
                        "Admin",
                        on_click=make_role_handler(user_id, "ADMIN"),
                        style=ft.ButtonStyle(text_style=ft.TextStyle(size=10)),
                        width=60,
                        height=30,
                    ),
                    ft.OutlinedButton(
                        "Agent",
                        on_click=make_role_handler(user_id, "AGENT"),
                        style=ft.ButtonStyle(text_style=ft.TextStyle(size=10)),
                        width=60,
                        height=30,
                    ),
                    ft.OutlinedButton(
                        "Secrétariat",
                        on_click=make_role_handler(user_id, "SECRETARIAT"),
                        style=ft.ButtonStyle(text_style=ft.TextStyle(size=8)),
                        width=70,
                        height=30,
                    ),
                    ft.OutlinedButton(
                        "Client",
                        on_click=make_role_handler(user_id, "CLIENT"),
                        style=ft.ButtonStyle(text_style=ft.TextStyle(size=10)),
                        width=60,
                        height=30,
                    ),
                ],
                spacing=5,
                wrap=True,
            )

            btn_supprimer = ft.TextButton(
                "🗑️",
                on_click=lambda e, uid=user_id: self.supprimer_utilisateur(uid),
                style=ft.ButtonStyle(color=ft.Colors.RED_700, text_style=ft.TextStyle(size=20)),
                tooltip="Supprimer",
            )

            ligne = ft.Container(
                content=ft.Row(
                    [info_row, role_buttons, btn_supprimer],
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

    def afficher_formulaire_creation(self, e):
        self.form_container.visible = True
        self.page.update()

    def cacher_formulaire(self, e):
        self.form_container.visible = False
        self.page.update()

    def creer_utilisateur(self, e):
        champs = self.form_container.controls
        email = champs[1].value
        nom = champs[2].value
        prenom = champs[3].value
        password = champs[4].value
        role = champs[5].value

        if not all([email, nom, prenom, password, role]):
            self.status.value = "⚠️ Tous les champs sont obligatoires."
            self.status.color = ft.Colors.RED_700
            self.page.update()
            return

        payload = {
            "email": email,
            "nom": nom,
            "prenom": prenom,
            "password": password,
            "role": role,
        }

        try:
            response = self.session.post(f"{API_URL}/users/", json=payload, timeout=30)
            if response.status_code == 201:
                self.status.value = f"✅ Utilisateur {email} créé !"
                self.status.color = ft.Colors.GREEN_700
                self.cacher_formulaire(e)
                self.charger_utilisateurs()
            else:
                try:
                    error = response.json().get("error", "Erreur inconnue")
                except:
                    error = response.text
                self.status.value = f"❌ Erreur: {error}"
                self.status.color = ft.Colors.RED_700
        except Exception as ex:
            self.status.value = f"❌ Erreur: {ex}"
            self.status.color = ft.Colors.RED_700
        self.page.update()

    def changer_role(self, user_id, new_role):
        if not new_role:
            return
        try:
            response = self.session.put(
                f"{API_URL}/users/{user_id}/role",
                json={"role": new_role},
                timeout=30,
            )
            if response.status_code == 200:
                self.status.value = f"✅ Rôle de l'utilisateur {user_id} mis à jour."
                self.status.color = ft.Colors.GREEN_700
                self.charger_utilisateurs()
            else:
                try:
                    error = response.json().get("error", "Erreur inconnue")
                except:
                    error = response.text
                self.status.value = f"❌ Erreur: {error}"
                self.status.color = ft.Colors.RED_700
        except Exception as ex:
            self.status.value = f"❌ Erreur: {ex}"
            self.status.color = ft.Colors.RED_700
        self.page.update()

    def supprimer_utilisateur(self, user_id):
        try:
            response = self.session.delete(f"{API_URL}/users/{user_id}", timeout=30)
            if response.status_code == 200:
                self.status.value = f"✅ Utilisateur {user_id} supprimé."
                self.status.color = ft.Colors.GREEN_700
                self.charger_utilisateurs()
            else:
                try:
                    error = response.json().get("error", "Erreur inconnue")
                except:
                    error = response.text
                self.status.value = f"❌ Erreur: {error}"
                self.status.color = ft.Colors.RED_700
        except Exception as ex:
            self.status.value = f"❌ Erreur: {ex}"
            self.status.color = ft.Colors.RED_700
        self.page.update()
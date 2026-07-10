# frontend/pages/gestion_utilisateurs.py
import flet as ft
import requests

class GestionUtilisateursPage:
    def __init__(self, page: ft.Page, session, go_back):
        self.page = page
        self.session = session
        self.go_back = go_back
        self.users = []
        self.status = ft.Text("", size=14, color=ft.Colors.RED_700)
        self.liste_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

        # En-tête
        header_row = ft.Row(
            [
                ft.Text("👥 Gestion des utilisateurs", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "➕ Créer un utilisateur",
                    icon="add",
                    on_click=self.ouvrir_dialog_creation,
                    width=200,
                    height=40,
                    bgcolor=ft.Colors.GREEN_600,
                    color=ft.Colors.WHITE,
                ),
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

        self.liste_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

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
                width=950,
                bgcolor=ft.Colors.WHITE,
                border_radius=20,
                height=650,
            ),
            elevation=20,
            width=950,
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
        print(">>> Chargement des utilisateurs")
        try:
            response = self.session.get("http://127.0.0.1:8000/api/users/", timeout=5)
            if response.status_code == 200:
                self.users = response.json()
                self.afficher_utilisateurs()
            else:
                self.status.value = f"Erreur {response.status_code}: {response.text[:100]}"
                self.status.color = ft.Colors.RED_700
        except Exception as e:
            self.status.value = f"❌ Erreur: {e}"
            self.status.color = ft.Colors.RED_700
        self.page.update()

    def afficher_utilisateurs(self):
        self.liste_container.controls.clear()
        if not self.users:
            self.liste_container.controls.append(
                ft.Text("Aucun utilisateur trouvé.", size=16, color=ft.Colors.GREY_600)
            )
            return

        for user in self.users:
            dropdown = ft.Dropdown(
                width=150,
                value=user['role'],
                options=[
                    ft.dropdown.Option("ADMIN", "Admin"),
                    ft.dropdown.Option("AGENT", "Agent"),
                    ft.dropdown.Option("SECRETARIAT", "Secrétariat"),
                    ft.dropdown.Option("CLIENT", "Client"),
                ],
            )
            dropdown.on_change = lambda e, uid=user['id'], d=dropdown: self.changer_role(uid, d.value)

            # Bouton Supprimer
            btn_supprimer = ft.ElevatedButton(
                "🗑️",
                on_click=lambda e, uid=user['id']: self.confirmer_suppression(uid),
                width=40,
                height=40,
                bgcolor=ft.Colors.RED_100,
                color=ft.Colors.RED_700,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
            )

            info_row = ft.Row(
                [
                    ft.Text(f"ID: {user['id']}", width=50, weight=ft.FontWeight.BOLD),
                    ft.Text(user['email'], width=250),
                    ft.Text(f"{user['nom']} {user['prenom']}", width=200),
                    dropdown,
                    btn_supprimer,
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=10,
                expand=True,
                wrap=True,
            )

            ligne = ft.Container(
                content=info_row,
                padding=10,
                bgcolor=ft.Colors.WHITE,
                border_radius=8,
                shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.GREY_200),
            )
            self.liste_container.controls.append(ligne)

        self.page.update()

    def changer_role(self, user_id, nouveau_role):
        print(f">>> Changement rôle pour l'utilisateur {user_id} vers {nouveau_role}")
        try:
            response = self.session.put(
                f"http://127.0.0.1:8000/api/users/{user_id}/role",
                json={"role": nouveau_role},
                timeout=5,
            )
            if response.status_code == 200:
                self.status.value = f"✅ Rôle mis à jour pour l'utilisateur #{user_id}"
                self.status.color = ft.Colors.GREEN_700
                self.charger_utilisateurs()
            else:
                error = response.json().get("error", "Erreur")
                self.status.value = f"❌ {error}"
                self.status.color = ft.Colors.RED_700
        except Exception as e:
            self.status.value = f"❌ Erreur: {e}"
            self.status.color = ft.Colors.RED_700
        self.page.update()

    def confirmer_suppression(self, user_id):
        print(f">>> Confirmation suppression pour l'utilisateur {user_id}")
        def supprimer(e):
            print(f">>> Suppression de l'utilisateur {user_id}")
            try:
                response = self.session.delete(
                    f"http://127.0.0.1:8000/api/users/{user_id}",
                    timeout=5,
                )
                if response.status_code == 200:
                    self.status.value = f"✅ Utilisateur #{user_id} supprimé avec succès"
                    self.status.color = ft.Colors.GREEN_700
                    self.charger_utilisateurs()
                else:
                    error = response.json().get("error", "Erreur")
                    self.status.value = f"❌ {error}"
                    self.status.color = ft.Colors.RED_700
                self.page.update()
                dialog.open = False
                self.page.update()
            except Exception as e:
                self.status.value = f"❌ Erreur: {e}"
                self.status.color = ft.Colors.RED_700
                self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmation de suppression"),
            content=ft.Text("Voulez-vous vraiment supprimer cet utilisateur ? Cette action est irréversible."),
            actions=[
                ft.TextButton("Annuler", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton("Supprimer", on_click=supprimer, bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        # Utiliser overlay pour afficher le dialogue
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
        print("Dialog suppression ouvert (overlay)")

    def ouvrir_dialog_creation(self, e):
        print(">>> Ouvrir dialog création")
        email_field = ft.TextField(label="Email", width=300)
        password_field = ft.TextField(label="Mot de passe", password=True, width=300, can_reveal_password=True)
        nom_field = ft.TextField(label="Nom", width=300)
        prenom_field = ft.TextField(label="Prénom", width=300)
        role_dropdown = ft.Dropdown(
            width=300,
            value="CLIENT",
            options=[
                ft.dropdown.Option("ADMIN", "Admin"),
                ft.dropdown.Option("AGENT", "Agent"),
                ft.dropdown.Option("SECRETARIAT", "Secrétariat"),
                ft.dropdown.Option("CLIENT", "Client"),
            ],
        )
        status_msg = ft.Text("", size=14, color=ft.Colors.RED_700)

        def creer_utilisateur(e):
            print(">>> Tentative de création d'utilisateur")
            email = email_field.value
            password = password_field.value
            nom = nom_field.value
            prenom = prenom_field.value
            role = role_dropdown.value

            if not all([email, password, nom, prenom, role]):
                status_msg.value = "⚠️ Tous les champs sont obligatoires."
                status_msg.color = ft.Colors.RED_700
                self.page.update()
                return

            try:
                response = self.session.post(
                    "http://127.0.0.1:8000/api/users/",
                    json={
                        "email": email,
                        "password": password,
                        "nom": nom,
                        "prenom": prenom,
                        "role": role,
                    },
                    timeout=5,
                )
                if response.status_code == 200:
                    status_msg.value = "✅ Utilisateur créé avec succès !"
                    status_msg.color = ft.Colors.GREEN_700
                    self.page.update()
                    dialog.open = False
                    self.page.update()
                    self.charger_utilisateurs()
                else:
                    error = response.json().get("error", "Erreur")
                    status_msg.value = f"❌ {error}"
                    status_msg.color = ft.Colors.RED_700
                    self.page.update()
            except Exception as e:
                status_msg.value = f"❌ Erreur: {e}"
                status_msg.color = ft.Colors.RED_700
                self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Créer un utilisateur"),
            content=ft.Column(
                [
                    email_field,
                    password_field,
                    nom_field,
                    prenom_field,
                    role_dropdown,
                    status_msg,
                ],
                spacing=15,
                width=400,
            ),
            actions=[
                ft.TextButton("Annuler", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton("Créer", on_click=creer_utilisateur, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
        print("Dialog création ouvert (overlay)")
# frontend/pages/dashboard.py
import flet as ft
import requests

API_URL = "http://127.0.0.1:8000/api"

class DashboardPage:
    def __init__(self, page: ft.Page, user_data, session, 
                 go_to_carte, go_to_creer_reservation, 
                 go_to_gestion_reservations, go_to_paiement,
                 go_to_gestion_utilisateurs, go_to_historique, logout):
        self.page = page
        self.user_data = user_data
        self.session = session
        self.go_to_carte = go_to_carte
        self.go_to_creer_reservation = go_to_creer_reservation
        self.go_to_gestion_reservations = go_to_gestion_reservations
        self.go_to_paiement = go_to_paiement
        self.go_to_gestion_utilisateurs = go_to_gestion_utilisateurs
        self.go_to_historique = go_to_historique
        self.logout = logout

        # --- Statistiques (valeurs initiales) ---
        self.card_reservations = ft.Text("0", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
        self.card_en_attente = ft.Text("0", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_700)
        self.card_impayees = ft.Text("0", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700)
        self.card_taux = ft.Text("0%", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_700)

        # ============================================================
        # MENU DYNAMIQUE SELON LE RÔLE
        # ============================================================
        role = user_data.get('role', 'CLIENT')
        is_admin = (role == 'ADMIN')

        menu_items = []

        # --- En-tête du menu ---
        menu_items.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.CircleAvatar(
                            content=ft.Text(user_data.get('prenom', 'U')[0].upper(), size=24),
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.BLUE_700,
                            radius=30,
                        ),
                        ft.Text(f"{user_data.get('prenom', '')} {user_data.get('nom', '')}",
                                size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text(user_data.get('email', ''), size=11, color=ft.Colors.WHITE),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                ),
                padding=10,
                bgcolor=ft.Colors.BLUE_800,
            )
        )

        # --- Séparateur ---
        menu_items.append(ft.Divider(height=1, color=ft.Colors.WHITE))

        # --- Boutons communs (tous les rôles) ---
        menu_items.append(ft.ElevatedButton(
            "🏠 Accueil",
            on_click=lambda e: self._afficher_accueil(),
            width=180,
            style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, color=ft.Colors.BLUE_800)
        ))
        menu_items.append(ft.ElevatedButton(
            "➕ Nouvelle réservation",
            on_click=lambda e: self._go_to_creer_reservation(None),
            width=180,
            style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, color=ft.Colors.BLUE_800)
        ))
        menu_items.append(ft.ElevatedButton(
            "📋 Gérer les réservations",
            on_click=lambda e: self._go_to_gestion_reservations(None),
            width=180,
            style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, color=ft.Colors.BLUE_800)
        ))
        menu_items.append(ft.ElevatedButton(
            "🗺️ Carte",
            on_click=lambda e: self._go_to_carte(None),
            width=180,
            style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, color=ft.Colors.BLUE_800)
        ))
        menu_items.append(ft.ElevatedButton(
            "💰 Paiements",
            on_click=lambda e: self._go_to_paiement(None),
            width=180,
            style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, color=ft.Colors.BLUE_800)
        ))

        # --- Boutons ADMIN uniquement ---
        if is_admin:
            menu_items.append(ft.ElevatedButton(
                "📈 Graphiques",
                on_click=lambda e: self._afficher_graphiques(),
                width=180,
                style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, color=ft.Colors.BLUE_800)
            ))
            menu_items.append(ft.ElevatedButton(
                "👥 Utilisateurs",
                on_click=lambda e: self._go_to_gestion_utilisateurs(None),
                width=180,
                style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, color=ft.Colors.BLUE_800)
            ))
            menu_items.append(ft.ElevatedButton(
                "📜 Historique",
                on_click=lambda e: self._go_to_historique(None),
                width=180,
                style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, color=ft.Colors.BLUE_800)
            ))

        # --- Déconnexion (tout le monde) ---
        menu_items.append(ft.ElevatedButton(
            "🚪 Déconnexion",
            on_click=lambda e: self._logout(None),
            width=180,
            style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, color=ft.Colors.RED_700)
        ))

        # --- Construction du menu ---
        menu = ft.Column(menu_items, spacing=10, expand=True)

        menu_container = ft.Container(
            content=menu,
            width=200,
            bgcolor=ft.Colors.BLUE_700,
            padding=10,
            expand=True,
        )

        # --- ZONE DE CONTENU ---
        self.content_area = ft.Container(
            content=ft.Text("Chargement...", size=30, color=ft.Colors.BLACK),
            expand=True,
            padding=40,
            bgcolor=ft.Colors.GREY_100,
        )

        # --- LAYOUT ---
        self.content = ft.Row(
            [menu_container, self.content_area],
            expand=True,
            spacing=0,
        )

        # Charger les stats et afficher l'accueil
        self.charger_stats()
        self._afficher_accueil()

    def get_content(self):
        return self.content

    def charger_stats(self):
        try:
            r = self.session.get(f"{API_URL}/terrains/statistiques", timeout=5)
            if r.status_code == 200:
                data = r.json()
                self.card_taux.value = f"{data.get('taux_occupation', 0)}%"

            r = self.session.get(f"{API_URL}/reservations/reservations/en-attente", timeout=5)
            if r.status_code == 200:
                en_attente = len(r.json())
                self.card_en_attente.value = str(en_attente)

            r = self.session.get(f"{API_URL}/reservations/reservations", timeout=5)
            if r.status_code == 200:
                total = len(r.json())
                self.card_reservations.value = str(total)

            r = self.session.get(f"{API_URL}/finances/factures/en-attente", timeout=5)
            if r.status_code == 200:
                impayees = len(r.json())
                self.card_impayees.value = str(impayees)

        except Exception as e:
            print("Erreur chargement stats:", e)
        self.page.update()

    def _afficher_accueil(self):
        accueil_col = ft.Column(
            [
                ft.Text("📊 Tableau de bord", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                ft.Divider(height=20),
                ft.Row(
                    [
                        ft.Card(ft.Container(ft.Column([ft.Text("Réservations", size=12, color=ft.Colors.GREY_600), self.card_reservations]), padding=15, width=130), elevation=4),
                        ft.Card(ft.Container(ft.Column([ft.Text("En attente", size=12, color=ft.Colors.GREY_600), self.card_en_attente]), padding=15, width=130), elevation=4),
                        ft.Card(ft.Container(ft.Column([ft.Text("Factures impayées", size=12, color=ft.Colors.GREY_600), self.card_impayees]), padding=15, width=140), elevation=4),
                        ft.Card(ft.Container(ft.Column([ft.Text("Taux d'occupation", size=12, color=ft.Colors.GREY_600), self.card_taux]), padding=15, width=140), elevation=4),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=15,
                    wrap=True,
                ),
                ft.Divider(height=20),
                ft.Text("Bienvenue ! Utilisez le menu de gauche pour naviguer.", size=16, color=ft.Colors.GREY_600),
            ],
            spacing=20,
            expand=True,
        )
        self.content_area.content = accueil_col
        self.page.update()

    def _afficher_graphiques(self):
        print(">>> Affichage des graphiques")
        graph_col = ft.Column(
            [
                ft.Text("📈 Graphiques", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                ft.Text("Chargement des graphiques...", size=14, color=ft.Colors.BLUE_700),
            ],
            spacing=20,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        self.content_area.content = graph_col
        self.page.update()

        try:
            from frontend.utils.charts import (
                generer_graphique_reservations,
                generer_graphique_statuts_caveaux,
                generer_graphique_revenus
            )
            graph_col.controls.append(ft.Text("✅ Import réussi", color=ft.Colors.GREEN))
            self.page.update()
        except Exception as e:
            graph_col.controls.append(ft.Text(f"❌ Erreur d'import : {e}", color=ft.Colors.RED))
            self.page.update()
            return

        # Graphique 1
        try:
            img = generer_graphique_reservations(self.session)
            if img:
                graph_col.controls.append(ft.Image(src=img, width=650))
            else:
                graph_col.controls.append(ft.Text("📉 Pas assez de données pour les réservations.", size=14, color=ft.Colors.GREY_600))
            self.page.update()
        except Exception as e:
            graph_col.controls.append(ft.Text(f"❌ Erreur réservations : {e}", color=ft.Colors.RED))
            self.page.update()

        # Graphique 2
        try:
            img = generer_graphique_statuts_caveaux(self.session)
            if img:
                graph_col.controls.append(ft.Image(src=img, width=500))
            else:
                graph_col.controls.append(ft.Text("📊 Pas assez de données pour les statuts.", size=14, color=ft.Colors.GREY_600))
            self.page.update()
        except Exception as e:
            graph_col.controls.append(ft.Text(f"❌ Erreur statuts : {e}", color=ft.Colors.RED))
            self.page.update()

        # Graphique 3
        try:
            img = generer_graphique_revenus(self.session)
            if img:
                graph_col.controls.append(ft.Image(src=img, width=650))
            else:
                graph_col.controls.append(ft.Text("💰 Pas assez de données pour les revenus.", size=14, color=ft.Colors.GREY_600))
            self.page.update()
        except Exception as e:
            graph_col.controls.append(ft.Text(f"❌ Erreur revenus : {e}", color=ft.Colors.RED))
            self.page.update()

        graph_col.controls.append(ft.Text("✅ Chargement terminé", size=12, color=ft.Colors.GREEN_700))
        graph_col.controls.append(
            ft.ElevatedButton(
                "Retour à l'accueil",
                on_click=lambda e: self._afficher_accueil(),
                width=200,
                bgcolor=ft.Colors.BLUE_700,
                color=ft.Colors.WHITE,
            )
        )
        self.page.update()

    # --- Navigation ---
    def _go_to_carte(self, e):
        self.go_to_carte()

    def _go_to_creer_reservation(self, e):
        self.go_to_creer_reservation()

    def _go_to_gestion_reservations(self, e):
        self.go_to_gestion_reservations()

    def _go_to_paiement(self, e):
        self.go_to_paiement()

    def _go_to_gestion_utilisateurs(self, e):
        self.go_to_gestion_utilisateurs()

    def _go_to_historique(self, e):
        self.go_to_historique()

    def _logout(self, e):
        self.logout()
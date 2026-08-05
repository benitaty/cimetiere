# frontend/pages/dashboard.py
import flet as ft
import requests

API_URL = "https://cimetiere-backend-otr7.onrender.com/api"

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

        # --- Conteneur principal (remplacé à chaque mise à jour) ---
        self.main_container = ft.Container(expand=True)

        # --- Chargement initial ---
        self.charger_stats()

    def get_content(self):
        return self.main_container

    def charger_stats(self):
        """Récupère les données et reconstruit l'interface"""
        print("🔍 Chargement des statistiques...")

        stats = {
            "total_reservations": 0,
            "en_attente": 0,
            "impayees": 0,
            "taux_occupation": "0%"
        }

        try:
            # 1. Statistiques des caveaux
            r = self.session.get(f"{API_URL}/terrains/statistiques", timeout=30)
            if r.status_code == 200:
                data = r.json()
                taux = data.get('taux_occupation', 0)
                stats["taux_occupation"] = f"{taux}%"
                print(f"✅ Taux d'occupation : {taux}%")
            else:
                print(f"❌ Erreur /statistiques : {r.status_code}")

            # 2. Réservations en attente
            r = self.session.get(f"{API_URL}/reservations/reservations/en-attente", timeout=30)
            if r.status_code == 200:
                en_attente = len(r.json())
                stats["en_attente"] = en_attente
                print(f"✅ En attente : {en_attente}")
            else:
                print(f"❌ Erreur /en-attente : {r.status_code}")

            # 3. Total des réservations
            r = self.session.get(f"{API_URL}/reservations/reservations", timeout=30)
            if r.status_code == 200:
                total = len(r.json())
                stats["total_reservations"] = total
                print(f"✅ Total réservations : {total}")
            else:
                print(f"❌ Erreur /reservations : {r.status_code}")

            # 4. Factures impayées
            r = self.session.get(f"{API_URL}/finances/factures/en-attente", timeout=30)
            if r.status_code == 200:
                impayees = len(r.json())
                stats["impayees"] = impayees
                print(f"✅ Impayées : {impayees}")
            else:
                print(f"❌ Erreur /factures/en-attente : {r.status_code}")

        except Exception as e:
            print(f"❌ Exception lors du chargement : {e}")

        # --- Construction de l'interface ---
        self._construire_interface(stats)

    def _construire_interface(self, stats):
        """Construit l'interface à partir des statistiques"""

        # --- Menu (identique) ---
        role = self.user_data.get('role', 'CLIENT')
        is_admin = (role == 'ADMIN')

        menu_items = []

        menu_items.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.CircleAvatar(
                            content=ft.Text(self.user_data.get('prenom', 'U')[0].upper(), size=24),
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.BLUE_700,
                            radius=30,
                        ),
                        ft.Text(f"{self.user_data.get('prenom', '')} {self.user_data.get('nom', '')}",
                                size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text(self.user_data.get('email', ''), size=11, color=ft.Colors.WHITE),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                ),
                padding=10,
                bgcolor=ft.Colors.BLUE_800,
            )
        )

        menu_items.append(ft.Divider(height=1, color=ft.Colors.WHITE))

        menu_items.append(ft.ElevatedButton(
            "🏠 Accueil",
            on_click=lambda e: self.charger_stats(),
            width=180,
            style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, color=ft.Colors.BLUE_800)
        ))
        menu_items.append(ft.ElevatedButton(
            "➕ Nouvelle réservation",
            on_click=lambda e: self.go_to_creer_reservation(),
            width=180,
            style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, color=ft.Colors.BLUE_800)
        ))
        menu_items.append(ft.ElevatedButton(
            "📋 Gérer les réservations",
            on_click=lambda e: self.go_to_gestion_reservations(),
            width=180,
            style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, color=ft.Colors.BLUE_800)
        ))
        menu_items.append(ft.ElevatedButton(
            "🗺️ Carte",
            on_click=lambda e: self.go_to_carte(),
            width=180,
            style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, color=ft.Colors.BLUE_800)
        ))
        menu_items.append(ft.ElevatedButton(
            "💰 Paiements",
            on_click=lambda e: self.go_to_paiement(),
            width=180,
            style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, color=ft.Colors.BLUE_800)
        ))

        if is_admin:
            menu_items.append(ft.ElevatedButton(
                "📈 Graphiques",
                on_click=lambda e: self._afficher_graphiques(),
                width=180,
                style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, color=ft.Colors.BLUE_800)
            ))
            menu_items.append(ft.ElevatedButton(
                "👥 Utilisateurs",
                on_click=lambda e: self.go_to_gestion_utilisateurs(),
                width=180,
                style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, color=ft.Colors.BLUE_800)
            ))
            menu_items.append(ft.ElevatedButton(
                "📜 Historique",
                on_click=lambda e: self.go_to_historique(),
                width=180,
                style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, color=ft.Colors.BLUE_800)
            ))

        menu_items.append(ft.ElevatedButton(
            "🚪 Déconnexion",
            on_click=lambda e: self.logout(),
            width=180,
            style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, color=ft.Colors.RED_700)
        ))

        menu = ft.Column(menu_items, spacing=10, expand=True)
        menu_container = ft.Container(
            content=menu,
            width=200,
            bgcolor=ft.Colors.BLUE_700,
            padding=10,
            expand=True,
        )

        # --- Contenu principal (les cartes) ---
        accueil_col = ft.Column(
            [
                ft.Text("📊 Tableau de bord", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                ft.Divider(height=20),
                ft.Row(
                    [
                        ft.Card(
                            ft.Container(
                                ft.Column([
                                    ft.Text("Réservations", size=12, color=ft.Colors.GREY_600),
                                    ft.Text(str(stats["total_reservations"]), size=28,
                                            weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
                                ]),
                                padding=15, width=140
                            ),
                            elevation=4
                        ),
                        ft.Card(
                            ft.Container(
                                ft.Column([
                                    ft.Text("En attente", size=12, color=ft.Colors.GREY_600),
                                    ft.Text(str(stats["en_attente"]), size=28,
                                            weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_700)
                                ]),
                                padding=15, width=140
                            ),
                            elevation=4
                        ),
                        ft.Card(
                            ft.Container(
                                ft.Column([
                                    ft.Text("Factures impayées", size=12, color=ft.Colors.GREY_600),
                                    ft.Text(str(stats["impayees"]), size=28,
                                            weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700)
                                ]),
                                padding=15, width=140
                            ),
                            elevation=4
                        ),
                        ft.Card(
                            ft.Container(
                                ft.Column([
                                    ft.Text("Taux d'occupation", size=12, color=ft.Colors.GREY_600),
                                    ft.Text(stats["taux_occupation"], size=28,
                                            weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_700)
                                ]),
                                padding=15, width=140
                            ),
                            elevation=4
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=15,
                    wrap=True,
                ),
                ft.Divider(height=20),
                ft.Text("Bienvenue ! Utilisez le menu de gauche pour naviguer.", size=16, color=ft.Colors.GREY_600),
                ft.ElevatedButton(
                    "🔄 Rafraîchir les données",
                    on_click=lambda e: self.charger_stats(),
                    width=200,
                    bgcolor=ft.Colors.BLUE_700,
                    color=ft.Colors.WHITE,
                ),
            ],
            spacing=20,
            expand=True,
        )

        content_area = ft.Container(
            content=accueil_col,
            expand=True,
            padding=40,
            bgcolor=ft.Colors.GREY_100,
        )

        # --- Assemblage final ---
        self.main_container.content = ft.Row(
            [menu_container, content_area],
            expand=True,
            spacing=0,
        )
        self.page.update()

    def _afficher_graphiques(self):
        """Affiche les graphiques (inchangé)"""
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
        self.main_container.content = ft.Container(
            content=graph_col,
            expand=True,
            padding=40,
            bgcolor=ft.Colors.GREY_100,
        )
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
                on_click=lambda e: self.charger_stats(),
                width=200,
                bgcolor=ft.Colors.BLUE_700,
                color=ft.Colors.WHITE,
            )
        )
        self.page.update()
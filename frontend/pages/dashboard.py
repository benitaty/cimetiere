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

        self.main_container = ft.Container(expand=True)
        self.charger_stats()

    def get_content(self):
        return self.main_container

    def charger_stats(self):
        print("🔍 Chargement des statistiques...")

        stats = {
            "total_reservations": 0,
            "en_attente": 0,
            "impayees": 0,
            "taux_occupation": "0%"
        }

        try:
            r = self.session.get(f"{API_URL}/terrains/statistiques", timeout=30)
            if r.status_code == 200:
                data = r.json()
                stats["taux_occupation"] = f"{data.get('taux_occupation', 0)}%"

            r = self.session.get(f"{API_URL}/reservations/reservations", timeout=30)
            if r.status_code == 200:
                stats["total_reservations"] = len(r.json())

            r = self.session.get(f"{API_URL}/reservations/reservations/en-attente", timeout=30)
            if r.status_code == 200:
                stats["en_attente"] = len(r.json())

        except Exception as e:
            print(f"❌ Erreur : {e}")

        self._afficher_dashboard(stats)

    def _afficher_dashboard(self, stats):
        # ============ MENU LATÉRAL ============
        menu_items = ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text("👤", size=30),
                    ft.Text(self.user_data.get('prenom', 'U'), size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(self.user_data.get('email', ''), size=10),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                padding=10,
                bgcolor=ft.Colors.BLUE_800,
            ),
            ft.Divider(color=ft.Colors.WHITE),
            ft.ElevatedButton("🏠 Accueil", on_click=lambda e: self.charger_stats(), width=160),
            ft.ElevatedButton("➕ Réservation", on_click=lambda e: self.go_to_creer_reservation(), width=160),
            ft.ElevatedButton("📋 Gérer", on_click=lambda e: self.go_to_gestion_reservations(), width=160),
            ft.ElevatedButton("🗺️ Carte", on_click=lambda e: self.go_to_carte(), width=160),
            ft.ElevatedButton("💰 Paiements", on_click=lambda e: self.go_to_paiement(), width=160),
            ft.ElevatedButton("📈 Graphiques", on_click=lambda e: self._afficher_graphiques(), width=160),
            ft.ElevatedButton("👥 Utilisateurs", on_click=lambda e: self.go_to_gestion_utilisateurs(), width=160),
            ft.ElevatedButton("📜 Historique", on_click=lambda e: self.go_to_historique(), width=160),
            ft.Divider(color=ft.Colors.WHITE),
            ft.ElevatedButton("🚪 Déconnexion", on_click=lambda e: self.logout(), width=160, style=ft.ButtonStyle(color=ft.Colors.RED_700)),
        ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        menu_container = ft.Container(
            content=menu_items,
            width=200,
            bgcolor=ft.Colors.BLUE_700,
            padding=10,
        )

        # ============ CONTENU PRINCIPAL (CARTES) ============
        cartes_row = ft.Row(
            [
                ft.Card(
                    ft.Container(
                        ft.Column([
                            ft.Text("📋 Réservations", size=14, color=ft.Colors.GREY_600),
                            ft.Text(str(stats["total_reservations"]), size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        padding=20, width=150, height=110,
                    ),
                    elevation=4,
                ),
                ft.Card(
                    ft.Container(
                        ft.Column([
                            ft.Text("⏳ En attente", size=14, color=ft.Colors.GREY_600),
                            ft.Text(str(stats["en_attente"]), size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_700),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        padding=20, width=150, height=110,
                    ),
                    elevation=4,
                ),
                ft.Card(
                    ft.Container(
                        ft.Column([
                            ft.Text("💰 Impayées", size=14, color=ft.Colors.GREY_600),
                            ft.Text(str(stats["impayees"]), size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        padding=20, width=150, height=110,
                    ),
                    elevation=4,
                ),
                ft.Card(
                    ft.Container(
                        ft.Column([
                            ft.Text("📈 Occupation", size=14, color=ft.Colors.GREY_600),
                            ft.Text(stats["taux_occupation"], size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_700),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        padding=20, width=150, height=110,
                    ),
                    elevation=4,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15,
            wrap=True,
        )

        content_right = ft.Container(
            content=ft.Column([
                ft.Text("📊 Tableau de bord", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                ft.Text(f"Bienvenue, {self.user_data.get('prenom', '')} {self.user_data.get('nom', '')} !", 
                        size=16, color=ft.Colors.GREY_600),
                ft.Divider(height=20),
                cartes_row,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20, expand=True),
            expand=True,
            padding=30,
            bgcolor=ft.Colors.GREY_100,
        )

        layout = ft.Row(
            [menu_container, content_right],
            expand=True,
            spacing=0,
        )

        self.main_container.content = layout
        self.page.update()
        print("✅ Dashboard avec cartes affiché.")

    def _afficher_graphiques(self):
        """Affiche les graphiques réels depuis l'API."""
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

        # --- Graphique 1 : Réservations ---
        try:
            img = generer_graphique_reservations(self.session)
            if img:
                graph_col.controls.append(ft.Image(src=img, width=650))  # <-- fit supprimé
            else:
                graph_col.controls.append(ft.Text("📉 Pas assez de données pour les réservations.", size=14, color=ft.Colors.GREY_600))
            self.page.update()
        except Exception as e:
            graph_col.controls.append(ft.Text(f"❌ Erreur réservations : {e}", color=ft.Colors.RED))
            self.page.update()

        # --- Graphique 2 : Statuts des caveaux ---
        try:
            img = generer_graphique_statuts_caveaux(self.session)
            if img:
                graph_col.controls.append(ft.Image(src=img, width=500))  # <-- fit supprimé
            else:
                graph_col.controls.append(ft.Text("📊 Pas assez de données pour les statuts.", size=14, color=ft.Colors.GREY_600))
            self.page.update()
        except Exception as e:
            graph_col.controls.append(ft.Text(f"❌ Erreur statuts : {e}", color=ft.Colors.RED))
            self.page.update()

        # --- Graphique 3 : Revenus ---
        try:
            img = generer_graphique_revenus(self.session)
            if img:
                graph_col.controls.append(ft.Image(src=img, width=650))  # <-- fit supprimé
            else:
                graph_col.controls.append(ft.Text("💰 Pas assez de données pour les revenus.", size=14, color=ft.Colors.GREY_600))
            self.page.update()
        except Exception as e:
            graph_col.controls.append(ft.Text(f"❌ Erreur revenus : {e}", color=ft.Colors.RED))
            self.page.update()

        # --- Bouton Retour ---
        graph_col.controls.append(ft.Text("✅ Chargement terminé", size=12, color=ft.Colors.GREEN_700))
        graph_col.controls.append(
            ft.ElevatedButton(
                "🔙 Retour",
                on_click=lambda e: self.charger_stats(),
                width=200,
                bgcolor=ft.Colors.BLUE_700,
                color=ft.Colors.WHITE,
            )
        )
        self.page.update()
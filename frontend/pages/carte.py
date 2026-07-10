# frontend/pages/carte.py
import flet as ft
import folium
import requests
import tempfile
import os
import webbrowser
from folium import plugins

API_URL = "http://127.0.0.1:8000/api"

class CartePage:
    def __init__(self, page: ft.Page, session, go_back):
        self.page = page
        self.session = session
        self.go_back = go_back
        self.chemin_carte = None
        self.carte_message = ft.Text("Chargement de la carte...", size=16, color=ft.Colors.BLUE_700)

        self.bouton_carte = ft.ElevatedButton(
            "Ouvrir la carte dans le navigateur",
            icon="map",
            on_click=self.ouvrir_carte,
            disabled=True,
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(text_style=ft.TextStyle(weight=ft.FontWeight.BOLD)),
        )

        self.stats_cards = {
            "total": ft.Text("0", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
            "disponibles": ft.Text("0", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
            "reserves": ft.Text("0", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE),
            "occupes": ft.Text("0", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
            "taux": ft.Text("0%", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_700),
        }

        self.content = ft.Column(
            [
                ft.Text("🗺️ Cartographie des caveaux", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                ft.Row(
                    [
                        ft.Card(ft.Container(ft.Column([ft.Text("Total", size=12, color=ft.Colors.GREY_600), self.stats_cards["total"]]), padding=10, width=100), elevation=4),
                        ft.Card(ft.Container(ft.Column([ft.Text("🟢 Disponibles", size=12, color=ft.Colors.GREY_600), self.stats_cards["disponibles"]]), padding=10, width=100), elevation=4),
                        ft.Card(ft.Container(ft.Column([ft.Text("🟠 Réservés", size=12, color=ft.Colors.GREY_600), self.stats_cards["reserves"]]), padding=10, width=100), elevation=4),
                        ft.Card(ft.Container(ft.Column([ft.Text("🔴 Occupés", size=12, color=ft.Colors.GREY_600), self.stats_cards["occupes"]]), padding=10, width=100), elevation=4),
                        ft.Card(ft.Container(ft.Column([ft.Text("📊 Taux occ.", size=12, color=ft.Colors.GREY_600), self.stats_cards["taux"]]), padding=10, width=110), elevation=4),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    wrap=True,
                    spacing=15,
                ),
                ft.Divider(height=20),
                self.carte_message,
                self.bouton_carte,
                ft.ElevatedButton(
                    "Retour au tableau de bord",
                    on_click=lambda e: self.go_back(),
                    icon="arrow_back",
                    bgcolor=ft.Colors.GREY_200,
                    color=ft.Colors.BLACK,
                    style=ft.ButtonStyle(text_style=ft.TextStyle(weight=ft.FontWeight.W_500)),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            expand=True,
        )

        self.container = ft.Container(
            content=self.content,
            alignment=ft.Alignment.CENTER,
            expand=True,
            padding=30,
            bgcolor=ft.Colors.GREY_50,
        )

        self.charger_donnees()

    def get_content(self):
        return self.container

    def charger_donnees(self):
        try:
            response = self.session.get(f"{API_URL}/terrains/caveaux", timeout=5)
            if response.status_code != 200:
                self.carte_message.value = f"❌ Erreur API: {response.status_code}"
                self.carte_message.color = ft.Colors.RED
                self.page.update()
                return

            caveaux = response.json()
            stats_response = self.session.get(f"{API_URL}/terrains/statistiques", timeout=5)
            stats = stats_response.json() if stats_response.status_code == 200 else {}

            self.stats_cards["total"].value = str(stats.get('total', 0))
            self.stats_cards["disponibles"].value = str(stats.get('disponibles', 0))
            self.stats_cards["reserves"].value = str(stats.get('reserves', 0))
            self.stats_cards["occupes"].value = str(stats.get('occupes', 0))
            self.stats_cards["taux"].value = f"{stats.get('taux_occupation', 0)}%"

            if caveaux:
                caveaux_avec_coords = [c for c in caveaux if c.get('latitude', 0) != 0 or c.get('longitude', 0) != 0]
                if not caveaux_avec_coords:
                    self.carte_message.value = "⚠️ Aucun caveau n'a de coordonnées valides."
                    self.carte_message.color = ft.Colors.ORANGE
                    self.bouton_carte.disabled = True
                    self.page.update()
                    return

                self.chemin_carte = self.generer_carte_html(caveaux_avec_coords)
                if self.chemin_carte:
                    self.carte_message.value = f"✅ Carte générée avec {len(caveaux_avec_coords)} caveaux."
                    self.carte_message.color = ft.Colors.GREEN
                    self.bouton_carte.disabled = False
                else:
                    self.carte_message.value = "❌ Erreur lors de la génération de la carte."
                    self.carte_message.color = ft.Colors.RED
                    self.bouton_carte.disabled = True
            else:
                self.carte_message.value = "❌ Aucun caveau trouvé."
                self.carte_message.color = ft.Colors.RED
                self.bouton_carte.disabled = True
        except Exception as e:
            self.carte_message.value = f"❌ Erreur : {e}"
            self.carte_message.color = ft.Colors.RED
            self.bouton_carte.disabled = True
            print("Erreur carte:", e)
        self.page.update()

    def generer_carte_html(self, caveaux):
        if not caveaux:
            return None
        carte = folium.Map(location=[-4.3, 15.3], zoom_start=13, tiles="OpenStreetMap")
        couleurs = {
            "DISPONIBLE": "green",
            "RESERVE": "orange",
            "OCCUPE": "red",
            "NON_EXPLOITABLE": "gray",
        }
        for caveau in caveaux:
            lat = caveau.get('latitude', 0)
            lng = caveau.get('longitude', 0)
            if lat == 0 and lng == 0:
                continue
            statut = caveau.get('statut', 'NON_EXPLOITABLE')
            couleur = couleurs.get(statut, 'gray')
            popup_html = f"""
            <b>Caveau {caveau.get('numero', 'N/A')}</b><br>
            Statut: {statut}<br>
            Bloc: {caveau.get('bloc', 'N/A')}<br>
            Superficie: {caveau.get('superficie', 'N/A')} m²
            """
            folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=couleur, icon="info-sign"),
            ).add_to(carte)
        plugins.Fullscreen().add_to(carte)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        carte.save(temp_file.name)
        return temp_file.name

    def ouvrir_carte(self, e):
        if self.chemin_carte and os.path.exists(self.chemin_carte):
            webbrowser.open(f"file://{self.chemin_carte}")
            self.carte_message.value = "🌍 Carte ouverte dans le navigateur."
            self.carte_message.color = ft.Colors.BLUE
            self.page.update()
        else:
            self.carte_message.value = "❌ Fichier carte introuvable."
            self.carte_message.color = ft.Colors.RED
            self.page.update()
# frontend/main.py
import flet as ft
import requests
from frontend.pages.login import LoginPage
from frontend.pages.dashboard import DashboardPage
from frontend.pages.carte import CartePage
from frontend.pages.creer_reservation import CreerReservationPage
from frontend.pages.gestion_reservations import GestionReservationsPage
from frontend.pages.paiement import PaiementPage
from frontend.pages.gestion_utilisateurs import GestionUtilisateursPage
from frontend.pages.historique import HistoriquePage
from frontend.pages.creer_compte import CreerComptePage

api_session = None
api_token = None  # Variable globale pour stocker le token

def get_api_session(token=None):
    global api_session, api_token
    if api_session is None:
        api_session = requests.Session()
        api_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    if token:
        api_token = token
        api_session.headers.update({'Authorization': f'Token {token}'})
    return api_session

def main(page: ft.Page):
    page.title = "Gestion Cimetière"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1200
    page.window_height = 750
    page.padding = 20

    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE_700,
            primary_container=ft.Colors.BLUE_100,
            secondary=ft.Colors.GREY_800,
            surface=ft.Colors.WHITE,
        ),
        font_family="Roboto",
    )

    user_data = {}
    content_container = ft.Column(expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # --- SWITCH FUNCTIONS ---
    def switch_to_dashboard(data, token=None):
        nonlocal user_data
        global api_token
        user_data = data
        api_token = token
        session = get_api_session(token)
        content_container.controls.clear()
        dashboard = DashboardPage(
            page,
            user_data,
            session,
            go_to_carte=switch_to_carte,
            go_to_creer_reservation=switch_to_creer_reservation,
            go_to_gestion_reservations=switch_to_gestion_reservations,
            go_to_paiement=switch_to_paiement,
            go_to_gestion_utilisateurs=switch_to_gestion_utilisateurs,
            go_to_historique=switch_to_historique,
            logout=switch_to_login
        )
        content_container.controls.append(dashboard.get_content())
        page.update()

    def switch_to_carte():
        content_container.controls.clear()
        carte = CartePage(
            page,
            get_api_session(api_token),
            go_back=lambda: switch_to_dashboard(user_data, api_token)
        )
        content_container.controls.append(carte.get_content())
        page.update()

    def switch_to_creer_reservation():
        content_container.controls.clear()
        creer = CreerReservationPage(
            page,
            get_api_session(api_token),
            go_back=lambda: switch_to_dashboard(user_data, api_token)
        )
        content_container.controls.append(creer.get_content())
        page.update()

    def switch_to_gestion_reservations():
        content_container.controls.clear()
        gestion = GestionReservationsPage(
            page,
            get_api_session(api_token),
            go_back=lambda: switch_to_dashboard(user_data, api_token)
        )
        content_container.controls.append(gestion.get_content())
        page.update()

    def switch_to_paiement():
        content_container.controls.clear()
        paiement = PaiementPage(
            page,
            get_api_session(api_token),
            go_back=lambda: switch_to_dashboard(user_data, api_token)
        )
        content_container.controls.append(paiement.get_content())
        page.update()

    def switch_to_gestion_utilisateurs():
        content_container.controls.clear()
        gestion_utilisateurs = GestionUtilisateursPage(
            page,
            get_api_session(api_token),
            go_back=lambda: switch_to_dashboard(user_data, api_token)
        )
        content_container.controls.append(gestion_utilisateurs.get_content())
        page.update()

    def switch_to_historique():
        content_container.controls.clear()
        historique = HistoriquePage(
            page,
            get_api_session(api_token),
            go_back=lambda: switch_to_dashboard(user_data, api_token)
        )
        content_container.controls.append(historique.get_content())
        page.update()

    def switch_to_creer_compte():
        content_container.controls.clear()
        creer_compte = CreerComptePage(
            page,
            get_api_session(),
            go_back=switch_to_login
        )
        content_container.controls.append(creer_compte.get_content())
        page.update()

    def switch_to_login():
        content_container.controls.clear()
        login = LoginPage(
            page,
            get_api_session(),
            on_login_success=switch_to_dashboard,
            go_to_creer_compte=switch_to_creer_compte
        )
        content_container.controls.append(login.get_content())
        page.update()

    page.add(content_container)
    switch_to_login()

if __name__ == "__main__":
    ft.run(main)
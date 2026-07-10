# frontend/pages/historique.py
import flet as ft
import requests

class HistoriquePage:
    def __init__(self, page: ft.Page, session, go_back):
        self.page = page
        self.session = session
        self.go_back = go_back
        self.status = ft.Text("", size=14, color=ft.Colors.RED_700)

        # --- En-tête ---
        header_row = ft.Row(
            [
                ft.Text("📜 Historique des réservations", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                ft.Container(expand=True),
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

        # --- Tableau avec colonnes bien dimensionnées ---
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", width=50)),
                ft.DataColumn(ft.Text("Caveau", width=90)),
                ft.DataColumn(ft.Text("Client", width=180)),
                ft.DataColumn(ft.Text("Email", width=220)),
                ft.DataColumn(ft.Text("Début", width=110)),
                ft.DataColumn(ft.Text("Fin", width=110)),
                ft.DataColumn(ft.Text("Statut", width=140, weight=ft.FontWeight.BOLD)),  # largeur 140
                ft.DataColumn(ft.Text("Créé par", width=150)),
                ft.DataColumn(ft.Text("Validé par", width=150)),
            ],
            rows=[],
            heading_row_color=ft.Colors.BLUE_50,
            heading_text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
        )

        # --- Colonne principale avec défilement vertical (autorisé) ---
        form = ft.Column(
            [header_row, ft.Divider(height=15), self.table, self.status],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            expand=True,
            scroll=ft.ScrollMode.AUTO,  # défilement vertical OK
        )

        # --- Carte large (1350px) ---
        card = ft.Card(
            content=ft.Container(
                content=form,
                padding=20,
                width=1350,  # largeur suffisante pour tout afficher
                bgcolor=ft.Colors.WHITE,
                border_radius=20,
                height=650,
            ),
            elevation=20,
            width=1350,
        )

        self.content = ft.Container(
            content=card,
            alignment=ft.Alignment.CENTER,
            expand=True,
            gradient=ft.LinearGradient(colors=[ft.Colors.BLUE_50, ft.Colors.WHITE]),
        )

        self.charger_historique()

    def get_content(self):
        return self.content

    def charger_historique(self):
        try:
            response = self.session.get("http://127.0.0.1:8000/api/reservations/historique", timeout=5)
            if response.status_code == 200:
                data = response.json()
                rows = []
                for r in data:
                    rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(str(r['id']))),
                            ft.DataCell(ft.Text(r['caveau'])),
                            ft.DataCell(ft.Text(r['client'])),
                            ft.DataCell(ft.Text(r['client_email'])),
                            ft.DataCell(ft.Text(r['date_debut'])),
                            ft.DataCell(ft.Text(r['date_fin'])),
                            ft.DataCell(ft.Text(r['statut'])),
                            ft.DataCell(ft.Text(r['cree_par'])),
                            ft.DataCell(ft.Text(r['valide_par'])),
                        ])
                    )
                self.table.rows = rows
            else:
                self.status.value = f"Erreur {response.status_code}: {response.text[:100]}"
                self.status.color = ft.Colors.RED_700
        except Exception as e:
            self.status.value = f"❌ Erreur: {e}"
            self.status.color = ft.Colors.RED_700
        self.page.update()
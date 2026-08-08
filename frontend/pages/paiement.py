# frontend/pages/paiement.py
import flet as ft

API_URL = "https://cimetiere-backend-otr7.onrender.com/api"
#API_URL = "http://127.0.0.1:8000/api"

class PaiementPage:
    def __init__(self, page: ft.Page, session, go_back):
        self.page = page
        self.session = session
        self.go_back = go_back
        self.factures = []
        self.liste_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        self.formulaire_container = ft.Container(visible=False)  # Conteneur pour le formulaire

        # En-tête
        header = ft.Row(
            [
                ft.Text("💰 Paiements", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                ft.Container(expand=True),
                ft.ElevatedButton("Retour", icon="arrow_back", on_click=lambda e: self.go_back()),
            ]
        )

        self.status = ft.Text("Chargement...", size=14, color=ft.Colors.GREY_600)

        # Contenu principal (liste + formulaire)
        self.content = ft.Container(
            content=ft.Column(
                [
                    header,
                    ft.Divider(height=10),
                    self.status,
                    self.liste_container,
                    self.formulaire_container,  # Formulaire caché par défaut
                ],
                spacing=10,
                expand=True,
            ),
            padding=20,
            expand=True,
            bgcolor=ft.Colors.GREY_50,
        )

        self.charger_factures()

    def get_content(self):
        return self.content

    def charger_factures(self):
        """Récupère les factures et affiche la liste"""
        try:
            url = f"{API_URL}/finances/factures"
            print(f"🔍 Appel : {url}")
            response = self.session.get(url, timeout=30)
            print(f"📦 Statut : {response.status_code}")

            if response.status_code == 200:
                toutes = response.json()
                print(f"📦 Nombre total : {len(toutes)}")
                self.factures = toutes
                self._afficher_liste()
                self.status.value = f"✅ {len(self.factures)} facture(s) affichée(s)"
                self.status.color = ft.Colors.GREEN_700
            else:
                self.status.value = f"❌ Erreur {response.status_code} : {response.text[:100]}"
                self.status.color = ft.Colors.RED_700

        except Exception as e:
            self.status.value = f"❌ Exception : {e}"
            self.status.color = ft.Colors.RED_700

        self.page.update()

    def _afficher_liste(self):
        """Affiche la liste des factures (masque le formulaire)"""
        self.formulaire_container.visible = False
        self.liste_container.visible = True
        self.liste_container.controls.clear()

        if not self.factures:
            self.liste_container.controls.append(
                ft.Text("✅ Aucune facture trouvée.", size=16, color=ft.Colors.GREEN_700)
            )
            self.page.update()
            return

        for facture in self.factures:
            card = self._creer_carte(facture)
            self.liste_container.controls.append(card)

        self.page.update()

    def _creer_carte(self, facture):
        statut = facture.get('statut', 'INCONNU')
        est_impayee = statut == 'EN_ATTENTE'

        return ft.Card(
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.Column([
                            ft.Text(f"Facture #{facture.get('numero_facture', 'N/A')}", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Montant : {facture.get('montant_total', 0)} FCFA", size=14),
                            ft.Text(f"Échéance : {facture.get('date_echeance', '')}", size=12, color=ft.Colors.GREY_600),
                            ft.Container(
                                content=ft.Text(statut, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                bgcolor=ft.Colors.ORANGE_700 if est_impayee else ft.Colors.GREEN_700,
                                padding=5,
                                border_radius=8,
                            ),
                        ], spacing=5, expand=True),
                        ft.ElevatedButton(
                            "💰 Payer",
                            icon="payment",
                            on_click=lambda e, fid=facture.get('id'): self._afficher_formulaire(fid),
                            bgcolor=ft.Colors.GREEN_700,
                            color=ft.Colors.WHITE,
                        ) if est_impayee else ft.Text("Payée", size=14, color=ft.Colors.GREEN_700),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=15,
            ),
            elevation=4,
            margin=5,
        )

    def _afficher_formulaire(self, facture_id):
        """Remplace la liste par le formulaire de paiement"""
        print(f"🔑 Paiement déclenché pour la facture {facture_id}")

        # Champ numéro
        numero_field = ft.TextField(
            label="Numéro Airtel",
            hint_text="Ex: 0612345678",
            width=300,
            keyboard_type=ft.KeyboardType.PHONE,
        )

        status_msg = ft.Text("", size=14, color=ft.Colors.GREY_600)

        def confirmer_paiement(e):
            numero = numero_field.value
            if not numero:
                status_msg.value = "❌ Numéro requis"
                status_msg.color = ft.Colors.RED_700
                self.page.update()
                return

            try:
                payload = {"facture_id": facture_id, "numero_telephone": numero}
                print(f"📤 Payload : {payload}")
                response = self.session.post(
                    f"{API_URL}/finances/paiements-airtel",
                    json=payload,
                    timeout=30
                )
                print(f"📦 Statut paiement : {response.status_code}")
                if response.status_code == 200:
                    status_msg.value = "✅ Paiement effectué !"
                    status_msg.color = ft.Colors.GREEN_700
                    self.page.update()
                    # Recharger la liste après 1 seconde
                    import asyncio
                    async def recharger():
                        await asyncio.sleep(1)
                        self.charger_factures()
                    self.page.run_task(recharger)
                else:
                    error = response.json().get('error', 'Erreur inconnue')
                    status_msg.value = f"❌ Erreur : {error}"
                    status_msg.color = ft.Colors.RED_700
            except Exception as ex:
                status_msg.value = f"❌ Erreur : {ex}"
                status_msg.color = ft.Colors.RED_700

            self.page.update()

        # Construction du formulaire
        formulaire = ft.Column(
            [
                ft.Text("💳 Paiement Airtel Money", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                ft.Text(f"Facture n° {facture_id}", size=14, color=ft.Colors.GREY_600),
                ft.Divider(height=10),
                ft.Text("Entrez votre numéro Airtel pour payer la facture.", size=14),
                numero_field,
                status_msg,
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "🔙 Annuler",
                            on_click=lambda e: self._afficher_liste(),
                            bgcolor=ft.Colors.GREY_300,
                            color=ft.Colors.BLACK,
                        ),
                        ft.ElevatedButton(
                            "✅ Confirmer",
                            on_click=confirmer_paiement,
                            bgcolor=ft.Colors.GREEN_700,
                            color=ft.Colors.WHITE,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=15,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        )

        # Remplacer le contenu de la liste par le formulaire
        self.liste_container.controls.clear()
        self.liste_container.controls.append(
            ft.Container(
                content=formulaire,
                padding=30,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.GREY_300),
            )
        )
        self.liste_container.visible = True
        self.status.value = "💳 Veuillez saisir votre numéro Airtel"
        self.status.color = ft.Colors.BLUE_700
        self.page.update()
        print("✅ Formulaire de paiement affiché")
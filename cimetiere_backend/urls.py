# cimetiere_backend/urls.py
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from ninja.security import SessionAuth

from users.api import router as users_router
from terrains.api import router as terrains_router
from reservations.api import router as reservations_router
from concessions.api import router as concessions_router
from finances.api import router as finances_router
from notifications.api import router as notifications_router
from public.api import router as public_router

api = NinjaAPI(
    title="Gestion Cimetiere API",
    version="1.0.0",
    description="API pour la gestion des emplacements funeraires",
    auth=SessionAuth(),
    csrf=False,
)

api.add_router("/users/", users_router, tags=["Utilisateurs"])
api.add_router("/public/", public_router, tags=["Public"])
api.add_router("/terrains/", terrains_router, tags=["Terrain"])
api.add_router("/reservations/", reservations_router, tags=["Reservations"])
api.add_router("/concessions/", concessions_router, tags=["Concessions"])
api.add_router("/finances/", finances_router, tags=["Finances"])
api.add_router("/notifications/", notifications_router, tags=["Notifications"])

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
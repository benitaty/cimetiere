# cimetiere_backend/middleware.py
from django.utils.deprecation import MiddlewareMixin

class DisableCSRFForAPI(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/api/'):
            # Désactiver la vérification CSRF pour les requêtes API
            setattr(request, '_dont_enforce_csrf_checks', True)
# cimetiere_backend/middleware.py
from django.utils.deprecation import MiddlewareMixin

class DisableCSRFForAPI(MiddlewareMixin):
    def process_request(self, request):
        # Désactiver CSRF pour toutes les routes qui commencent par /api/
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf', True)
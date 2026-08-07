# cimetiere_backend/middleware.py
from django.middleware.csrf import CsrfViewMiddleware
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from users.models import UserToken

class CustomCsrfMiddleware(CsrfViewMiddleware):
    """
    Middleware CSRF personnalisé qui ignore les requêtes commençant par /api/.
    """
    def process_request(self, request):
        # Ignorer la vérification CSRF pour toutes les routes /api/
        if request.path.startswith('/api/'):
            return None  # Ne pas appliquer la vérification CSRF
        # Appliquer la vérification CSRF normale pour les autres routes
        return super().process_request(request)


class TokenAuthMiddleware(MiddlewareMixin):
    """
    Middleware d'authentification par token pour l'API.
    """
    def process_request(self, request):
        if not request.path.startswith('/api/'):
            return None

        # Exclure les endpoints publics
        if (request.path.startswith('/api/users/signin') or
            request.path.startswith('/api/users/signin/verifier-otp') or
            request.path.startswith('/api/users/signin/renvoyer-otp') or
            request.path.startswith('/api/public/')):
            return None

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Token '):
            return JsonResponse({"error": "Token manquant ou invalide"}, status=401)

        token_key = auth_header.split(' ')[1]
        try:
            token = UserToken.objects.get(token=token_key)
            request.user = token.user
        except UserToken.DoesNotExist:
            return JsonResponse({"error": "Token invalide"}, status=401)

        return None
# cimetiere_backend/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from users.models import UserToken

class DisableCSRFForAPI(MiddlewareMixin):
    """
    Désactive la vérification CSRF pour toutes les routes commençant par /api/.
    """
    def process_request(self, request):
        if request.path.startswith('/api/'):
            # Désactiver CSRF en définissant un attribut spécial
            setattr(request, '_dont_enforce_csrf', True)
            request.csrf_processing_done = True
        return None


class TokenAuthMiddleware(MiddlewareMixin):
    """
    Middleware d'authentification par token pour l'API.
    Ignore les requêtes qui ne commencent pas par /api/.
    """
    def process_request(self, request):
        # Ne pas bloquer les requêtes qui ne sont pas destinées à l'API
        print(f"🔍 Middleware CSRF déclenché pour {request.path}")
        if not request.path.startswith('/api/'):
            return None

        # Exclure les endpoints d'authentification (publics)
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
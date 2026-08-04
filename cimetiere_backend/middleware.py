# cimetiere_backend/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from users.models import UserToken

class DisableCSRFForAPI(MiddlewareMixin):
    def process_request(self, request):
        # Désactiver CSRF pour toutes les routes qui commencent par /api/
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf', True)


class TokenAuthMiddleware(MiddlewareMixin):
    """
    Middleware d'authentification par token.
    Vérifie la présence d'un token valide dans l'en-tête Authorization.
    """
    def process_request(self, request):
        # Exclure les routes publiques et d'authentification
        if (request.path.startswith('/api/users/signin') or
            request.path.startswith('/api/users/signin/verifier-otp') or
            request.path.startswith('/api/users/signin/renvoyer-otp') or
            request.path.startswith('/api/public/') or
            request.path.startswith('/admin/')):
            return None  # Pas d'authentification requise

        # Récupérer le token depuis l'en-tête Authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Token '):
            return JsonResponse({"error": "Token manquant ou invalide"}, status=401)

        token_key = auth_header.split(' ')[1]
        try:
            token = UserToken.objects.get(token=token_key)
            # Attacher l'utilisateur à la requête pour une utilisation ultérieure
            request.user = token.user
        except UserToken.DoesNotExist:
            return JsonResponse({"error": "Token invalide"}, status=401)

        return None  # Continuer le traitement normal
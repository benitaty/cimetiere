# cimetiere_backend/middleware.py
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class DebugAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if settings.DEBUG and request.path.startswith('/admin/'):
            User = get_user_model()
            user, created = User.objects.get_or_create(
                email='admin@debug.local',
                defaults={
                    'nom': 'Debug',
                    'prenom': 'Admin',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                }
            )
            if created:
                user.set_password('debugpass')
                user.save()
            else:
                # S'assurer que l'utilisateur a les droits
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.save()

            # Assigner directement l'utilisateur à la requête
            request.user = user
            return None  # Continue le traitement normal
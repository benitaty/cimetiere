from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Zone, Bloc, Caveau

admin.site.register(Zone)
admin.site.register(Bloc)
admin.site.register(Caveau)
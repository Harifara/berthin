# projet/urls.py

from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', auth_views.LoginView.as_view(), name='login'), # Ajoutez cette ligne pour la page d'accueil
    path('', include('gestion.urls')), # Inclure les URL de l'application "etudiants"
]

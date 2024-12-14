# etudiants/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Étudiants
    path('', auth_views.LoginView.as_view(), name='login'),
    path('signup/', views.signup, name='signup'),
    path('gestion/', views.home, name='home'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='deconnexion'),  
    
    path('gestion/liste_etudiants/', views.liste_etudiants, name='liste_etudiants'),
    path('gestion/<int:pk>/', views.detail_etudiant, name='detail_etudiant'),
    path('gestion/ajouter/', views.ajouter_etudiant, name='ajouter_etudiant'),
    path('gestion/modifier/<int:pk>/', views.modifier_etudiant, name='modifier_etudiant'),
    path('gestion/supprimer/<int:pk>/', views.supprimer_etudiant, name='supprimer_etudiant'),
    
    path('gestion/list_enseignant/', views.list_enseignant, name='list_enseignant'),
    path('gestion/<int:pk>/', views.detail_enseignant, name='detail_enseignant'),
    path('gestion/ajouter_enseignant/', views.ajouter_enseignant, name='ajouter_enseignant'),
    path('gestion/modifier_enseignant/<int:pk>/', views.modifier_enseignant, name='modifier_enseignant'),
    path('gestion/supprimer_enseignant/<int:pk>/', views.supprimer_enseignant, name='supprimer_enseignant'),
    
    path('gestion/list_ue/', views.list_ue, name='list_ue'),
    path('gestion/ajouter_ue/', views.ajouter_ue, name='ajouter_ue'),
    path('gestion/modifier_ue/<int:pk>/', views.modifier_ue, name='modifier_ue'),
    path('gestion/supprimer_ue/<int:pk>/', views.supprimer_ue, name='supprimer_ue'),
    
    # path('gestion/list_cart/<int:pk>/', views.list_cart, name='list_cart'),
    # path('gestion/ajouter_cart/', views.ajouter_cart, name='ajouter_cart'),
    # path('gestion/modifier_cart/<int:pk>/', views.modifier_cart, name='modifier_cart'),
    # path('gestion/supprimer_cart/<int:pk>/', views.supprimer_cart, name='supprimer_cart'),
    
    path('gestion/list_semestre/', views.list_semestre, name='list_semestre'),
    path('gestion/ajouter_semestre/', views.ajouter_semestre, name='ajouter_semestre'),
    path('gestion/modifier_semestre/<int:pk>/', views.modifier_semestre, name='modifier_semestre'),
    path('gestion/supprimer_semestre/<int:pk>/', views.supprimer_semestre, name='supprimer_semestre'),
    
    path('gestion/list_matier/', views.list_matier, name='list_matier'),
    path('gestion/ajouter_matier/', views.ajouter_matier, name='ajouter_matier'),
    path('gestion/modifier_matier/<int:pk>/', views.modifier_matier, name='modifier_matier'),
    path('gestion/supprimer_matier/<int:pk>/', views.supprimer_matier, name='supprimer_matier'),
    
    
    path('gestion/list_niveau/', views.list_niveau, name='list_niveau'),
    path('gestion/ajouter_niveau/', views.ajouter_niveau, name='ajouter_niveau'),
    path('gestion/modifier_niveau/<int:pk>/', views.modifier_niveau, name='modifier_niveau'),
    path('gestion/supprimer_niveau/<int:pk>/', views.supprimer_niveau, name='supprimer_niveau'),
    
  
    path('gestion/list_note/', views.list_note, name='list_note'),
    path('gestion/ajouter_note/', views.ajouter_note, name='ajouter_note'),
    path('gestion/modifier_note/<int:pk>/', views.modifier_note, name='modifier_note'),
    path('gestion/supprimer_note/<int:pk>/', views.supprimer_note, name='supprimer_note'),
    path('gestion/etudiant_det/<int:pk>/', views.etudiant_det, name='etudiant_det'),
    path('get-ue/<int:semestre_id>/', views.get_ue, name='get_ue'),
    path('get-matiere/<int:ue_id>/', views.get_matiere, name='get_matiere'),
    
    # path('gestion/generate_card/<int:pk>/card/', views.generate_card_pdf, name='generate_card'),
    # path('gestion/card_view/<int:pk>/', views.card_view, name='card_view'),
    
    path('generer_carte/<int:etudiant_id>/', views.generer_carte_etudiant, name='generer_carte'),
 
   

                                                        
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

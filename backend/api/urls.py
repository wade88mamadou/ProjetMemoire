from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'patients', views.PatientViewSet)
router.register(r'professions', views.ProfessionViewSet)
router.register(r'logements', views.LogementViewSet)
router.register(r'residences', views.ResidenceViewSet)
router.register(r'comportements', views.ComportementViewSet)
router.register(r'utilisateurs', views.UtilisateurViewSet)
router.register(r'dossiers-medicaux', views.DossierMedicalViewSet)
router.register(r'rapports', views.RapportViewSet)
router.register(r'vaccins', views.VaccinViewSet)
router.register(r'infections', views.InfectionViewSet)
router.register(r'regles-conformite', views.RegleConformiteViewSet)
router.register(r'parametres-conformite', views.ParametreConformiteViewSet)
router.register(r'alertes', views.AlerteViewSet)
router.register(r'analyses', views.AnalyseViewSet)
router.register(r'resultats-analyse', views.ResultatAnalyseViewSet)
router.register(r'alimentations', views.AlimentationViewSet)
router.register(r'acces', views.AccesViewSet)

urlpatterns = [
    # URLs d'authentification
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/user/', views.UserDetailView.as_view(), name='user-detail'),
    path('auth/change-password/', views.change_password, name='change-password'),
    
    # URLs de gestion des utilisateurs (admin seulement)
    path('admin/users/', views.UserAdminViewSet.as_view(), name='admin-users'),
    path('admin/users/<int:pk>/', views.UserAdminDetailView.as_view(), name='admin-user-detail'),
    
    # URLs des autres modèles
    path('', include(router.urls)),
] 
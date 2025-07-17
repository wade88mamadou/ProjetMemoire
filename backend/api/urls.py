from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import ImportCSVView, tester_detection_seuils, mes_patients, export_patients_pdf, export_patient_pdf, export_patients_csv, export_patient_csv

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
router.register(r'demandes-exportation', views.DemandeExportationViewSet, basename='demande-exportation')

urlpatterns = [
    # Test de connexion
    path('test-connexion/', views.test_connexion, name='test-connexion'),
    # Endpoint pour la liste des médecins
    path('medecins/', views.medecins_list, name='medecins-list'),
    # Endpoint pour la liste des user_simple d'un médecin connecté
    path('mes-users-simples/', views.mes_users_simples, name='mes-users-simples'),
    
    # URLs d'authentification
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/user/', views.UserDetailView.as_view(), name='user-detail'),
    path('auth/change-password/', views.change_password, name='change-password'),
    
    # URLs de gestion des utilisateurs (admin seulement)
    path('admin/users/', views.UserAdminViewSet.as_view(), name='admin-users'),
    path('admin/users/<int:pk>/', views.UserAdminDetailView.as_view(), name='admin-user-detail'),
    
    # URLs de statistiques
    path('patient-statistics/', views.patient_statistics, name='patient-statistics'),
    
    # URLs des demandes d'exportation
    path('mes-demandes-exportation/', views.mes_demandes_exportation, name='mes-demandes-exportation'),
    path('demandes-a-traiter/', views.demandes_a_traiter, name='demandes-a-traiter'),
    path('traiter-demande-exportation/<int:demande_id>/', views.traiter_demande_exportation, name='traiter-demande-exportation'),
    path('statistiques-demandes-exportation/', views.statistiques_demandes_exportation, name='statistiques-demandes-exportation'),
    
    # URLs des statistiques spécifiques au médecin
    path('mes-patients/', views.mes_patients, name='mes-patients'),
    path('mes-dossiers-medicaux/', views.mes_dossiers_medicaux, name='mes-dossiers-medicaux'),
    path('mes-rapports/', views.mes_rapports, name='mes-rapports'),
    
    # URLs des autres modèles
    path('import-csv/', ImportCSVView.as_view(), name='import_csv'),  

    # Statistiques par maladie
    path('stats/patients-par-maladie/', views.patients_par_maladie, name='patients_par_maladie'),

    # APIs d'alertes critiques et détection
    path('alertes/detecter-seuil-medical/', views.detecter_seuil_medical, name='detecter_seuil_medical'),
    path('alertes/acces-non-autorise/', views.signaler_acces_non_autorise, name='signaler_acces_non_autorise'),
    path('alertes/suppression-accidentelle/', views.signaler_suppression_accidentelle, name='signaler_suppression_accidentelle'),
    path('alertes/violation-donnees/', views.signaler_violation_donnees, name='signaler_violation_donnees'),
    path('alertes-critiques/', views.alertes_critiques, name='alertes_critiques'),
    path('alertes/tester-detection-seuils/', tester_detection_seuils, name='tester-detection-seuils'),
    path('export/dossier-medical/<int:dossier_id>/', views.ExportDossierMedicalView.as_view(), name='export-dossier-medical'),
    path('export/resultats-analyse/<int:analyse_id>/', views.ExportResultatsAnalyseView.as_view(), name='export-resultats-analyse'),
    path('export/dossier-medical-pdf/<int:dossier_id>/', views.ExportDossierMedicalPDFView.as_view(), name='export-dossier-medical-pdf'),
    path('export/resultats-analyse-pdf/<int:analyse_id>/', views.ExportResultatsAnalysePDFView.as_view(), name='export-resultats-analyse-pdf'),
    path('rapport-audit/', views.rapport_audit, name='rapport-audit'),
    path('', include(router.urls)),
] 
urlpatterns += [
    path('mes-patients/', mes_patients, name='mes-patients'),
    path('export-patients-pdf/', export_patients_pdf, name='export-patients-pdf'),
    path('export-patient-pdf/<int:patient_id>/', export_patient_pdf, name='export-patient-pdf'),
    path('export-patient-csv/<int:patient_id>/', export_patient_csv, name='export-patient-csv'),
    path('export-patients-csv/', export_patients_csv, name='export-patients-csv'),
] 
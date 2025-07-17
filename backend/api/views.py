from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework import status, permissions
import pandas as pd
import chardet  
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import render
from django.http import HttpResponse
from .serializers import ImportSerializer

from django.contrib.auth import authenticate 
from .models import (
    Patient, Profession, Logement, Residence, Comportement, Utilisateur,
    DossierMedical, Rapport, Vaccin, Infection, RegleConformite,
    ParametreConformite, Alerte, Analyse, ResultatAnalyse, Alimentation, Acces,
    DemandeExportation
)
from .serializers import (
    PatientSerializer, ProfessionSerializer, LogementSerializer, ResidenceSerializer, ComportementSerializer,
    DossierMedicalSerializer, RapportSerializer, VaccinSerializer, InfectionSerializer, RegleConformiteSerializer,
    ParametreConformiteSerializer, AlerteSerializer, AnalyseSerializer, ResultatAnalyseSerializer, AlimentationSerializer, AccesSerializer,
    UserSerializer, LoginSerializer, UserCreateSerializer, UserUpdateSerializer,
    DemandeExportationSerializer, DemandeExportationCreateSerializer, DemandeExportationTraitementSerializer
)
from django.utils import timezone
from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from .services import DetectionSeuilsService, AuditTrailService
from .utils import log_audit, AuditAccessMixin
from .models import DossierMedical, ResultatAnalyse
import csv
from reportlab.pdfgen import canvas
from django.http import JsonResponse
from .models import Acces
from .serializers import AccesSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from django.shortcuts import get_object_or_404


# Create your views here.

@api_view(['GET'])
def test_connexion(request):
    return Response({"message": "Connexion OK entre Django et React !"})

def accueil(request):
    return HttpResponse("Bienvenue sur l'API du Dashboard !")

class PatientViewSet(AuditAccessMixin, viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    
    def perform_create(self, serializer):
        """Override pour ajouter la détection automatique des seuils"""
        patient = serializer.save()
        
        # Détecter les violations de seuils pour les données du patient
        alertes_crees = DetectionSeuilsService.detecter_violations_patient(
            patient, self.request.user
        )
        
        # Enregistrer l'audit trail
        AuditTrailService.enregistrer_acces(
            self.request.user,
            "Création patient",
            f"Patient ID: {patient.idPatient}"
        )
        
        # Log des alertes créées
        if alertes_crees:
            print(f"Alertes créées lors de la création du patient: {len(alertes_crees)}")
    
    def perform_update(self, serializer):
        """Override pour ajouter la détection automatique lors des modifications"""
        patient = serializer.save()
        
        # Détecter les violations de seuils pour les données du patient
        alertes_crees = DetectionSeuilsService.detecter_violations_patient(
            patient, self.request.user
        )
        
        # Enregistrer l'audit trail
        AuditTrailService.enregistrer_modification(
            self.request.user,
            "Modification patient",
            f"Ancien ID: {patient.idPatient}",
            f"Nouveau ID: {patient.idPatient}",
            f"Patient {patient.idPatient}"
        )
        
        # Log des alertes créées
        if alertes_crees:
            print(f"Alertes créées lors de la modification du patient: {len(alertes_crees)}")

class ProfessionViewSet(viewsets.ModelViewSet):
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer

class LogementViewSet(viewsets.ModelViewSet):
    queryset = Logement.objects.all()
    serializer_class = LogementSerializer

class ResidenceViewSet(viewsets.ModelViewSet):
    queryset = Residence.objects.all()
    serializer_class = ResidenceSerializer

class ComportementViewSet(viewsets.ModelViewSet):
    queryset = Comportement.objects.all()
    serializer_class = ComportementSerializer

class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class DossierMedicalViewSet(AuditAccessMixin, viewsets.ModelViewSet):
    queryset = DossierMedical.objects.all()
    serializer_class = DossierMedicalSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Audit : consultation d’un dossier médical
        log_audit(
            user=request.user,
            type_acces='CONSULTATION',
            donnees_concernees=f'Dossier #{getattr(instance, 'idDossier', instance.pk)}'
        )
        return super().retrieve(request, *args, **kwargs)

class RapportViewSet(AuditAccessMixin, viewsets.ModelViewSet):
    queryset = Rapport.objects.all()
    serializer_class = RapportSerializer

class VaccinViewSet(viewsets.ModelViewSet):
    queryset = Vaccin.objects.all()
    serializer_class = VaccinSerializer

class InfectionViewSet(viewsets.ModelViewSet):
    queryset = Infection.objects.all()
    serializer_class = InfectionSerializer

class RegleConformiteViewSet(viewsets.ModelViewSet):
    queryset = RegleConformite.objects.all()
    serializer_class = RegleConformiteSerializer

class ParametreConformiteViewSet(viewsets.ModelViewSet):
    queryset = ParametreConformite.objects.all()
    serializer_class = ParametreConformiteSerializer

class AlerteViewSet(viewsets.ModelViewSet):
    queryset = Alerte.objects.all()
    serializer_class = AlerteSerializer

class AnalyseViewSet(viewsets.ModelViewSet):
    queryset = Analyse.objects.all()
    serializer_class = AnalyseSerializer

class ResultatAnalyseViewSet(AuditAccessMixin, viewsets.ModelViewSet):
    queryset = ResultatAnalyse.objects.all()
    serializer_class = ResultatAnalyseSerializer
    
    def perform_create(self, serializer):
        """Override pour ajouter la détection automatique des seuils"""
        resultat = serializer.save()
        
        # Détecter les violations de seuils
        alertes_crees = DetectionSeuilsService.detecter_violations_resultat_analyse(
            resultat, self.request.user
        )
        
        # Enregistrer l'audit trail
        AuditTrailService.enregistrer_acces(
            self.request.user,
            "Création résultat d'analyse",
            f"Résultat ID: {resultat.idResultatAnalyse}"
        )
        
        # Log des alertes créées
        if alertes_crees:
            print(f"Alertes créées lors de la création du résultat d'analyse: {len(alertes_crees)}")
    
    def perform_update(self, serializer):
        """Override pour ajouter la détection automatique lors des modifications"""
        resultat = serializer.save()
        
        # Détecter les violations de seuils
        alertes_crees = DetectionSeuilsService.detecter_violations_resultat_analyse(
            resultat, self.request.user
        )
        
        # Enregistrer l'audit trail
        AuditTrailService.enregistrer_modification(
            self.request.user,
            "Modification résultat d'analyse",
            f"Ancien ID: {resultat.idResultatAnalyse}",
            f"Nouveau ID: {resultat.idResultatAnalyse}",
            f"Résultat d'analyse {resultat.idResultatAnalyse}"
        )
        
        # Log des alertes créées
        if alertes_crees:
            print(f"Alertes créées lors de la modification du résultat d'analyse: {len(alertes_crees)}")

class AlimentationViewSet(viewsets.ModelViewSet):
    queryset = Alimentation.objects.all()
    serializer_class = AlimentationSerializer

class AccesViewSet(viewsets.ModelViewSet):
    queryset = Acces.objects.all()
    serializer_class = AccesSerializer

class LoginView(APIView):
    """Vue pour la connexion utilisateur"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': 'Connexion réussie',
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            })
        
        # Gestion spéciale pour les comptes désactivés
        errors = serializer.errors
        if 'non_field_errors' in errors:
            error_data = errors['non_field_errors'][0]
            if isinstance(error_data, dict) and error_data.get('code') == 'ACCOUNT_DISABLED':
                return Response({
                    'success': False,
                    'error': error_data['error'],
                    'message': error_data['message'],
                    'code': error_data['code']
                }, status=status.HTTP_403_FORBIDDEN)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """Vue pour la déconnexion utilisateur"""
    #permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({
                'success': True,
                'message': 'Déconnexion réussie'
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Erreur lors de la déconnexion'
            }, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    """Vue pour récupérer les détails de l'utilisateur connecté"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UserAdminViewSet(generics.ListCreateAPIView):
    """Vue pour la gestion des utilisateurs (admin seulement)"""
    queryset = Utilisateur.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserCreateSerializer
    
    def get_queryset(self):
        # Exclure les admins de la liste des utilisateurs gérés
        return Utilisateur.objects.exclude(role='ADMIN').order_by('-date_joined')

class UserAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour la gestion détaillée d'un utilisateur (admin seulement)"""
    queryset = Utilisateur.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserUpdateSerializer

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """Vue pour changer le mot de passe"""
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    new_password_confirm = request.data.get('new_password_confirm')
    
    if not user.check_password(old_password):
        return Response({
            'error': 'Ancien mot de passe incorrect'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if new_password != new_password_confirm:
        return Response({
            'error': 'Les nouveaux mots de passe ne correspondent pas'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if len(new_password) < 8:
        return Response({
            'error': 'Le nouveau mot de passe doit contenir au moins 8 caractères'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(new_password)
    user.save()
    
    return Response({
        'success': True,
        'message': 'Mot de passe modifié avec succès'
    })




class ImportCSVView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def clean_value(self, value):
        """Nettoie une valeur (NaN, espaces, etc.)"""
        if pd.isna(value) or value == '' or str(value).strip() == '':
            return None
        return str(value).strip()

    def safe_float(self, value):
        """Convertit en float de manière sécurisée"""
        if pd.isna(value) or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def safe_int(self, value):
        """Convertit en int de manière sécurisée"""
        if pd.isna(value) or value == '':
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None

    def safe_bool(self, value):
        """Convertit en bool de manière sécurisée"""
        if pd.isna(value) or value == '':
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            value = value.lower().strip()
            return value in ['true', '1', 'yes', 'oui', 'vrai']
        if isinstance(value, (int, float)):
            return bool(value)
        return None

    def get_or_create_profession(self, row):
        """Crée ou récupère une profession"""
        nom_profession = self.clean_value(row.get('Job', ''))
        print(f"    Job: '{row.get('Job', 'N/A')}' -> nom_profession: '{nom_profession}'")
        if not nom_profession:
            print(f"    ✗ Pas de profession, retourne None")
            return None
        
        try:
            profession, created = Profession.objects.get_or_create(
                nomProfession=nom_profession,
                defaults={
                    'typeProfession': self.clean_value(row.get('Job_type', '')),
                    'environnementTravail': self.clean_value(row.get('Working_Env', '')),
                    'travailleDehors': self.clean_value(row.get('Outdoor_Work_type', '')),
                    'travailleSansEmploi': self.clean_value(row.get('Occup_if_jobless', '')),
                    'situationSansEmploi': self.clean_value(row.get('Occup_if_jobless', '')),
                    'revenu': self.clean_value(row.get('Incomes', '')),
                    'freqRevenu': self.clean_value(row.get('Freq_Incomes', ''))
                }
            )
            print(f"    ✓ Profession créée/récupérée: {profession} (créé: {created})")
            return profession
        except Exception as e:
            print(f"    ✗ Erreur création profession: {e}")
            return None

    def get_or_create_residence(self, row):
        """Crée ou récupère une résidence"""
        pays = self.clean_value(row.get('Place_birth', ''))
        print(f"    Place_birth: '{row.get('Place_birth', 'N/A')}' -> pays: '{pays}'")
        if not pays:
            print(f"    ✗ Pas de pays, retourne None")
            return None
        
        residence, created = Residence.objects.get_or_create(
            pays=pays,
            defaults={
                'ville': self.clean_value(row.get('Current_resid', '')),
                'quartier': self.clean_value(row.get('Current_resid', '')),
                'adresseComplete': f"{self.clean_value(row.get('Current_resid', ''))}, {pays}"
            }
        )
        return residence

    def get_or_create_logement(self, row):
        """Crée ou récupère un logement"""
        type_logement = self.clean_value(row.get('Housing_type', ''))
        if not type_logement:
            return None
        
        logement, created = Logement.objects.get_or_create(
            typeLogement=type_logement,
            defaults={
                'nombrePersonnesFoyer': self.safe_int(row.get('Nr_people_house', 0)) or 1,
                'nbMursMaisonCouverts': self.safe_int(row.get('Wall_Covered', 0)) or 0,
                'nbSolsMaisonCouverts': self.safe_int(row.get('House_Ground_Covered', 0)) or 0,
                'nbToilettesMaison': self.safe_int(row.get('Toilet_Location', 0)) or 0,
                'toilettesInterieures': self.safe_bool(row.get('Toilet_Location', '')) or False
            }
        )
        return logement

    def get_or_create_comportement(self, row):
        """Crée ou récupère un comportement"""
        lieu_repas = self.clean_value(row.get('Eating_Location', ''))
        if not lieu_repas:
            return None
        
        comportement, created = Comportement.objects.get_or_create(
            lieuRepas=lieu_repas,
            defaults={
                'mangeAvecLesMains': self.clean_value(row.get('Eating_Man', '')),
                'laveLesMainsAvantDeManger': self.clean_value(row.get('Wash_Hand_When_Eating', '')),
                'utiliseDuSavon': self.clean_value(row.get('Soab_Wash_Hand', '')),
                'laveLesMainsDesEnfants': self.clean_value(row.get('Wash_Hand_Child', '')),
                'utiliseGelHydroalcoolique': self.clean_value(row.get('Hand_Antisep_Use', ''))
            }
        )
        return comportement

    def get_or_create_alimentation(self, row):
        """Crée ou récupère une alimentation"""
        type_repas = self.clean_value(row.get('Eating_way', ''))
        if not type_repas:
            return None
        
        alimentation, created = Alimentation.objects.get_or_create(
            typeRepas=type_repas
        )
        return alimentation

    def create_patient(self, row, profession, residence, logement, comportement, alimentation):
        """Crée un patient"""
        id_code = self.clean_value(row.get('ID', ''))
        print(f"  ID_CODE: '{id_code}' (type: {type(id_code)})")
        if id_code is None or id_code == '':
            print(f"  ✗ ID_CODE vide, patient ignoré")
            return None
        
        # Vérifier si le patient existe déjà
        if Patient.objects.filter(id_code=id_code).exists():
            return Patient.objects.get(id_code=id_code)
        
        # Convertir le sexe
        sexe_value = self.clean_value(row.get('Sex', ''))
        sexe = None
        if sexe_value:
            sexe = sexe_value.lower() in ['m', 'male', '1', 'homme']
        
        patient = Patient.objects.create(
            id_code=id_code,
            sexe=sexe,
            poids=self.safe_float(row.get('weight', 0)),
            taille=self.safe_float(row.get('height', 0)),
            lieuNaissance=self.clean_value(row.get('Place_birth', '')),
            niveauEtude=self.clean_value(row.get('Edu_Level', '')),
            profession=profession,
            comportement=comportement,
            logement=logement,
            alimentation=alimentation,
            residence=residence
        )
        return patient

    def create_dossier_medical(self, patient, row):
        """Crée un dossier médical"""
        dossier, created = DossierMedical.objects.get_or_create(
            patient=patient,
            defaults={
                'dateCreation': timezone.now().date(),
                'commentaireGeneral': f"Dossier créé automatiquement pour le patient {patient.id_code}"
            }
        )
        return dossier

    def create_analyse(self, dossier, row):
        """Crée une analyse"""
        analyse, created = Analyse.objects.get_or_create(
            dossier=dossier,
            defaults={
                'typeAnalyse': 'Analyse générale',
                'dateAnalyse': timezone.now().date()
            }
        )
        return analyse

    def create_resultat_analyse(self, analyse, row):
        """Crée un résultat d'analyse"""
        # Vérifier si des données d'analyse existent
        glycemie = self.safe_float(row.get('Gluc_mM_L'))
        if glycemie is None:
            return None
        
        resultat, created = ResultatAnalyse.objects.get_or_create(
            analyse=analyse,
            defaults={
                'glycemie': glycemie,
                'cholesterol': self.safe_float(row.get('Cholesterol', 0)) or 0,
                'triglyceride': self.safe_float(row.get('Triglyceride', 0)) or 0,
                'hdl': self.safe_float(row.get('HDL', 0)) or 0,
                'ldl': self.safe_float(row.get('LDL', 0)) or 0,
                'creatinine': self.safe_float(row.get('Creatinine', 0)) or 0,
                'uree': self.safe_float(row.get('Uree', 0)) or 0,
                'proteinurie': self.safe_float(row.get('Proteinurie', 0)) or 0
            }
        )
        return resultat

    def create_alerte(self, dossier, row):
        """Crée une alerte si nécessaire"""
        alertes = []
        
        # Alerte pour diabète
        if self.clean_value(row.get('Diabetes', '')):
            alerte, created = Alerte.objects.get_or_create(
                dossier=dossier,
                typeAlerte='Diabète',
                defaults={
                    'message': 'Patient diagnostiqué avec diabète',
                    'dateAlerte': timezone.now().date()
                }
            )
            alertes.append(alerte)
        
        # Alerte pour hypertension
        ap_sys = self.safe_float(row.get('AP_Sys_mmHg'))
        if ap_sys and ap_sys > 140:
            alerte, created = Alerte.objects.get_or_create(
                dossier=dossier,
                typeAlerte='Hypertension',
                defaults={
                    'message': f'Pression artérielle élevée: {ap_sys} mmHg',
                    'dateAlerte': timezone.now().date()
                }
            )
            alertes.append(alerte)
        
        return alertes

    def create_vaccin(self, dossier, row):
        """Crée un vaccin"""
        vaccin_recu = self.clean_value(row.get('Vacc_Received', ''))
        if not vaccin_recu:
            return None
        
        vaccin, created = Vaccin.objects.get_or_create(
            dossier=dossier,
            nomVaccin=vaccin_recu,
            defaults={
                'typeVaccination': self.clean_value(row.get('Vacc_Program', '')),
                'dose': self.safe_int(row.get('Last_Vac_year', 1)) or 1
            }
        )
        return vaccin

    def create_infection(self, dossier, row):
        """Crée une infection"""
        infection_actuelle = self.clean_value(row.get('Cur_Infection1', ''))
        if not infection_actuelle:
            return None
        
        infection, created = Infection.objects.get_or_create(
            dossier=dossier,
            nomInfection=infection_actuelle,
            defaults={
                'typeInfection': self.clean_value(row.get('Cur_Infection1_type', ''))
            }
        )
        return infection

    def post(self, request):
        # Debug: afficher les fichiers reçus
        print("=== DEBUG IMPORT CSV ===")
        print(f"FILES reçus: {list(request.FILES.keys())}")
        print(f"Content-Type: {request.content_type}")
        print(f"Headers: {dict(request.headers)}")
        
        # Accepter plusieurs noms de champ pour le fichier
        file = request.FILES.get('file') or request.FILES.get('csv_file')

        if not file:
            return Response({
                "status": False,
                "message": f"Aucun fichier CSV fourni. Utilisez le champ 'file' ou 'csv_file'. Fichiers reçus: {list(request.FILES.keys())}"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Détection automatique de l'encodage avec fallback
            raw_data = file.read()
            file.seek(0)
            
            print(f"=== DEBUG ENCODAGE ===")
            print(f"Taille du fichier reçu: {len(raw_data)} bytes")
            print(f"Premiers bytes: {raw_data[:50]}")
            
            # Essayer plusieurs encodages (ISO-8859-1 en premier car c'est le plus courant pour les CSV)
            encodings_to_try = ['ISO-8859-1', 'latin-1', 'cp1252', 'windows-1252', 'utf-8']
            encoding_detected = None
            
            # D'abord essayer chardet
            try:
                detected = chardet.detect(raw_data)
                print(f"Chardet détecté: {detected}")
                if detected['confidence'] > 0.7 and detected['encoding']:
                    # Ajouter l'encodage détecté en premier s'il n'est pas déjà dans la liste
                    if detected['encoding'] not in encodings_to_try:
                        encodings_to_try.insert(0, detected['encoding'])
            except Exception as e:
                print(f"Erreur chardet: {e}")
            
            print(f"Encodages à tester: {encodings_to_try}")
            
            # Essayer chaque encodage
            for encoding in encodings_to_try:
                try:
                    file.seek(0)
                    # Lire le fichier en mode binaire d'abord
                    raw_data = file.read()
                    # Décoder avec l'encodage spécifié
                    decoded_data = raw_data.decode(encoding)
                    # Créer un StringIO object pour pandas
                    from io import StringIO
                    df = pd.read_csv(StringIO(decoded_data), sep=';')
                    encoding_detected = encoding
                    print(f"✓ Succès avec l'encodage: {encoding}")
                    print(f"  Dimensions: {df.shape}")
                    break
                except UnicodeDecodeError as e:
                    print(f"✗ {encoding}: UnicodeDecodeError - {str(e)[:50]}...")
                    continue
                except Exception as e:
                    print(f"✗ {encoding}: Exception - {str(e)[:50]}...")
                    continue
            
            if encoding_detected is None:
                return Response({
                    "status": False,
                    "message": "Impossible de lire le fichier CSV. Vérifiez l'encodage du fichier."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Vérification des colonnes requises
            required_columns = ['ID', 'Age', 'Sex', 'Place_birth', 'Edu_Level', ' weight', 'height']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response({
                    "status": False,
                    "message": f"Colonnes manquantes: {', '.join(missing_columns)}"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Statistiques
            stats = {
                'patients_created': 0,
                'patients_skipped': 0,
                'dossiers_created': 0,
                'analyses_created': 0,
                'resultats_created': 0,
                'alertes_created': 0,
                'vaccins_created': 0,
                'infections_created': 0,
                'errors': []
            }

            for index, row in df.iterrows():
                try:
                    print(f"\n=== TRAITEMENT LIGNE {index + 1} ===")
                    print(f"ID: {row.get('ID', 'N/A')}")
                    print(f"Age: {row.get('Age', 'N/A')}")
                    print(f"Sex: {row.get('Sex', 'N/A')}")
                    
                    # 1. Créer les objets de base
                    print(f"  Création des objets de base...")
                    profession = self.get_or_create_profession(row)
                    print(f"  ✓ Profession créée: {profession}")
                    
                    residence = self.get_or_create_residence(row)
                    print(f"  ✓ Residence créée: {residence}")
                    
                    logement = self.get_or_create_logement(row)
                    print(f"  ✓ Logement créé: {logement}")
                    
                    comportement = self.get_or_create_comportement(row)
                    print(f"  ✓ Comportement créé: {comportement}")
                    
                    alimentation = self.get_or_create_alimentation(row)
                    print(f"  ✓ Alimentation créée: {alimentation}")
                    
                    # 2. Créer le patient
                    patient = self.create_patient(row, profession, residence, logement, comportement, alimentation)
                    if patient:
                        stats['patients_created'] += 1
                        print(f"✓ Patient créé: {patient.id_code}")
                    else:
                        stats['patients_skipped'] += 1
                        print(f"✗ Patient ignoré")
                        continue
                    
                    # 3. Créer le dossier médical
                    dossier = self.create_dossier_medical(patient, row)
                    if dossier:
                        stats['dossiers_created'] += 1
                    
                    # 4. Créer l'analyse
                    analyse = self.create_analyse(dossier, row)
                    if analyse:
                        stats['analyses_created'] += 1
                    
                    # 5. Créer le résultat d'analyse
                    resultat = self.create_resultat_analyse(analyse, row)
                    if resultat:
                        stats['resultats_created'] += 1
                    
                    # 6. Créer les alertes
                    alertes = self.create_alerte(dossier, row)
                    stats['alertes_created'] += len(alertes)
                    
                    # 7. Créer le vaccin
                    vaccin = self.create_vaccin(dossier, row)
                    if vaccin:
                        stats['vaccins_created'] += 1
                    
                    # 8. Créer l'infection
                    infection = self.create_infection(dossier, row)
                    if infection:
                        stats['infections_created'] += 1

                except Exception as e:
                    error_msg = f"Ligne {index + 1}: {str(e)}"
                    stats['errors'].append(error_msg)
                    continue

            return Response({
                'status': True,
                'message': f"Import complet terminé avec succès!",
                'details': {
                    'encoding_used': encoding_detected,
                    'patients_created': stats['patients_created'],
                    'patients_skipped': stats['patients_skipped'],
                    'dossiers_created': stats['dossiers_created'],
                    'analyses_created': stats['analyses_created'],
                    'resultats_created': stats['resultats_created'],
                    'alertes_created': stats['alertes_created'],
                    'vaccins_created': stats['vaccins_created'],
                    'infections_created': stats['infections_created'],
                    'errors': stats['errors'][:10] if stats['errors'] else []
                }
            }, status=status.HTTP_201_CREATED)

        except UnicodeDecodeError as e:
            return Response({
                "status": False,
                "message": f"Erreur d'encodage : {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": False,
                "message": f"Erreur lors de l'importation : {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





@api_view(['GET'])
def medecins_list(request):
    """Retourne la liste des utilisateurs ayant le rôle MEDECIN"""
    medecins = Utilisateur.objects.filter(role='MEDECIN', is_active=True)
    serializer = UserSerializer(medecins, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def mes_users_simples(request):
    """Retourne la liste des user_simple rattachés au médecin connecté"""
    user = request.user
    if not hasattr(user, 'role') or user.role != 'MEDECIN':
        return Response({'detail': 'Non autorisé'}, status=403)
    users_simples = Utilisateur.objects.filter(role='user_simple', medecin=user)
    serializer = UserSerializer(users_simples, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def patient_statistics(request):
    """Statistiques des patients pour le dashboard"""
    try:
        total_patients = Patient.objects.count()
        patients_with_dossiers = Patient.objects.filter(dossiermedical__isnull=False).distinct().count()
        
        return Response({
            'total_patients': total_patients,
            'patients_with_dossiers': patients_with_dossiers,
            'patients_without_dossiers': total_patients - patients_with_dossiers
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patients_par_maladie(request):
    """
    Retourne le nombre de patients pour chaque type de maladie
    """
    try:
        # Compter les patients par type de maladie
        stats_maladies = {}
        
        # Infections actuelles - utiliser typeInfection au lieu de nomInfection
        infections = Infection.objects.values('typeInfection').annotate(
            count=Count('dossier__patient', distinct=True)
        ).filter(typeInfection__isnull=False).exclude(typeInfection='')
        
        stats_maladies['infections'] = [
            {'maladie': item['typeInfection'], 'nombre_patients': item['count']}
            for item in infections
        ]
        
        # Compter les patients avec des infections (tous types confondus)
        total_infections = Infection.objects.filter(
            typeInfection__isnull=False
        ).exclude(typeInfection='').values('dossier__patient').distinct().count()
        
        stats_maladies['total_patients_avec_infections'] = total_infections
        
        # Statistiques générales
        total_patients = Patient.objects.count()
        stats_maladies['total_patients'] = total_patients
        
        return Response({
            'success': True,
            'data': stats_maladies
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

# ===================== VUES DEMANDES D'EXPORTATION =====================

class DemandeExportationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les demandes d'exportation"""
    serializer_class = DemandeExportationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'MEDECIN':
            # Médecin : voir les demandes de ses patients
            return DemandeExportation.objects.filter(medecin=user)
        elif user.role == 'user_simple':
            # User simple : voir ses propres demandes
            return DemandeExportation.objects.filter(demandeur=user)
        else:
            # Admin : voir toutes les demandes
            return DemandeExportation.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DemandeExportationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return DemandeExportationTraitementSerializer
        return DemandeExportationSerializer
    
    def perform_create(self, serializer):
        instance = serializer.save(demandeur=self.request.user)
        # Audit : création d'une demande d'exportation
        log_audit(
            user=self.request.user,
            type_acces='DEMANDE_EXPORT',
            donnees_concernees=f"DemandeExportation #{instance.id}"
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def mes_demandes_exportation(request):
    """Récupérer les demandes d'exportation de l'utilisateur connecté"""
    try:
        user = request.user
        demandes = DemandeExportation.objects.filter(demandeur=user).order_by('-date_demande')
        serializer = DemandeExportationSerializer(demandes, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def demandes_a_traiter(request):
    """Récupérer les demandes en attente pour un médecin"""
    try:
        user = request.user
        if user.role != 'MEDECIN':
            return Response(
                {'error': 'Accès non autorisé'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        demandes = DemandeExportation.objects.filter(
            medecin=user, 
            statut='EN_ATTENTE'
        ).order_by('date_demande')
        
        serializer = DemandeExportationSerializer(demandes, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def traiter_demande_exportation(request, demande_id):
    """Traiter une demande d'exportation (approuver/refuser)"""
    try:
        user = request.user
        if user.role != 'MEDECIN':
            # Audit accès refusé
            log_audit(
                user=user,
                type_acces='REFUS',
                donnees_concernees=f"DemandeExportation #{demande_id}",
                statut='REFUSE'
            )
            return Response(
                {'error': 'Accès non autorisé'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            demande = DemandeExportation.objects.get(
                id=demande_id, 
                medecin=user, 
                statut='EN_ATTENTE'
            )
        except DemandeExportation.DoesNotExist:
            return Response(
                {'error': 'Demande non trouvée ou déjà traitée'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = DemandeExportationTraitementSerializer(
            demande, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            instance = serializer.save()
            # Audit : traitement d'une demande d'exportation
            log_audit(
                user=user,
                type_acces='TRAITEMENT_EXPORT',
                donnees_concernees=f"DemandeExportation #{instance.id}"
            )
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def statistiques_demandes_exportation(request):
    """Statistiques des demandes d'exportation pour les médecins"""
    if request.user.role != 'MEDECIN':
        return Response({'error': 'Accès réservé aux médecins'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Demandes en attente pour ce médecin
        demandes_en_attente = DemandeExportation.objects.filter(
            medecin=request.user,
            statut='EN_ATTENTE'
        ).count()
        
        # Demandes approuvées pour ce médecin
        demandes_approuvees = DemandeExportation.objects.filter(
            medecin=request.user,
            statut='APPROUVEE'
        ).count()
        
        # Demandes refusées pour ce médecin
        demandes_refusees = DemandeExportation.objects.filter(
            medecin=request.user,
            statut='REFUSEE'
        ).count()
        
        return Response({
            'demandes_en_attente': demandes_en_attente,
            'demandes_approuvees': demandes_approuvees,
            'demandes_refusees': demandes_refusees,
            'total_demandes': demandes_en_attente + demandes_approuvees + demandes_refusees
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def mes_patients(request):
    patients = Patient.objects.all()
    serializer = PatientSerializer(patients, many=True)
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_patient_csv(request, patient_id):
    import csv
    from io import StringIO
    patient = get_object_or_404(Patient, pk=patient_id)
    dossiers = patient.dossiermedical_set.order_by('-dateCreation')
    dossier = dossiers.first() if dossiers.exists() else None
    analyses = []
    if dossier:
        for analyse in dossier.analyse_set.all():
            res = ''
            if hasattr(analyse, 'resultatanalyse'):
                ra = analyse.resultatanalyse
                champs = ['glycemie', 'cholesterol', 'triglyceride', 'hdl', 'ldl', 'creatinine', 'uree', 'proteinurie']
                res = '; '.join([f"{champ}: {getattr(ra, champ, '')}" for champ in champs if hasattr(ra, champ)])
            analyses.append(f"{analyse.typeAnalyse} ({analyse.dateAnalyse}) - {res}")
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID Patient', 'Nom', 'Prénom', 'Date naissance', 'Dossier médical', 'Analyses'])
    writer.writerow([
        getattr(patient, 'idPatient', ''),
        getattr(patient, 'nom', ''),
        getattr(patient, 'prenom', ''),
        getattr(patient, 'dateNaissance', ''),
        dossier.commentaireGeneral if dossier else '',
        ' | '.join(analyses)
    ])
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="patient_{patient_id}.csv"'
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_patients_csv(request):
    patients = Patient.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="patients.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'ID Patient', 'Dossier résumé', 'Dossier date', 'Analyses', 'Résultats', 'Infections', 'Vaccins', 'Données médicales'
    ])
    for patient in patients:
        # Dossier médical principal (le plus récent)
        dossier = patient.dossiermedical_set.order_by('-dateCreation').first()
        dossier_resume = dossier.commentaireGeneral if dossier else ''
        dossier_date = dossier.dateCreation if dossier else ''
        # Analyses
        analyses = []
        resultats = []
        if dossier:
            for analyse in dossier.analyse_set.all():
                analyses.append(f"{analyse.typeAnalyse} ({analyse.dateAnalyse})")
                if hasattr(analyse, 'resultatanalyse'):
                    ra = analyse.resultatanalyse
                    res = []
                    for champ in ['glycemie', 'cholesterol', 'triglyceride', 'hdl', 'ldl', 'creatinine', 'uree', 'proteinurie']:
                        if hasattr(ra, champ):
                            res.append(f"{champ}: {getattr(ra, champ, '')}")
                    resultats.append('; '.join(res))
        # Infections
        infections = []
        if dossier:
            for inf in dossier.infection_set.all():
                infections.append(f"{inf.nomInfection} ({inf.typeInfection})")
        # Vaccins
        vaccins = []
        if dossier:
            for vac in dossier.vaccin_set.all():
                vaccins.append(f"{vac.nomVaccin} ({vac.typeVaccination}, dose {vac.dose})")
        # Données médicales
        donnees_medicales = []
        for champ in ['antecedents', 'allergies', 'traitements']:
            if hasattr(patient, champ):
                donnees_medicales.append(f"{champ}: {getattr(patient, champ, '')}")
        writer.writerow([
            getattr(patient, 'idPatient', ''),
            dossier_resume,
            dossier_date,
            ' | '.join(analyses),
            ' | '.join(resultats),
            ' | '.join(infections),
            ' | '.join(vaccins),
            ' | '.join(donnees_medicales)
        ])
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_patients_pdf(request):
    patients = Patient.objects.all()
    
    # Création de la réponse PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="patients.pdf"'
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # En-têtes du tableau
    data = [
        ['ID Patient', 'Dossier résumé', 'Dossier date', 'Analyses', 'Résultats', 'Infections', 'Vaccins', 'Données médicales']
    ]
    
    for patient in patients:
        dossier = patient.dossiermedical_set.order_by('-dateCreation').first()
        dossier_resume = dossier.commentaireGeneral if dossier else ''
        dossier_date = dossier.dateCreation if dossier else ''
        
        analyses = []
        resultats = []
        if dossier:
            for analyse in dossier.analyse_set.all():
                analyses.append(f"{analyse.typeAnalyse} ({analyse.dateAnalyse})")
                if hasattr(analyse, 'resultatanalyse'):
                    ra = analyse.resultatanalyse
                    res = []
                    for champ in ['glycemie', 'cholesterol', 'triglyceride', 'hdl', 'ldl', 'creatinine', 'uree', 'proteinurie']:
                        if hasattr(ra, champ):
                            val = getattr(ra, champ, '')
                            if val is not None:
                                res.append(f"{champ}: {val}")
                    resultats.append('; '.join(res))
        
        infections = []
        if dossier:
            for inf in dossier.infection_set.all():
                infections.append(f"{inf.nomInfection} ({inf.typeInfection})")
        
        vaccins = []
        if dossier:
            for vac in dossier.vaccin_set.all():
                vaccins.append(f"{vac.nomVaccin} ({vac.typeVaccination}, dose {vac.dose})")
        
        donnees_medicales = []
        for champ in ['antecedents', 'allergies', 'traitements']:
            if hasattr(patient, champ):
                val = getattr(patient, champ, '')
                if val:
                    donnees_medicales.append(f"{champ}: {val}")
        
        data.append([
            getattr(patient, 'idPatient', ''),
            dossier_resume,
            dossier_date,
            ' | '.join(analyses),
            ' | '.join(resultats),
            ' | '.join(infections),
            ' | '.join(vaccins),
            ' | '.join(donnees_medicales)
        ])
    
    # Création du tableau PDF
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    
    # Composition du document
    elements.append(Paragraph("Export des patients", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(table)
    doc.build(elements)
    
    # Écriture dans la réponse HTTP
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_patient_pdf(request, patient_id):
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from io import BytesIO
    patient = get_object_or_404(Patient, pk=patient_id)
    dossiers = patient.dossiermedical_set.order_by('-dateCreation')
    dossier = dossiers.first() if dossiers.exists() else None
    analyses = []
    if dossier:
        for analyse in dossier.analyse_set.all():
            # Récupérer tous les résultats d'analyse pour cette analyse
            resultats = []
            try:
                ra = analyse.resultatanalyse
                # Récupérer tous les champs du résultat d'analyse
                champs_resultats = [
                    'glycemie', 'cholesterol', 'triglyceride', 'hdl', 'ldl', 
                    'creatinine', 'uree', 'proteinurie'
                ]
                for champ in champs_resultats:
                    if hasattr(ra, champ):
                        valeur = getattr(ra, champ)
                        # Inclure même les valeurs à 0
                        resultats.append(f"{champ}: {valeur}")
                
                # Formater l'analyse avec tous ses résultats
                if resultats:
                    analyse_text = f"{analyse.typeAnalyse} ({analyse.dateAnalyse}) - {', '.join(resultats)}"
                else:
                    analyse_text = f"{analyse.typeAnalyse} ({analyse.dateAnalyse}) - Aucun résultat disponible"
                    
            except ResultatAnalyse.DoesNotExist:
                analyse_text = f"{analyse.typeAnalyse} ({analyse.dateAnalyse}) - Aucun résultat disponible"
            
            analyses.append(analyse_text)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Export du patient {getattr(patient, 'idPatient', patient_id)}", styles['Title']))
    elements.append(Spacer(1, 12))
    data = [
        ['Dossier médical', 'Analyses']
    ]
    data.append([
        dossier.commentaireGeneral if dossier else '',
        ' | '.join(analyses) if analyses else 'Aucune analyse disponible'
    ])
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="patient_{patient_id}.pdf"'
    return response

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def mes_dossiers_medicaux(request):
    """Récupérer les dossiers médicaux des patients pour le médecin ou l'utilisateur simple connecté"""
    if request.user.role not in ['MEDECIN', 'user_simple']:
        return Response({'error': 'Accès réservé'}, status=status.HTTP_403_FORBIDDEN)
    try:
        # Les deux rôles voient tous les dossiers médicaux
        dossiers = DossierMedical.objects.all()
        serializer = DossierMedicalSerializer(dossiers, many=True)
        return Response({
            'dossiers': serializer.data,
            'total_dossiers': dossiers.count()
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def mes_rapports(request):
    """Récupérer les rapports créés par le médecin connecté"""
    if request.user.role != 'MEDECIN':
        return Response({'error': 'Accès réservé aux médecins'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Le modèle Rapport n'a pas de champ medecin, donc retourner tous les rapports
        # ou créer une logique basée sur d'autres critères
        rapports = Rapport.objects.all()
        
        # Sérialiser les rapports
        serializer = RapportSerializer(rapports, many=True)
        
        return Response({
            'rapports': serializer.data,
            'total_rapports': rapports.count()
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Détection seuil médical
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def detecter_seuil_medical(request):
    """Détecte les anomalies sur les résultats médicaux et crée une alerte si besoin."""
    data = request.data
    dossier_id = data.get('dossier_id')
    valeurs = data.get('valeurs', {})  # ex: {'glycemie': 1.5, 'cholesterol': 2.1}
    utilisateur = request.user
    alertes = []
    for param in ParametreConformite.objects.all():
        value = valeurs.get(param.nom)
        if value is not None and (value < param.seuilMin or value > param.seuilMax):
            alerte = Alerte.objects.create(
                dossier_id=dossier_id,
                typeAlerte=f"Seuil critique {param.nom}",
                message=f"Valeur {value} {param.unite} hors seuil [{param.seuilMin}-{param.seuilMax}]",
                dateAlerte=timezone.now(),
                gravite='critique',
                utilisateur=utilisateur,
                donnees_concernees=param.nom,
                notifie_cdp=True
            )
            alertes.append(alerte)
    return Response(AlerteSerializer(alertes, many=True).data)

# Accès non autorisé
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def signaler_acces_non_autorise(request):
    data = request.data
    utilisateur = request.user
    cible = data.get('cible')
    raison = data.get('raison', 'Accès non autorisé détecté')
    alerte = Alerte.objects.create(
        typeAlerte="Accès non autorisé",
        message=f"{raison} sur {cible}",
        dateAlerte=timezone.now(),
        gravite='critique',
        utilisateur=utilisateur,
        donnees_concernees=cible,
        notifie_cdp=True
    )
    return Response(AlerteSerializer(alerte).data)

# Suppression accidentelle
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def signaler_suppression_accidentelle(request):
    data = request.data
    utilisateur = request.user
    donnees = data.get('donnees')
    alerte = Alerte.objects.create(
        typeAlerte="Suppression accidentelle",
        message=f"Suppression accidentelle de {donnees}",
        dateAlerte=timezone.now(),
        gravite='warning',
        utilisateur=utilisateur,
        donnees_concernees=donnees,
        notifie_cdp=True
    )
    return Response(AlerteSerializer(alerte).data)

# Violation de données
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def signaler_violation_donnees(request):
    data = request.data
    utilisateur = request.user
    details = data.get('details')
    alerte = Alerte.objects.create(
        typeAlerte="Violation de données",
        message=f"Violation de données détectée : {details}",
        dateAlerte=timezone.now(),
        gravite='critique',
        utilisateur=utilisateur,
        donnees_concernees=details,
        notifie_cdp=True
    )
    return Response(AlerteSerializer(alerte).data)

# Lister toutes les alertes critiques
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tester_detection_seuils(request):
    """
    Endpoint de test pour la détection automatique des seuils
    Permet de tester la logique sans créer de vraies données
    """
    try:
        nom_parametre = request.data.get('nom_parametre')
        valeur = request.data.get('valeur')
        
        if not nom_parametre or valeur is None:
            return Response({
                'error': 'nom_parametre et valeur sont requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Tester la détection
        alerte = DetectionSeuilsService.detecter_violation_seuil(
            nom_parametre, float(valeur), request.user
        )
        
        if alerte:
            return Response({
                'success': True,
                'message': 'Violation de seuil détectée',
                'alerte': {
                    'type': alerte.typeAlerte,
                    'message': alerte.message,
                    'gravite': alerte.gravite,
                    'notifie_cdp': alerte.notifie_cdp
                }
            })
        else:
            return Response({
                'success': True,
                'message': 'Aucune violation de seuil détectée',
                'alerte': None
            })
            
    except ValueError:
        return Response({
            'error': 'La valeur doit être un nombre'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': f'Erreur lors du test: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alertes_critiques(request):
    alertes = Alerte.objects.filter(gravite='critique').order_by('-dateAlerte')
    serializer = AlerteSerializer(alertes, many=True)
    return Response(serializer.data)

class ExportDossierMedicalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, dossier_id):
        print(f"[DEBUG] ExportDossierMedicalView appelé avec dossier_id={dossier_id} par user={request.user}")
        try:
            dossier = DossierMedical.objects.get(pk=dossier_id)
            print(f"[DEBUG] Dossier trouvé: {dossier}")
            # Génération du CSV
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename=\"dossier_{dossier_id}.csv\"'
            writer = csv.writer(response)
            writer.writerow(['Champ', 'Valeur'])
            writer.writerow(['ID', dossier.idDossier])
            writer.writerow(['Patient', dossier.patient.idPatient])
            writer.writerow(['Date création', dossier.dateCreation])
            writer.writerow(['Commentaire', dossier.commentaireGeneral])
            # Ajoute d'autres champs si besoin
            log_audit(
                user=request.user,
                type_acces='EXPORT',
                donnees_concernees=f"Export dossier médical #{dossier_id}"
            )
            print(f"[DEBUG] Export CSV réussi pour dossier_id={dossier_id}")
            return response
        except DossierMedical.DoesNotExist:
            print(f"[DEBUG] DossierMedical.DoesNotExist pour dossier_id={dossier_id}")
            return JsonResponse({'error': 'Dossier médical non trouvé'}, status=404)
        except Exception as e:
            print(f"[DEBUG] Exception dans ExportDossierMedicalView: {e}")
            return JsonResponse({'error': f"Erreur lors de l'export : {str(e)}"}, status=500)

class ExportDossierMedicalPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, dossier_id):
        print(f"[DEBUG] ExportDossierMedicalPDFView appelé avec dossier_id={dossier_id} par user={request.user}")
        try:
            dossier = DossierMedical.objects.get(pk=dossier_id)
            patient = dossier.patient
            analyses = Analyse.objects.filter(dossier=dossier)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="dossier_{dossier_id}.pdf"'
            p = canvas.Canvas(response)
            y = 800
            p.drawString(100, y, f"Dossier médical #{dossier.idDossier}")
            y -= 20
            p.drawString(100, y, f"Patient ID: {patient.idPatient}")
            y -= 20
            p.drawString(100, y, f"Date création: {dossier.dateCreation}")
            y -= 20
            p.drawString(100, y, f"Commentaire: {dossier.commentaireGeneral}")
            y -= 40
            p.drawString(100, y, "Analyses et résultats :")
            y -= 20
            if analyses.exists():
                for analyse in analyses:
                    p.drawString(120, y, f"Analyse ID: {analyse.idAnalyse} | Type: {analyse.typeAnalyse} | Date: {analyse.dateAnalyse}")
                    y -= 20
                    try:
                        resultat = analyse.resultatanalyse
                        p.drawString(140, y, f"Glycémie: {resultat.glycemie} | Cholestérol: {resultat.cholesterol} | Triglycéride: {resultat.triglyceride}")
                        y -= 20
                        p.drawString(140, y, f"HDL: {resultat.hdl} | LDL: {resultat.ldl} | Créatinine: {resultat.creatinine} | Urée: {resultat.uree} | Protéinurie: {resultat.proteinurie}")
                        y -= 30
                    except ResultatAnalyse.DoesNotExist:
                        p.drawString(140, y, "Aucun résultat d'analyse associé.")
                        y -= 30
                    if y < 100:
                        p.showPage()
                        y = 800
            else:
                p.drawString(120, y, "Aucune analyse trouvée pour ce dossier.")
            p.showPage()
            p.save()
            log_audit(
                user=request.user,
                type_acces='EXPORT',
                donnees_concernees=f"Export PDF dossier médical #{dossier_id}"
            )
            print(f"[DEBUG] Export PDF réussi pour dossier_id={dossier_id}")
            return response
        except DossierMedical.DoesNotExist:
            print(f"[DEBUG] DossierMedical.DoesNotExist pour dossier_id={dossier_id}")
            return JsonResponse({'error': 'Dossier médical non trouvé'}, status=404)
        except Exception as e:
            print(f"[DEBUG] Exception dans ExportDossierMedicalPDFView: {e}")
            return JsonResponse({'error': f"Erreur lors de l'export PDF : {str(e)}"}, status=500)

class ExportResultatsAnalyseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, analyse_id):
        print(f"[DEBUG] ExportResultatsAnalyseView appelé avec analyse_id={analyse_id} par user={request.user}")
        try:
            analyse = ResultatAnalyse.objects.get(pk=analyse_id)
            print(f"[DEBUG] Analyse trouvée: {analyse}")
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename=\"resultats_analyse_{analyse_id}.csv\"'
            writer = csv.writer(response)
            writer.writerow(['Champ', 'Valeur'])
            writer.writerow(['ID', analyse.idResultatAnalyse])
            # Correction ici : on va chercher la date via la relation Analyse
            writer.writerow(['Date analyse', analyse.analyse.dateAnalyse])
            writer.writerow(['Température', getattr(analyse, 'temperature', '-')])
            writer.writerow(['Pression Systolique', getattr(analyse, 'pressionSystolique', '-')])
            writer.writerow(['Pression Diastolique', getattr(analyse, 'pressionDiastolique', '-')])
            writer.writerow(['Glycémie', analyse.glycemie])
            writer.writerow(['Hémoglobine', getattr(analyse, 'hemoglobine', '-')])
            writer.writerow(['Globules blancs', getattr(analyse, 'globulesBlancs', '-')])
            writer.writerow(['Lymphocytes', getattr(analyse, 'lymphocytesAbsolus', '-')])
            writer.writerow(['Neutrophiles', getattr(analyse, 'neutrophilesAbsolus', '-')])
            writer.writerow(['Basophiles', getattr(analyse, 'basophilesAbsolus', '-')])
            writer.writerow(['Eosinophiles', getattr(analyse, 'eosinophilesAbsolus', '-')])
            writer.writerow(['Monocytes', getattr(analyse, 'monocytesAbsolus', '-')])
            writer.writerow(['Plaquettes', getattr(analyse, 'plaquettes', '-')])
            log_audit(
                user=request.user,
                type_acces='EXPORT',
                donnees_concernees=f"Export résultats analyse #{analyse_id}"
            )
            print(f"[DEBUG] Export CSV réussi pour analyse_id={analyse_id}")
            return response
        except ResultatAnalyse.DoesNotExist:
            print(f"[DEBUG] ResultatAnalyse.DoesNotExist pour analyse_id={analyse_id}")
            return JsonResponse({'error': "Résultat d'analyse non trouvé"}, status=404)
        except Exception as e:
            print(f"[DEBUG] Exception dans ExportResultatsAnalyseView: {e}")
            return JsonResponse({'error': f"Erreur lors de l'export : {str(e)}"}, status=500)

class ExportResultatsAnalysePDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, analyse_id):
        print(f"[DEBUG] ExportResultatsAnalysePDFView appelé avec analyse_id={analyse_id} par user={request.user}")
        try:
            analyse = ResultatAnalyse.objects.get(pk=analyse_id)
            print(f"[DEBUG] Analyse trouvée: {analyse}")
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename=\"resultats_analyse_{analyse_id}.pdf\"'
            p = canvas.Canvas(response)
            p.drawString(100, 800, f"Résultat d'analyse #{analyse.idResultatAnalyse}")
            # Correction ici : on va chercher la date via la relation Analyse
            p.drawString(100, 780, f"Date analyse: {analyse.analyse.dateAnalyse}")
            p.drawString(100, 760, f"Température: {getattr(analyse, 'temperature', '-')}")
            p.drawString(100, 740, f"Pression Systolique: {getattr(analyse, 'pressionSystolique', '-')}")
            p.drawString(100, 720, f"Pression Diastolique: {getattr(analyse, 'pressionDiastolique', '-')}")
            p.drawString(100, 700, f"Glycémie: {analyse.glycemie}")
            p.drawString(100, 680, f"Lymphocytes: {getattr(analyse, 'lymphocytesAbsolus', '-')}")
            p.drawString(100, 660, f"Neutrophiles: {getattr(analyse, 'neutrophilesAbsolus', '-')}")
            # Ajoute d'autres champs si besoin
            p.showPage()
            p.save()
            log_audit(
                user=request.user,
                type_acces='EXPORT',
                donnees_concernees=f"Export PDF résultats analyse #{analyse_id}"
            )
            print(f"[DEBUG] Export PDF réussi pour analyse_id={analyse_id}")
            return response
        except ResultatAnalyse.DoesNotExist:
            print(f"[DEBUG] ResultatAnalyse.DoesNotExist pour analyse_id={analyse_id}")
            return JsonResponse({'error': "Résultat d'analyse non trouvé"}, status=404)
        except Exception as e:
            print(f"[DEBUG] Exception dans ExportResultatsAnalysePDFView: {e}")
            return JsonResponse({'error': f"Erreur lors de l'export PDF : {str(e)}"}, status=500)

def rapport_audit(request):
    format = request.GET.get('format')

    if format == 'csv':
        return export_csv()

    elif format == 'pdf':
        return export_pdf()

    else:
        # format JSON par défaut
        acces_list = Acces.objects.all().values(
            'id', 'dateAcces', 'utilisateur__username', 'typeAcces', 'donnees_concernees'
        )
        return JsonResponse(list(acces_list), safe=False)

def export_csv():
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="rapport_audit.csv"'

        writer = csv.writer(response)
        writer.writerow(['Date', 'Utilisateur', 'Type d\'accès', 'Données concernées'])

        for acces in Acces.objects.all():
            writer.writerow([
            acces.dateAcces,
            acces.utilisateur.username if acces.utilisateur else '',
            acces.typeAcces,
            acces.donnees_concernees
        ])
        return response

def export_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []
    styles = getSampleStyleSheet()

    # Titre
    elements.append(Paragraph("Rapport d'Audit des Accès", styles['Title']))
    elements.append(Spacer(1, 12))

    # Données
    data = [['Date', 'Utilisateur', "Type d'accès", 'Données concernées']]
    for acces in Acces.objects.all():
        data.append([
            str(acces.dateAcces),
            acces.utilisateur.username if acces.utilisateur else '',
            acces.typeAcces,
            acces.donnees_concernees or ''
        ])

    # Tableau stylé
    table = Table(data, repeatRows=1, colWidths=[80, 100, 100, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    elements.append(table)

    # Pagination (numéro de page)
    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.setFont('Helvetica', 9)
        canvas.drawRightString(780, 15, text)

    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="rapport_audit.pdf"'
    return response
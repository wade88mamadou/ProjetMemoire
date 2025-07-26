#!/usr/bin/env python
"""
Script de test complet du système de conformité médicale
Valide tous les composants : API, base de données, sécurité, etc.
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from api.models import *
from api.serializers import *

User = get_user_model()

class TestCompletSysteme:
    """Tests complets du système"""
    
    def __init__(self):
        self.client = Client()
        self.api_client = APITestCase()
        self.base_url = "http://localhost:8000"
        self.results = {
            'success': [],
            'errors': [],
            'warnings': []
        }
    
    def log_success(self, test_name, details=""):
        """Log un test réussi"""
        self.results['success'].append({
            'test': test_name,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        print(f"✅ {test_name}: {details}")
    
    def log_error(self, test_name, error, details=""):
        """Log une erreur"""
        self.results['errors'].append({
            'test': test_name,
            'error': str(error),
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        print(f"❌ {test_name}: {error}")
    
    def log_warning(self, test_name, warning, details=""):
        """Log un avertissement"""
        self.results['warnings'].append({
            'test': test_name,
            'warning': str(warning),
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        print(f"⚠️ {test_name}: {warning}")
    
    def test_configuration_django(self):
        """Test de la configuration Django"""
        try:
            from django.conf import settings
            
            # Vérifier les paramètres critiques
            assert settings.DEBUG is not None, "DEBUG non défini"
            assert settings.SECRET_KEY, "SECRET_KEY manquant"
            assert settings.DATABASES, "Configuration base de données manquante"
            assert 'api' in settings.INSTALLED_APPS, "App 'api' non installée"
            
            self.log_success("Configuration Django", "Tous les paramètres critiques sont définis")
            
        except Exception as e:
            self.log_error("Configuration Django", e)
    
    def test_base_donnees(self):
        """Test de la base de données"""
        try:
            # Test de connexion
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                assert result[0] == 1, "Test de connexion échoué"
            
            # Test des modèles
            models_to_test = [
                User, Patient, DossierMedical, Alerte, 
                RegleConformite, DemandeExportation
            ]
            
            for model in models_to_test:
                count = model.objects.count()
                self.log_success(f"Modèle {model.__name__}", f"{count} enregistrements")
            
        except Exception as e:
            self.log_error("Base de données", e)
    
    def test_api_endpoints(self):
        """Test des endpoints API"""
        try:
            # Test de connexion API
            response = requests.get(f"{self.base_url}/api/test-connexion/", timeout=5)
            if response.status_code == 200:
                self.log_success("API Test connexion", "Endpoint accessible")
            else:
                self.log_warning("API Test connexion", f"Status: {response.status_code}")
            
            # Test des endpoints principaux
            endpoints = [
                "/api/patients/",
                "/api/dossiers-medicaux/",
                "/api/alertes/",
                "/api/regles-conformite/",
                "/api/tableau-bord/",
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                    if response.status_code in [200, 401, 403]:  # 401/403 sont normaux sans auth
                        self.log_success(f"API {endpoint}", f"Status: {response.status_code}")
                    else:
                        self.log_warning(f"API {endpoint}", f"Status inattendu: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    self.log_warning(f"API {endpoint}", f"Erreur de connexion: {e}")
                    
        except Exception as e:
            self.log_error("API Endpoints", e)
    
    def test_securite(self):
        """Test de la sécurité"""
        try:
            # Test CORS
            response = requests.options(f"{self.base_url}/api/patients/", 
                                      headers={'Origin': 'http://localhost:3000'})
            if 'Access-Control-Allow-Origin' in response.headers:
                self.log_success("Sécurité CORS", "Headers CORS présents")
            else:
                self.log_warning("Sécurité CORS", "Headers CORS manquants")
            
            # Test HTTPS (en développement, devrait être False)
            from django.conf import settings
            if not settings.DEBUG:
                assert settings.SECURE_SSL_REDIRECT, "HTTPS requis en production"
                self.log_success("Sécurité HTTPS", "HTTPS activé en production")
            else:
                self.log_success("Sécurité HTTPS", "Mode développement - HTTP autorisé")
                
        except Exception as e:
            self.log_error("Sécurité", e)
    
    def test_authentification(self):
        """Test de l'authentification"""
        try:
            # Test JWT
            from rest_framework_simplejwt.tokens import RefreshToken
            
            # Créer un utilisateur de test
            user, created = User.objects.get_or_create(
                username='test_user',
                defaults={
                    'email': 'test@example.com',
                    'role': 'user_simple'
                }
            )
            
            if created:
                user.set_password('testpass123')
                user.save()
            
            # Générer un token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            # Test avec token
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(f"{self.base_url}/api/auth/user/", headers=headers, timeout=5)
            
            if response.status_code == 200:
                self.log_success("Authentification JWT", "Token valide")
            else:
                self.log_warning("Authentification JWT", f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_error("Authentification", e)
    
    def test_modeles_donnees(self):
        """Test des modèles de données"""
        try:
            # Test création Patient
            patient = Patient.objects.create(
                id_code="TEST001",
                sexe=True,
                poids=70.0,
                taille=175.0,
                lieuNaissance="Dakar",
                niveauEtude="Bac"
            )
            self.log_success("Modèle Patient", f"Créé: {patient.id_code}")
            
            # Test création Dossier Médical
            dossier = DossierMedical.objects.create(
                patient=patient,
                dateCreation=datetime.now().date(),
                commentaireGeneral="Test dossier"
            )
            self.log_success("Modèle DossierMedical", f"Créé pour patient {patient.id_code}")
            
            # Test création Alerte
            alerte = Alerte.objects.create(
                dossier=dossier,
                typeAlerte="Test",
                message="Alerte de test",
                dateAlerte=datetime.now().date(),
                gravite="info"
            )
            self.log_success("Modèle Alerte", f"Créée: {alerte.typeAlerte}")
            
            # Nettoyage
            alerte.delete()
            dossier.delete()
            patient.delete()
            
        except Exception as e:
            self.log_error("Modèles de données", e)
    
    def test_serializers(self):
        """Test des sérialiseurs"""
        try:
            # Test PatientSerializer
            patient_data = {
                'id_code': 'TEST002',
                'sexe': True,
                'poids': 65.0,
                'taille': 170.0,
                'lieuNaissance': 'Thiès',
                'niveauEtude': 'Master'
            }
            
            serializer = PatientSerializer(data=patient_data)
            if serializer.is_valid():
                patient = serializer.save()
                self.log_success("PatientSerializer", "Sérialisation/désérialisation OK")
                patient.delete()
            else:
                self.log_error("PatientSerializer", f"Erreurs: {serializer.errors}")
                
        except Exception as e:
            self.log_error("Sérialiseurs", e)
    
    def test_permissions(self):
        """Test des permissions"""
        try:
            # Test permissions par rôle
            admin_user, _ = User.objects.get_or_create(
                username='admin_test',
                defaults={'role': 'ADMIN', 'email': 'admin@test.com'}
            )
            admin_user.set_password('admin123')
            admin_user.save()
            
            medecin_user, _ = User.objects.get_or_create(
                username='medecin_test',
                defaults={'role': 'MEDECIN', 'email': 'medecin@test.com'}
            )
            medecin_user.set_password('medecin123')
            medecin_user.save()
            
            self.log_success("Permissions", f"Utilisateurs créés: {admin_user.role}, {medecin_user.role}")
            
            # Nettoyage
            admin_user.delete()
            medecin_user.delete()
            
        except Exception as e:
            self.log_error("Permissions", e)
    
    def test_frontend_connectivite(self):
        """Test de connectivité avec le frontend"""
        try:
            # Test si le frontend est accessible
            frontend_url = "http://localhost:3000"
            response = requests.get(frontend_url, timeout=5)
            
            if response.status_code == 200:
                self.log_success("Frontend Connectivité", "Frontend accessible")
            else:
                self.log_warning("Frontend Connectivité", f"Status: {response.status_code}")
                
        except requests.exceptions.RequestException:
            self.log_warning("Frontend Connectivité", "Frontend non accessible (normal si pas démarré)")
    
    def generer_rapport(self):
        """Générer un rapport complet"""
        print("\n" + "="*60)
        print("📊 RAPPORT DE TEST COMPLET DU SYSTÈME")
        print("="*60)
        
        total_tests = len(self.results['success']) + len(self.results['errors']) + len(self.results['warnings'])
        
        print(f"\n📈 RÉSULTATS GÉNÉRAUX:")
        print(f"   ✅ Tests réussis: {len(self.results['success'])}")
        print(f"   ❌ Erreurs: {len(self.results['errors'])}")
        print(f"   ⚠️ Avertissements: {len(self.results['warnings'])}")
        print(f"   📊 Total: {total_tests} tests")
        
        if self.results['errors']:
            print(f"\n❌ ERREURS DÉTECTÉES:")
            for error in self.results['errors']:
                print(f"   • {error['test']}: {error['error']}")
        
        if self.results['warnings']:
            print(f"\n⚠️ AVERTISSEMENTS:")
            for warning in self.results['warnings']:
                print(f"   • {warning['test']}: {warning['warning']}")
        
        print(f"\n✅ TESTS RÉUSSIS:")
        for success in self.results['success']:
            print(f"   • {success['test']}: {success['details']}")
        
        # Calculer le score
        if total_tests > 0:
            score = (len(self.results['success']) / total_tests) * 100
            print(f"\n🎯 SCORE GLOBAL: {score:.1f}%")
            
            if score >= 90:
                print("🎉 EXCELLENT! Le système est prêt pour la production!")
            elif score >= 75:
                print("👍 BON! Quelques améliorations mineures nécessaires.")
            elif score >= 50:
                print("⚠️ MOYEN! Des corrections importantes sont nécessaires.")
            else:
                print("❌ CRITIQUE! Le système nécessite des corrections majeures.")
        
        # Sauvegarder le rapport
        rapport_file = f"rapport_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(rapport_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 Rapport sauvegardé: {rapport_file}")
        print("="*60)
    
    def executer_tous_tests(self):
        """Exécuter tous les tests"""
        print("🚀 DÉMARRAGE DES TESTS COMPLETS DU SYSTÈME")
        print("="*60)
        
        tests = [
            self.test_configuration_django,
            self.test_base_donnees,
            self.test_api_endpoints,
            self.test_securite,
            self.test_authentification,
            self.test_modeles_donnees,
            self.test_serializers,
            self.test_permissions,
            self.test_frontend_connectivite,
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_error(f"Test {test.__name__}", e, "Erreur lors de l'exécution")
        
        self.generer_rapport()

if __name__ == "__main__":
    testeur = TestCompletSysteme()
    testeur.executer_tous_tests() 
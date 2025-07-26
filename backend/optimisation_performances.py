#!/usr/bin/env python
"""
Script d'optimisation des performances du système de conformité médicale
Améliore les performances de l'API et de la base de données
"""

import os
import sys
import django
import time
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.db import connection
from django.core.cache import cache
from django.conf import settings
from api.models import *
from api.views import *
from rest_framework.test import APITestCase
from rest_framework.test import APIClient

class OptimisationPerformances:
    """Classe pour optimiser les performances du système"""
    
    def __init__(self):
        self.client = APIClient()
        self.results = {
            'optimisations': [],
            'tests_performance': [],
            'recommandations': []
        }
    
    def log_optimisation(self, nom, details, impact):
        """Log une optimisation"""
        self.results['optimisations'].append({
            'nom': nom,
            'details': details,
            'impact': impact,
            'timestamp': datetime.now().isoformat()
        })
        print(f"🔧 {nom}: {details} (Impact: {impact})")
    
    def log_test(self, nom, temps_avant, temps_apres, amelioration):
        """Log un test de performance"""
        self.results['tests_performance'].append({
            'nom': nom,
            'temps_avant': temps_avant,
            'temps_apres': temps_apres,
            'amelioration': amelioration,
            'timestamp': datetime.now().isoformat()
        })
        print(f"⚡ {nom}: {temps_avant:.3f}s → {temps_apres:.3f}s (Amélioration: {amelioration:.1f}%)")
    
    def log_recommandation(self, nom, description, priorite):
        """Log une recommandation"""
        self.results['recommandations'].append({
            'nom': nom,
            'description': description,
            'priorite': priorite,
            'timestamp': datetime.now().isoformat()
        })
        print(f"💡 {nom}: {description} (Priorité: {priorite})")
    
    def optimiser_requetes_patients(self):
        """Optimiser les requêtes des patients"""
        try:
            # Test avant optimisation
            start_time = time.time()
            patients = Patient.objects.all()
            for patient in patients[:10]:  # Test sur 10 patients
                _ = patient.profession
                _ = patient.residence
            temps_avant = time.time() - start_time
            
            # Optimisation avec select_related
            start_time = time.time()
            patients_optimises = Patient.objects.select_related('profession', 'residence').all()
            for patient in patients_optimises[:10]:
                _ = patient.profession
                _ = patient.residence
            temps_apres = time.time() - start_time
            
            amelioration = ((temps_avant - temps_apres) / temps_avant) * 100
            
            self.log_test("Requêtes Patients", temps_avant, temps_apres, amelioration)
            self.log_optimisation(
                "select_related pour Patient", 
                "Ajout de select_related pour profession et residence",
                f"Réduction de {amelioration:.1f}% du temps de requête"
            )
            
        except Exception as e:
            print(f"❌ Erreur lors de l'optimisation des patients: {e}")
    
    def optimiser_requetes_dossiers(self):
        """Optimiser les requêtes des dossiers médicaux"""
        try:
            # Test avant optimisation
            start_time = time.time()
            dossiers = DossierMedical.objects.all()
            for dossier in dossiers[:10]:
                _ = dossier.patient.profession
                _ = dossier.patient.residence
            temps_avant = time.time() - start_time
            
            # Optimisation avec select_related et prefetch_related
            start_time = time.time()
            dossiers_optimises = DossierMedical.objects.select_related(
                'patient__profession', 
                'patient__residence'
            ).prefetch_related('analyse_set', 'alerte_set').all()
            
            for dossier in dossiers_optimises[:10]:
                _ = dossier.patient.profession
                _ = dossier.patient.residence
                _ = list(dossier.analyse_set.all())
                _ = list(dossier.alerte_set.all())
            temps_apres = time.time() - start_time
            
            amelioration = ((temps_avant - temps_apres) / temps_avant) * 100
            
            self.log_test("Requêtes Dossiers", temps_avant, temps_apres, amelioration)
            self.log_optimisation(
                "select_related et prefetch_related pour DossierMedical",
                "Optimisation des relations patient, analyses et alertes",
                f"Réduction de {amelioration:.1f}% du temps de requête"
            )
            
        except Exception as e:
            print(f"❌ Erreur lors de l'optimisation des dossiers: {e}")
    
    def optimiser_cache(self):
        """Optimiser l'utilisation du cache"""
        try:
            # Test sans cache
            start_time = time.time()
            for _ in range(10):
                total_patients = Patient.objects.count()
                total_dossiers = DossierMedical.objects.count()
            temps_sans_cache = time.time() - start_time
            
            # Test avec cache
            start_time = time.time()
            for _ in range(10):
                total_patients = cache.get('total_patients')
                if total_patients is None:
                    total_patients = Patient.objects.count()
                    cache.set('total_patients', total_patients, 300)  # 5 minutes
                
                total_dossiers = cache.get('total_dossiers')
                if total_dossiers is None:
                    total_dossiers = DossierMedical.objects.count()
                    cache.set('total_dossiers', total_dossiers, 300)  # 5 minutes
            temps_avec_cache = time.time() - start_time
            
            amelioration = ((temps_sans_cache - temps_avec_cache) / temps_sans_cache) * 100
            
            self.log_test("Cache Statistiques", temps_sans_cache, temps_avec_cache, amelioration)
            self.log_optimisation(
                "Cache pour statistiques",
                "Mise en cache des statistiques fréquemment utilisées",
                f"Réduction de {amelioration:.1f}% du temps de calcul"
            )
            
        except Exception as e:
            print(f"❌ Erreur lors de l'optimisation du cache: {e}")
    
    def optimiser_index_base_donnees(self):
        """Optimiser les index de la base de données"""
        try:
            # Vérifier les index existants
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT indexname, tablename 
                    FROM pg_indexes 
                    WHERE tablename IN ('api_patient', 'api_dossiermedical', 'api_alerte')
                    ORDER BY tablename, indexname;
                """)
                index_existants = cursor.fetchall()
            
            self.log_optimisation(
                "Vérification des index",
                f"Trouvé {len(index_existants)} index existants",
                "Base pour l'optimisation"
            )
            
            # Recommandations d'index
            index_recommandes = [
                "CREATE INDEX IF NOT EXISTS idx_patient_id_code ON api_patient(id_code);",
                "CREATE INDEX IF NOT EXISTS idx_patient_sexe ON api_patient(sexe);",
                "CREATE INDEX IF NOT EXISTS idx_dossier_date_creation ON api_dossiermedical(dateCreation);",
                "CREATE INDEX IF NOT EXISTS idx_alerte_date_gravite ON api_alerte(dateAlerte, gravite);",
                "CREATE INDEX IF NOT EXISTS idx_alerte_gravite ON api_alerte(gravite);",
            ]
            
            for index_sql in index_recommandes:
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(index_sql)
                    self.log_optimisation(
                        "Création d'index",
                        index_sql,
                        "Amélioration des performances de requête"
                    )
                except Exception as e:
                    print(f"⚠️ Index déjà existant ou erreur: {e}")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'optimisation des index: {e}")
    
    def optimiser_pagination(self):
        """Optimiser la pagination"""
        try:
            # Test pagination par défaut
            start_time = time.time()
            patients = Patient.objects.all()
            page_size = 20
            for i in range(0, min(100, patients.count()), page_size):
                page = patients[i:i+page_size]
                _ = list(page)
            temps_avant = time.time() - start_time
            
            # Test pagination optimisée
            start_time = time.time()
            patients_optimises = Patient.objects.select_related('profession', 'residence').all()
            for i in range(0, min(100, patients_optimises.count()), page_size):
                page = patients_optimises[i:i+page_size]
                _ = list(page)
            temps_apres = time.time() - start_time
            
            amelioration = ((temps_avant - temps_apres) / temps_avant) * 100
            
            self.log_test("Pagination", temps_avant, temps_apres, amelioration)
            self.log_optimisation(
                "Pagination optimisée",
                "Combinaison de select_related avec pagination",
                f"Réduction de {amelioration:.1f}% du temps de pagination"
            )
            
        except Exception as e:
            print(f"❌ Erreur lors de l'optimisation de la pagination: {e}")
    
    def analyser_requetes_lentes(self):
        """Analyser les requêtes lentes"""
        try:
            # Activer le logging des requêtes
            from django.db import connection
            from django.test.utils import override_settings
            
            with override_settings(DEBUG=True):
                # Effectuer quelques requêtes
                Patient.objects.count()
                DossierMedical.objects.select_related('patient').all()[:10]
                Alerte.objects.filter(gravite='critique').count()
                
                # Analyser les requêtes
                queries = connection.queries
                requetes_lentes = [q for q in queries if float(q['time']) > 0.1]
                
                if requetes_lentes:
                    self.log_optimisation(
                        "Détection requêtes lentes",
                        f"Trouvé {len(requetes_lentes)} requêtes > 100ms",
                        "Optimisation ciblée nécessaire"
                    )
                    
                    for i, query in enumerate(requetes_lentes[:3]):
                        self.log_recommandation(
                            f"Requête lente #{i+1}",
                            f"SQL: {query['sql'][:100]}... (Temps: {query['time']}s)",
                            "Haute"
                        )
                else:
                    self.log_optimisation(
                        "Analyse requêtes",
                        "Aucune requête lente détectée",
                        "Performance satisfaisante"
                    )
                    
        except Exception as e:
            print(f"❌ Erreur lors de l'analyse des requêtes: {e}")
    
    def generer_recommandations(self):
        """Générer des recommandations d'optimisation"""
        recommandations = [
            {
                'nom': 'Cache Redis',
                'description': 'Implémenter Redis pour le cache des statistiques et données fréquemment accédées',
                'priorite': 'Haute'
            },
            {
                'nom': 'CDN pour assets statiques',
                'description': 'Utiliser un CDN pour servir les fichiers CSS/JS du frontend',
                'priorite': 'Moyenne'
            },
            {
                'nom': 'Compression GZIP',
                'description': 'Activer la compression GZIP pour réduire la taille des réponses API',
                'priorite': 'Haute'
            },
            {
                'nom': 'Database connection pooling',
                'description': 'Configurer le pooling de connexions pour PostgreSQL',
                'priorite': 'Moyenne'
            },
            {
                'nom': 'Monitoring des performances',
                'description': 'Implémenter APM (Application Performance Monitoring)',
                'priorite': 'Basse'
            }
        ]
        
        for rec in recommandations:
            self.log_recommandation(rec['nom'], rec['description'], rec['priorite'])
    
    def generer_rapport(self):
        """Générer un rapport d'optimisation"""
        print("\n" + "="*60)
        print("🚀 RAPPORT D'OPTIMISATION DES PERFORMANCES")
        print("="*60)
        
        print(f"\n📊 RÉSULTATS:")
        print(f"   🔧 Optimisations appliquées: {len(self.results['optimisations'])}")
        print(f"   ⚡ Tests de performance: {len(self.results['tests_performance'])}")
        print(f"   💡 Recommandations: {len(self.results['recommandations'])}")
        
        if self.results['tests_performance']:
            print(f"\n⚡ AMÉLIORATIONS DE PERFORMANCE:")
            total_amelioration = 0
            for test in self.results['tests_performance']:
                print(f"   • {test['nom']}: {test['amelioration']:.1f}% d'amélioration")
                total_amelioration += test['amelioration']
            
            moyenne_amelioration = total_amelioration / len(self.results['tests_performance'])
            print(f"   📈 Amélioration moyenne: {moyenne_amelioration:.1f}%")
        
        print(f"\n💡 RECOMMANDATIONS PRIORITAIRES:")
        recommandations_haute = [r for r in self.results['recommandations'] if r['priorite'] == 'Haute']
        for rec in recommandations_haute:
            print(f"   🔴 {rec['nom']}: {rec['description']}")
        
        # Sauvegarder le rapport
        import json
        rapport_file = f"rapport_optimisation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(rapport_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 Rapport sauvegardé: {rapport_file}")
        print("="*60)
    
    def executer_optimisations(self):
        """Exécuter toutes les optimisations"""
        print("🚀 DÉMARRAGE DES OPTIMISATIONS DE PERFORMANCE")
        print("="*60)
        
        optimisations = [
            self.optimiser_requetes_patients,
            self.optimiser_requetes_dossiers,
            self.optimiser_cache,
            self.optimiser_index_base_donnees,
            self.optimiser_pagination,
            self.analyser_requetes_lentes,
        ]
        
        for optimisation in optimisations:
            try:
                optimisation()
            except Exception as e:
                print(f"❌ Erreur lors de {optimisation.__name__}: {e}")
        
        self.generer_recommandations()
        self.generer_rapport()

if __name__ == "__main__":
    optimiseur = OptimisationPerformances()
    optimiseur.executer_optimisations() 
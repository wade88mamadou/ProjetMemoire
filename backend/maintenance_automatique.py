#!/usr/bin/env python
"""
Script de maintenance automatique pour le système de conformité médicale
À exécuter quotidiennement via cron
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.core.cache import cache
from django.db import connection
from api.models import Alerte, Acces, DemandeExportation

def nettoyer_cache():
    """Nettoyer le cache expiré"""
    print("🧹 Nettoyage du cache...")
    # Le cache Django se nettoie automatiquement
    
def nettoyer_logs_anciens():
    """Nettoyer les logs anciens"""
    print("📋 Nettoyage des logs anciens...")
    # Supprimer les alertes de plus de 1 an
    date_limite = datetime.now().date() - timedelta(days=365)
    alertes_supprimees = Alerte.objects.filter(dateAlerte__lt=date_limite).count()
    Alerte.objects.filter(dateAlerte__lt=date_limite).delete()
    print(f"   {alertes_supprimees} alertes anciennes supprimées")

def optimiser_base_donnees():
    """Optimiser la base de données"""
    print("🗄️ Optimisation de la base de données...")
    with connection.cursor() as cursor:
        cursor.execute("VACUUM ANALYZE;")
    print("   VACUUM ANALYZE terminé")

def verifier_integrite():
    """Vérifier l'intégrité des données"""
    print("🔍 Vérification de l'intégrité...")
    
    # Vérifier les dossiers orphelins
    dossiers_orphelins = DossierMedical.objects.filter(patient__isnull=True).count()
    if dossiers_orphelins > 0:
        print(f"   ⚠️ {dossiers_orphelins} dossiers orphelins détectés")
    
    # Vérifier les demandes d'exportation expirées
    demandes_expirees = DemandeExportation.objects.filter(
        statut='EN_ATTENTE',
        date_demande__lt=datetime.now() - timedelta(days=30)
    ).count()
    if demandes_expirees > 0:
        print(f"   ⚠️ {demandes_expirees} demandes d'exportation expirées")

def main():
    """Fonction principale"""
    print(f"🚀 Maintenance automatique - {datetime.now()}")
    print("="*50)
    
    nettoyer_cache()
    nettoyer_logs_anciens()
    optimiser_base_donnees()
    verifier_integrite()
    
    print("✅ Maintenance terminée avec succès")

if __name__ == "__main__":
    main()

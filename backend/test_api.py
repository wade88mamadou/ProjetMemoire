#!/usr/bin/env python
import os
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

def test_api_endpoints():
    """Teste les endpoints API pour vérifier les statistiques"""
    
    base_url = "http://localhost:8000/api"
    
    # Endpoints à tester
    endpoints = [
        "/patients/",
        "/utilisateurs/",
        "/alertes/",
        "/dossiers-medicaux/",
        "/analyses/",
        "/resultats-analyse/",
        "/vaccins/",
        "/infections/",
        "/professions/",
        "/residences/",
        "/logements/",
        "/comportements/",
        "/alimentations/"
    ]
    
    print("=== TEST DES ENDPOINTS API ===\n")
    
    for endpoint in endpoints:
        try:
            url = base_url + endpoint
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else "N/A"
                print(f"✅ {endpoint}: {count} éléments")
            else:
                print(f"❌ {endpoint}: Erreur {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint}: Erreur - {e}")
    
    print("\n=== STATISTIQUES RÉSUMÉ ===")
    
    # Calculer les statistiques principales
    try:
        patients = requests.get(f"{base_url}/patients/").json()
        users = requests.get(f"{base_url}/utilisateurs/").json()
        alertes = requests.get(f"{base_url}/alertes/").json()
        dossiers = requests.get(f"{base_url}/dossiers-medicaux/").json()
        analyses = requests.get(f"{base_url}/analyses/").json()
        
        print(f"👥 Total Utilisateurs: {len(users)}")
        print(f"🏥 Total Patients: {len(patients)}")
        print(f"📋 Total Dossiers Médicaux: {len(dossiers)}")
        print(f"🔬 Total Analyses: {len(analyses)}")
        print(f"⚠️  Total Alertes: {len(alertes)}")
        
    except Exception as e:
        print(f"Erreur lors du calcul des statistiques: {e}")

if __name__ == "__main__":
    test_api_endpoints() 
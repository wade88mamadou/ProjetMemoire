#!/usr/bin/env python
"""
Script de test pour la détection automatique des seuils médicaux
Permet de tester la logique sans avoir besoin de l'interface web
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from api.models import RegleConformite, ParametreConformite, Utilisateur
from api.services import DetectionSeuilsService

def creer_donnees_test():
    """Crée des données de test pour les seuils médicaux"""
    print("🔧 Création des données de test...")
    
    # Créer une règle de conformité
    regle, created = RegleConformite.objects.get_or_create(
        nomRegle="Surveillance paramètres vitaux",
        defaults={
            'description': "Règle pour surveiller les paramètres vitaux des patients",
            'typeRegle': "RGPD",
            'niveauCritique': 3
        }
    )
    
    if created:
        print(f"✅ Règle créée: {regle.nomRegle}")
    else:
        print(f"📋 Règle existante: {regle.nomRegle}")
    
    # Créer des paramètres de test
    parametres_test = [
        {
            'nom': 'Glycémie',
            'seuilMin': 70,
            'seuilMax': 110,
            'unite': 'mg/dL'
        },
        {
            'nom': 'Température',
            'seuilMin': 36,
            'seuilMax': 37.5,
            'unite': '°C'
        },
        {
            'nom': 'Poids',
            'seuilMin': 40,
            'seuilMax': 150,
            'unite': 'kg'
        }
    ]
    
    for param_data in parametres_test:
        parametre, created = ParametreConformite.objects.get_or_create(
            nom=param_data['nom'],
            defaults={
                'seuilMin': param_data['seuilMin'],
                'seuilMax': param_data['seuilMax'],
                'unite': param_data['unite'],
                'regle': regle
            }
        )
        
        if created:
            print(f"✅ Paramètre créé: {parametre.nom} ({parametre.seuilMin}-{parametre.seuilMax} {parametre.unite})")
        else:
            print(f"📋 Paramètre existant: {parametre.nom}")

def tester_detection():
    """Teste la détection de seuils avec différentes valeurs"""
    print("\n🧪 Test de la détection automatique...")
    
    # Récupérer un utilisateur pour les tests
    try:
        utilisateur = Utilisateur.objects.first()
        if not utilisateur:
            print("⚠️  Aucun utilisateur trouvé, création d'un utilisateur de test...")
            utilisateur = Utilisateur.objects.create_user(
                username='test_user',
                password='test123',
                email='test@example.com'
            )
    except Exception as e:
        print(f"❌ Erreur lors de la récupération/création de l'utilisateur: {e}")
        return
    
    # Tests de détection
    tests = [
        ('Glycémie', 50, "Valeur en dessous du seuil minimum"),
        ('Glycémie', 80, "Valeur normale"),
        ('Glycémie', 120, "Valeur au-dessus du seuil maximum"),
        ('Température', 35, "Température trop basse"),
        ('Température', 36.5, "Température normale"),
        ('Température', 39, "Température élevée"),
        ('Poids', 30, "Poids très faible"),
        ('Poids', 70, "Poids normal"),
        ('Poids', 200, "Poids très élevé"),
    ]
    
    for nom_parametre, valeur, description in tests:
        print(f"\n🔍 Test: {description}")
        print(f"   Paramètre: {nom_parametre}, Valeur: {valeur}")
        
        try:
            alerte = DetectionSeuilsService.detecter_violation_seuil(
                nom_parametre, valeur, utilisateur
            )
            
            if alerte:
                print(f"   ⚠️  ALERTE CRÉÉE:")
                print(f"      Type: {alerte.typeAlerte}")
                print(f"      Message: {alerte.message}")
                print(f"      Gravité: {alerte.gravite}")
                print(f"      Notification CDP: {alerte.notifie_cdp}")
            else:
                print(f"   ✅ Aucune alerte - valeur dans les normes")
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")

def afficher_statistiques():
    """Affiche les statistiques des alertes créées"""
    print("\n📊 Statistiques des alertes...")
    
    from api.models import Alerte
    
    total_alertes = Alerte.objects.count()
    alertes_critiques = Alerte.objects.filter(gravite='critique').count()
    alertes_warning = Alerte.objects.filter(gravite='warning').count()
    alertes_info = Alerte.objects.filter(gravite='info').count()
    alertes_cdp = Alerte.objects.filter(notifie_cdp=True).count()
    
    print(f"   Total alertes: {total_alertes}")
    print(f"   Alertes critiques: {alertes_critiques}")
    print(f"   Alertes warning: {alertes_warning}")
    print(f"   Alertes info: {alertes_info}")
    print(f"   Alertes CDP: {alertes_cdp}")
    
    if total_alertes > 0:
        print("\n   Dernières alertes:")
        for alerte in Alerte.objects.order_by('-dateAlerte')[:5]:
            print(f"      - {alerte.dateAlerte}: {alerte.typeAlerte} ({alerte.gravite})")

def main():
    """Fonction principale"""
    print("🚀 Test de la détection automatique des seuils médicaux")
    print("=" * 60)
    
    try:
        # Créer les données de test
        creer_donnees_test()
        
        # Tester la détection
        tester_detection()
        
        # Afficher les statistiques
        afficher_statistiques()
        
        print("\n✅ Test terminé avec succès!")
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 
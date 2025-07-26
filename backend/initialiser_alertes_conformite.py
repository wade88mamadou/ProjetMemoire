#!/usr/bin/env python
"""
Script d'initialisation du système d'alertes de conformité RGPD/HIPAA/CDP
"""

import os
import sys
import django
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from api.services_conformite import ServiceAlertesConformite
from api.models import TypeAlerteConformite, RegleAlerteConformite

def initialiser_systeme_alertes():
    """Initialise le système complet d'alertes de conformité"""
    
    print("🚀 INITIALISATION DU SYSTÈME D'ALERTES DE CONFORMITÉ")
    print("="*60)
    
    # 1. Initialiser les types d'alertes
    print("\n📋 1. Initialisation des types d'alertes...")
    ServiceAlertesConformite.initialiser_types_alertes()
    
    types_alertes = TypeAlerteConformite.objects.all()
    print(f"   ✅ {types_alertes.count()} types d'alertes créés")
    
    # Afficher les types par norme
    for norme in ['RGPD', 'HIPAA', 'CDP', 'GENERAL']:
        count = types_alertes.filter(norme_conformite=norme).count()
        print(f"      • {norme}: {count} types")
    
    # 2. Créer des règles d'alertes par défaut
    print("\n⚙️ 2. Création des règles d'alertes par défaut...")
    
    regles_defaut = [
        {
            'nom': 'Surveillance accès non autorisés',
            'description': 'Détecte les tentatives d\'accès non autorisées',
            'type_alerte_code': 'ACCES_NON_AUTORISE',
            'seuil_min': 1,
            'action_automatique': 'NOTIFICATION',
            'notifier_admin': True,
            'notifier_dpo': True
        },
        {
            'nom': 'Surveillance consultations excessives',
            'description': 'Détecte les consultations excessives de dossiers',
            'type_alerte_code': 'CONSULTATION_EXCESSIVE',
            'seuil_max': 50,
            'periode_surveillance': 1,
            'action_automatique': 'NOTIFICATION',
            'notifier_admin': True
        },
        {
            'nom': 'Surveillance violations RGPD',
            'description': 'Détecte les violations de données personnelles',
            'type_alerte_code': 'RGPD_VIOLATION_DONNEES',
            'action_automatique': 'ESCALADER',
            'notifier_admin': True,
            'notifier_dpo': True,
            'notifier_cdp': True
        },
        {
            'nom': 'Surveillance violations HIPAA',
            'description': 'Détecte les accès non autorisés aux PHI',
            'type_alerte_code': 'HIPAA_PHI_ACCES_NON_AUTORISE',
            'action_automatique': 'BLOQUER_ACCES',
            'notifier_admin': True,
            'notifier_dpo': True
        },
        {
            'nom': 'Surveillance violations CDP',
            'description': 'Détecte les violations du secret médical',
            'type_alerte_code': 'CDP_SECRET_MEDICAL_VIOLATION',
            'action_automatique': 'ESCALADER',
            'notifier_admin': True,
            'notifier_cdp': True
        }
    ]
    
    regles_crees = 0
    for regle_data in regles_defaut:
        try:
            type_alerte = TypeAlerteConformite.objects.get(code=regle_data['type_alerte_code'])
            
            regle, created = RegleAlerteConformite.objects.get_or_create(
                nom=regle_data['nom'],
                defaults={
                    'description': regle_data['description'],
                    'type_alerte': type_alerte,
                    'seuil_min': regle_data.get('seuil_min'),
                    'seuil_max': regle_data.get('seuil_max'),
                    'periode_surveillance': regle_data.get('periode_surveillance', 24),
                    'action_automatique': regle_data['action_automatique'],
                    'notifier_admin': regle_data.get('notifier_admin', True),
                    'notifier_dpo': regle_data.get('notifier_dpo', False),
                    'notifier_cdp': regle_data.get('notifier_cdp', False),
                    'is_active': True
                }
            )
            
            if created:
                regles_crees += 1
                print(f"   ✅ Règle créée: {regle.nom}")
            else:
                print(f"   ⚠️ Règle existante: {regle.nom}")
                
        except TypeAlerteConformite.DoesNotExist:
            print(f"   ❌ Type d'alerte non trouvé: {regle_data['type_alerte_code']}")
        except Exception as e:
            print(f"   ❌ Erreur création règle {regle_data['nom']}: {e}")
    
    print(f"   📊 {regles_crees} nouvelles règles créées")
    
    # 3. Tester la surveillance
    print("\n🔍 3. Test de la surveillance de conformité...")
    try:
        alertes_crees = ServiceAlertesConformite.executer_surveillance_conformite()
        print(f"   ✅ Surveillance testée: {len(alertes_crees)} alertes créées")
    except Exception as e:
        print(f"   ❌ Erreur lors du test: {e}")
    
    # 4. Afficher les statistiques
    print("\n📊 4. Statistiques du système...")
    try:
        stats = ServiceAlertesConformite.obtenir_statistiques_conformite()
        print(f"   • Total alertes: {stats.get('total_alertes', 0)}")
        print(f"   • Alertes nouvelles: {stats.get('alertes_nouvelles', 0)}")
        print(f"   • Alertes RGPD: {stats.get('alertes_rgpd', 0)}")
        print(f"   • Alertes HIPAA: {stats.get('alertes_hipaa', 0)}")
        print(f"   • Alertes CDP: {stats.get('alertes_cdp', 0)}")
    except Exception as e:
        print(f"   ❌ Erreur statistiques: {e}")
    
    # 5. Configuration recommandée
    print("\n⚙️ 5. Configuration recommandée...")
    config_recommandee = {
        'activation_surveillance': True,
        'delai_notification_defaut': 24,
        'escalation_automatique': True,
        'seuil_acces_non_autorise': 3,
        'seuil_consultation_excessive': 50,
        'seuil_modification_non_autorisee': 2,
        'notifier_admin_par_defaut': True,
        'notifier_dpo_par_defaut': False,
        'notifier_cdp_par_defaut': False,
        'bloquer_acces_automatique': False,
        'fermer_session_automatique': False,
        'logger_toutes_actions': True
    }
    
    from django.core.cache import cache
    cache.set('config_alertes_conformite', config_recommandee, 3600)
    print("   ✅ Configuration par défaut sauvegardée")
    
    print("\n" + "="*60)
    print("🎉 SYSTÈME D'ALERTES DE CONFORMITÉ INITIALISÉ AVEC SUCCÈS!")
    print("="*60)
    
    print("\n📋 RÉCAPITULATIF:")
    print(f"   • Types d'alertes: {TypeAlerteConformite.objects.count()}")
    print(f"   • Règles actives: {RegleAlerteConformite.objects.filter(is_active=True).count()}")
    print(f"   • Configuration: Sauvegardée")
    
    print("\n🚀 PROCHAINES ÉTAPES:")
    print("   1. Configurer les notifications email/SMS")
    print("   2. Définir les seuils spécifiques à votre organisation")
    print("   3. Former les utilisateurs sur les alertes")
    print("   4. Mettre en place la surveillance automatique")
    
    print("\n📚 DOCUMENTATION:")
    print("   • API Endpoints: /api/conformite/")
    print("   • Interface: /admin/")
    print("   • Rapports: /api/conformite/rapport/")
    
    return True

if __name__ == "__main__":
    try:
        initialiser_systeme_alertes()
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        sys.exit(1) 
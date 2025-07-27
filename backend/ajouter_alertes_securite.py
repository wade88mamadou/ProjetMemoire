#!/usr/bin/env python
"""
Script pour ajouter les nouvelles alertes de sécurité à l'ancien système
Ajoute les alertes manquantes : accès non autorisé, fuite de données, etc.
"""

import os
import sys
import django
from django.utils import timezone

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from api.models import RegleConformite, ParametreConformite, TypeAlerteConformite, RegleAlerteConformite

def ajouter_alertes_securite():
    """Ajoute les nouvelles alertes de sécurité à l'ancien système"""
    
    print("🔒 AJOUT DES NOUVELLES ALERTES DE SÉCURITÉ")
    print("=" * 50)
    
    # 1. Créer les nouveaux types d'alertes de sécurité
    types_alertes_securite = [
        {
            'code': 'ACCES_NON_AUTORISE',
            'nom': 'Accès non autorisé',
            'description': 'Détection d\'un accès non autorisé au système ou aux données médicales',
            'norme_conformite': 'GENERAL',
            'niveau_critique': 4,
            'delai_notification': 1
        },
        {
            'code': 'FUITES_DONNEES',
            'nom': 'Fuite de données',
            'description': 'Détection d\'une possible fuite de données médicales sensibles',
            'norme_conformite': 'RGPD',
            'niveau_critique': 5,
            'delai_notification': 1
        },
        {
            'code': 'TENTATIVE_INTRUSION',
            'nom': 'Tentative d\'intrusion',
            'description': 'Détection de tentatives d\'intrusion dans le système',
            'norme_conformite': 'GENERAL',
            'niveau_critique': 4,
            'delai_notification': 2
        },
        {
            'code': 'EXPORT_NON_AUTORISE',
            'nom': 'Export non autorisé',
            'description': 'Tentative d\'export de données sans autorisation',
            'norme_conformite': 'RGPD',
            'niveau_critique': 4,
            'delai_notification': 2
        },
        {
            'code': 'MODIFICATION_CRITIQUE',
            'nom': 'Modification critique non autorisée',
            'description': 'Modification de données critiques sans autorisation',
            'norme_conformite': 'HIPAA',
            'niveau_critique': 4,
            'delai_notification': 2
        },
        {
            'code': 'SUPPRESSION_MASSE',
            'nom': 'Suppression en masse',
            'description': 'Suppression de multiples dossiers médicaux',
            'norme_conformite': 'HIPAA',
            'niveau_critique': 5,
            'delai_notification': 1
        },
        {
            'code': 'CONNEXION_SUSPICIEUSE',
            'nom': 'Connexion suspecte',
            'description': 'Connexion depuis une adresse IP ou un appareil suspect',
            'norme_conformite': 'GENERAL',
            'niveau_critique': 3,
            'delai_notification': 6
        },
        {
            'code': 'VIOLATION_SECRET_MEDICAL',
            'nom': 'Violation du secret médical',
            'description': 'Partage non autorisé d\'informations médicales',
            'norme_conformite': 'CDP',
            'niveau_critique': 5,
            'delai_notification': 1
        },
        {
            'code': 'ACCES_HORS_HORAIRE',
            'nom': 'Accès hors horaires',
            'description': 'Accès au système en dehors des horaires de travail',
            'norme_conformite': 'GENERAL',
            'niveau_critique': 2,
            'delai_notification': 12
        },
        {
            'code': 'MULTIPLE_ECHECS_CONNEXION',
            'nom': 'Multiples échecs de connexion',
            'description': 'Plusieurs tentatives de connexion échouées',
            'norme_conformite': 'GENERAL',
            'niveau_critique': 3,
            'delai_notification': 6
        }
    ]
    
    print("1️⃣ Création des types d'alertes de sécurité...")
    types_crees = 0
    
    for type_alerte in types_alertes_securite:
        try:
            type_obj, created = TypeAlerteConformite.objects.get_or_create(
                code=type_alerte['code'],
                defaults=type_alerte
            )
            if created:
                print(f"   ✅ Créé: {type_alerte['nom']}")
                types_crees += 1
            else:
                print(f"   ⚠️  Existant: {type_alerte['nom']}")
        except Exception as e:
            print(f"   ❌ Erreur: {type_alerte['nom']} - {e}")
    
    print(f"   📊 {types_crees} nouveaux types créés")
    
    # 2. Créer les règles d'alertes de sécurité
    regles_securite = [
        {
            'nom': 'Surveillance accès non autorisés',
            'description': 'Détecte les tentatives d\'accès non autorisé au système',
            'type_alerte_code': 'ACCES_NON_AUTORISE',
            'seuil_min': 1,
            'seuil_max': None,
            'periode_surveillance': 1,
            'action_automatique': 'BLOQUER_ACCES',
            'notifier_admin': True,
            'notifier_dpo': True,
            'notifier_cdp': False
        },
        {
            'nom': 'Surveillance fuites de données',
            'description': 'Détecte les possibles fuites de données médicales',
            'type_alerte_code': 'FUITES_DONNEES',
            'seuil_min': 1,
            'seuil_max': None,
            'periode_surveillance': 1,
            'action_automatique': 'ESCALADER',
            'notifier_admin': True,
            'notifier_dpo': True,
            'notifier_cdp': True
        },
        {
            'nom': 'Surveillance tentatives d\'intrusion',
            'description': 'Détecte les tentatives d\'intrusion dans le système',
            'type_alerte_code': 'TENTATIVE_INTRUSION',
            'seuil_min': 3,
            'seuil_max': None,
            'periode_surveillance': 1,
            'action_automatique': 'BLOQUER_ACCES',
            'notifier_admin': True,
            'notifier_dpo': False,
            'notifier_cdp': False
        },
        {
            'nom': 'Surveillance exports non autorisés',
            'description': 'Détecte les tentatives d\'export sans autorisation',
            'type_alerte_code': 'EXPORT_NON_AUTORISE',
            'seuil_min': 1,
            'seuil_max': None,
            'periode_surveillance': 1,
            'action_automatique': 'BLOQUER_ACCES',
            'notifier_admin': True,
            'notifier_dpo': True,
            'notifier_cdp': False
        },
        {
            'nom': 'Surveillance modifications critiques',
            'description': 'Détecte les modifications de données critiques',
            'type_alerte_code': 'MODIFICATION_CRITIQUE',
            'seuil_min': 1,
            'seuil_max': None,
            'periode_surveillance': 1,
            'action_automatique': 'LOGGER',
            'notifier_admin': True,
            'notifier_dpo': True,
            'notifier_cdp': False
        },
        {
            'nom': 'Surveillance suppressions en masse',
            'description': 'Détecte les suppressions de multiples dossiers',
            'type_alerte_code': 'SUPPRESSION_MASSE',
            'seuil_min': 5,
            'seuil_max': None,
            'periode_surveillance': 1,
            'action_automatique': 'BLOQUER_ACCES',
            'notifier_admin': True,
            'notifier_dpo': True,
            'notifier_cdp': True
        },
        {
            'nom': 'Surveillance connexions suspectes',
            'description': 'Détecte les connexions depuis des sources suspectes',
            'type_alerte_code': 'CONNEXION_SUSPICIEUSE',
            'seuil_min': 1,
            'seuil_max': None,
            'periode_surveillance': 6,
            'action_automatique': 'NOTIFICATION',
            'notifier_admin': True,
            'notifier_dpo': False,
            'notifier_cdp': False
        },
        {
            'nom': 'Surveillance violations secret médical',
            'description': 'Détecte les violations du secret médical',
            'type_alerte_code': 'VIOLATION_SECRET_MEDICAL',
            'seuil_min': 1,
            'seuil_max': None,
            'periode_surveillance': 1,
            'action_automatique': 'ESCALADER',
            'notifier_admin': True,
            'notifier_dpo': True,
            'notifier_cdp': True
        },
        {
            'nom': 'Surveillance accès hors horaires',
            'description': 'Détecte les accès en dehors des horaires normaux',
            'type_alerte_code': 'ACCES_HORS_HORAIRE',
            'seuil_min': 1,
            'seuil_max': None,
            'periode_surveillance': 12,
            'action_automatique': 'NOTIFICATION',
            'notifier_admin': True,
            'notifier_dpo': False,
            'notifier_cdp': False
        },
        {
            'nom': 'Surveillance échecs de connexion',
            'description': 'Détecte les multiples échecs de connexion',
            'type_alerte_code': 'MULTIPLE_ECHECS_CONNEXION',
            'seuil_min': 5,
            'seuil_max': None,
            'periode_surveillance': 1,
            'action_automatique': 'BLOQUER_ACCES',
            'notifier_admin': True,
            'notifier_dpo': False,
            'notifier_cdp': False
        }
    ]
    
    print("\n2️⃣ Création des règles d'alertes de sécurité...")
    regles_crees = 0
    
    for regle in regles_securite:
        try:
            # Récupérer le type d'alerte
            type_alerte = TypeAlerteConformite.objects.get(code=regle['type_alerte_code'])
            
            regle_obj, created = RegleAlerteConformite.objects.get_or_create(
                nom=regle['nom'],
                defaults={
                    'description': regle['description'],
                    'type_alerte': type_alerte,
                    'conditions': {'type': 'seuil', 'valeur': regle['seuil_min']},
                    'seuil_min': regle['seuil_min'],
                    'seuil_max': regle['seuil_max'],
                    'periode_surveillance': regle['periode_surveillance'],
                    'action_automatique': regle['action_automatique'],
                    'notifier_admin': regle['notifier_admin'],
                    'notifier_dpo': regle['notifier_dpo'],
                    'notifier_cdp': regle['notifier_cdp'],
                    'is_active': True
                }
            )
            if created:
                print(f"   ✅ Créée: {regle['nom']}")
                regles_crees += 1
            else:
                print(f"   ⚠️  Existante: {regle['nom']}")
        except Exception as e:
            print(f"   ❌ Erreur: {regle['nom']} - {e}")
    
    print(f"   📊 {regles_crees} nouvelles règles créées")
    
    # 3. Ajouter les nouvelles règles à l'ancien système RegleConformite
    print("\n3️⃣ Ajout des règles à l'ancien système...")
    anciennes_regles_crees = 0
    
    anciennes_regles = [
        {
            'nomRegle': 'Surveillance accès non autorisés',
            'description': 'Détecte les tentatives d\'accès non autorisé au système médical',
            'typeRegle': 'SECURITE_ACCES',
            'niveauCritique': 4
        },
        {
            'nomRegle': 'Surveillance fuites de données',
            'description': 'Détecte les possibles fuites de données médicales sensibles',
            'typeRegle': 'SECURITE_DONNEES',
            'niveauCritique': 5
        },
        {
            'nomRegle': 'Surveillance tentatives d\'intrusion',
            'description': 'Détecte les tentatives d\'intrusion dans le système médical',
            'typeRegle': 'SECURITE_INTRUSION',
            'niveauCritique': 4
        },
        {
            'nomRegle': 'Surveillance exports non autorisés',
            'description': 'Détecte les tentatives d\'export de données sans autorisation',
            'typeRegle': 'SECURITE_EXPORT',
            'niveauCritique': 4
        },
        {
            'nomRegle': 'Surveillance modifications critiques',
            'description': 'Détecte les modifications de données médicales critiques',
            'typeRegle': 'SECURITE_MODIFICATION',
            'niveauCritique': 4
        },
        {
            'nomRegle': 'Surveillance suppressions en masse',
            'description': 'Détecte les suppressions de multiples dossiers médicaux',
            'typeRegle': 'SECURITE_SUPPRESSION',
            'niveauCritique': 5
        },
        {
            'nomRegle': 'Surveillance connexions suspectes',
            'description': 'Détecte les connexions depuis des sources suspectes',
            'typeRegle': 'SECURITE_CONNEXION',
            'niveauCritique': 3
        },
        {
            'nomRegle': 'Surveillance violations secret médical',
            'description': 'Détecte les violations du secret médical',
            'typeRegle': 'SECURITE_SECRET',
            'niveauCritique': 5
        },
        {
            'nomRegle': 'Surveillance accès hors horaires',
            'description': 'Détecte les accès en dehors des horaires de travail',
            'typeRegle': 'SECURITE_HORAIRE',
            'niveauCritique': 2
        },
        {
            'nomRegle': 'Surveillance échecs de connexion',
            'description': 'Détecte les multiples échecs de connexion',
            'typeRegle': 'SECURITE_ECHEC',
            'niveauCritique': 3
        }
    ]
    
    for regle in anciennes_regles:
        try:
            regle_obj, created = RegleConformite.objects.get_or_create(
                nomRegle=regle['nomRegle'],
                defaults=regle
            )
            if created:
                print(f"   ✅ Créée: {regle['nomRegle']}")
                anciennes_regles_crees += 1
            else:
                print(f"   ⚠️  Existante: {regle['nomRegle']}")
        except Exception as e:
            print(f"   ❌ Erreur: {regle['nomRegle']} - {e}")
    
    print(f"   📊 {anciennes_regles_crees} anciennes règles créées")
    
    # 4. Statistiques finales
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DE L'AJOUT DES ALERTES DE SÉCURITÉ")
    print("=" * 50)
    print(f"   • Types d'alertes créés: {types_crees}")
    print(f"   • Règles modernes créées: {regles_crees}")
    print(f"   • Règles anciennes créées: {anciennes_regles_crees}")
    print(f"   • Total: {types_crees + regles_crees + anciennes_regles_crees} éléments")
    
    print("\n🎯 NOUVELLES ALERTES DE SÉCURITÉ AJOUTÉES:")
    print("   🔒 Accès non autorisé")
    print("   💧 Fuite de données")
    print("   🚪 Tentative d'intrusion")
    print("   📤 Export non autorisé")
    print("   ✏️  Modification critique")
    print("   🗑️  Suppression en masse")
    print("   🔍 Connexion suspecte")
    print("   🤐 Violation secret médical")
    print("   ⏰ Accès hors horaires")
    print("   ❌ Multiples échecs de connexion")
    
    print("\n✅ SYSTÈME D'ALERTES DE SÉCURITÉ COMPLÉTÉ !")
    print("\n📝 PROCHAINES ÉTAPES:")
    print("   1. Redémarrer le serveur backend")
    print("   2. Accéder à l'interface de configuration")
    print("   3. Configurer les seuils spécifiques")
    print("   4. Tester les nouvelles alertes")

if __name__ == '__main__':
    ajouter_alertes_securite() 
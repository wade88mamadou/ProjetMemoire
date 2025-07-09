#!/usr/bin/env python3
"""
Script de migration de SQLite vers PostgreSQL pour ConformiMed
Ce script transfère les données existantes de SQLite vers PostgreSQL
"""

import os
import sys
import django
from django.conf import settings
import json

# Configuration Django temporaire pour SQLite
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.db import connections
from api.models import *

def backup_sqlite_data():
    """Sauvegarde les données SQLite existantes"""
    print("📦 Sauvegarde des données SQLite...")
    
    backup_data = {}
    
    # Sauvegarder les utilisateurs
    try:
        users = Utilisateur.objects.all()
        backup_data['users'] = []
        for user in users:
            backup_data['users'].append({
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'specialite': user.specialite,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
            })
        print(f"✅ {len(backup_data['users'])} utilisateurs sauvegardés")
    except Exception as e:
        print(f"⚠️  Erreur lors de la sauvegarde des utilisateurs: {e}")
    
    # Sauvegarder les autres modèles si nécessaire
    # Ajoutez ici d'autres modèles selon vos besoins
    
    # Sauvegarder dans un fichier JSON
    with open('sqlite_backup.json', 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
    
    print("✅ Sauvegarde terminée dans sqlite_backup.json")
    return backup_data

def restore_to_postgresql(backup_data):
    """Restaure les données dans PostgreSQL"""
    print("🔄 Restauration des données dans PostgreSQL...")
    
    # Restaurer les utilisateurs
    if 'users' in backup_data:
        for user_data in backup_data['users']:
            try:
                # Vérifier si l'utilisateur existe déjà
                if not Utilisateur.objects.filter(username=user_data['username']).exists():
                    user = Utilisateur.objects.create_user(
                        username=user_data['username'],
                        email=user_data['email'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        role=user_data['role'],
                        specialite=user_data['specialite'],
                        is_staff=user_data['is_staff'],
                        is_superuser=user_data['is_superuser'],
                    )
                    print(f"✅ Utilisateur {user.username} restauré")
                else:
                    print(f"⚠️  Utilisateur {user_data['username']} existe déjà")
            except Exception as e:
                print(f"❌ Erreur lors de la restauration de {user_data['username']}: {e}")
    
    print("✅ Restauration terminée")

def main():
    """Fonction principale de migration"""
    print("🚀 Migration SQLite vers PostgreSQL")
    print("=" * 50)
    
    # Vérifier que PostgreSQL est configuré
    try:
        # Tester la connexion PostgreSQL
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Connexion PostgreSQL établie")
    except Exception as e:
        print(f"❌ Erreur de connexion PostgreSQL: {e}")
        print("Assurez-vous que PostgreSQL est configuré et accessible")
        return False
    
    # Sauvegarder les données SQLite
    backup_data = backup_sqlite_data()
    
    # Restaurer dans PostgreSQL
    restore_to_postgresql(backup_data)
    
    print("\n🎉 Migration terminée avec succès!")
    print("Vous pouvez maintenant supprimer le fichier db.sqlite3")
    
    return True

if __name__ == "__main__":
    if main():
        print("\n✅ Migration réussie!")
    else:
        print("\n❌ Migration échouée!")
        sys.exit(1) 
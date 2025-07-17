#!/usr/bin/env python
import os
import django
import psycopg2
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

def clean_and_reset():
    """Nettoie les tables et réinitialise les migrations"""
    
    # Connexion à la base de données
    conn = psycopg2.connect(
        dbname='conformimed_db',
        user='conformimed_user',
        password='conformimed_password',
        host='localhost',
        port='5432'
    )
    
    cursor = conn.cursor()
    
    try:
        print("Suppression de toutes les tables...")
        
        # Supprimer toutes les tables dans l'ordre correct
        tables_to_drop = [
            'token_blacklist_outstandingtoken',
            'token_blacklist_blacklistedtoken',
            'api_acces',
            'api_alerte',
            'api_vaccin',
            'api_infection',
            'api_resultatanalyse',
            'api_analyse',
            'api_dossiermedical',
            'api_patient',
            'api_alimentation',
            'api_logement',
            'api_comportement',
            'api_residence',
            'api_profession',
            'api_parametreconformite',
            'api_rapport',
            'api_regleconformite',
            'api_utilisateur_groups',
            'api_utilisateur_user_permissions',
            'api_utilisateur',
            'django_admin_log',
            'django_content_type',
            'django_migrations',
            'django_session',
            'auth_group_permissions',
            'auth_user_groups',
            'auth_user_user_permissions',
            'auth_group',
            'auth_permission',
            'django_migrations',
        ]
        
        for table in tables_to_drop:
            try:
                cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE;')
                print(f"✓ Table {table} supprimée")
            except Exception as e:
                print(f"⚠ Erreur suppression {table}: {e}")
        
        # Supprimer toutes les séquences
        cursor.execute("""
            SELECT sequence_name 
            FROM information_schema.sequences 
            WHERE sequence_schema = 'public';
        """)
        
        sequences = [row[0] for row in cursor.fetchall()]
        for seq in sequences:
            try:
                cursor.execute(f'DROP SEQUENCE IF EXISTS "{seq}";')
            except:
                pass
        
        conn.commit()
        print("✓ Base de données nettoyée")
        
        # Supprimer le fichier de migrations
        migrations_file = 'api/migrations/0001_initial.py'
        if os.path.exists(migrations_file):
            os.remove(migrations_file)
            print(f"✓ Fichier de migration supprimé: {migrations_file}")
        
    except Exception as e:
        print(f"Erreur: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    clean_and_reset() 
#!/usr/bin/env python
import os
import django
import psycopg2
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

def reset_database():
    """Réinitialise complètement la base de données"""
    
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
        print("⚠️  ATTENTION: Cette opération va supprimer toutes les données existantes!")
        print("Tables qui seront supprimées:")
        
        # Lister toutes les tables existantes
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'api_%'
            ORDER BY table_name;
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        for table in existing_tables:
            print(f"  - {table}")
        
        if not existing_tables:
            print("  Aucune table api_* trouvée")
        
        print("\nVoulez-vous continuer? (y/N): ", end="")
        response = input().strip().lower()
        
        if response != 'y':
            print("Opération annulée.")
            return
        
        # Supprimer toutes les tables api_*
        print("\nSuppression des tables existantes...")
        for table in existing_tables:
            try:
                cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE;')
                print(f"✓ Table {table} supprimée")
            except Exception as e:
                print(f"⚠ Erreur suppression {table}: {e}")
        
        conn.commit()
        print("✓ Toutes les tables supprimées")
        
        # Réinitialiser les séquences
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
        print("✓ Séquences réinitialisées")
        
    except Exception as e:
        print(f"Erreur: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    reset_database() 
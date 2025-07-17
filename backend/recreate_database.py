#!/usr/bin/env python
import os
import django
import psycopg2
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

def recreate_database():
    """Supprime et recrée complètement la base de données"""
    
    # Connexion à postgres (base de données système)
    conn = psycopg2.connect(
        dbname='postgres',
        user='conformimed_user',
        password='conformimed_password',
        host='localhost',
        port='5432'
    )
    
    conn.autocommit = True  # Important pour DROP/CREATE DATABASE
    cursor = conn.cursor()
    
    try:
        print("Suppression de la base de données existante...")
        
        # Terminer toutes les connexions à la base
        cursor.execute("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = 'conformimed_db' AND pid <> pg_backend_pid();
        """)
        
        # Supprimer la base de données
        cursor.execute('DROP DATABASE IF EXISTS conformimed_db;')
        print("✓ Base de données supprimée")
        
        # Recréer la base de données
        cursor.execute('CREATE DATABASE conformimed_db;')
        print("✓ Base de données recréée")
        
    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    recreate_database() 
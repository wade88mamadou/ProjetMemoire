#!/usr/bin/env python3
"""
Script de configuration PostgreSQL pour ConformiMed
Ce script crée la base de données et l'utilisateur PostgreSQL
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os

def create_database():
    """Crée la base de données et l'utilisateur PostgreSQL"""
    
    # Configuration par défaut
    DB_NAME = 'conformimed_db'
    DB_USER = 'conformimed_user'
    DB_PASSWORD = 'conformimed_password'
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    
    # Connexion à PostgreSQL en tant que superutilisateur
    try:
        # Connexion à la base de données postgres (base par défaut)
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database='postgres',
            user='postgres',  # Utilisateur par défaut PostgreSQL
            password=input("Entrez le mot de passe PostgreSQL (postgres): ") or 'postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connexion à PostgreSQL établie")
        
        # Créer l'utilisateur
        try:
            cursor.execute(f"CREATE USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}';")
            print(f"✅ Utilisateur {DB_USER} créé")
        except psycopg2.errors.DuplicateObject:
            print(f"⚠️  L'utilisateur {DB_USER} existe déjà")
        
        # Créer la base de données
        try:
            cursor.execute(f"CREATE DATABASE {DB_NAME} OWNER {DB_USER};")
            print(f"✅ Base de données {DB_NAME} créée")
        except psycopg2.errors.DuplicateDatabase:
            print(f"⚠️  La base de données {DB_NAME} existe déjà")
        
        # Accorder les privilèges
        try:
            cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER};")
            print(f"✅ Privilèges accordés à {DB_USER}")
        except Exception as e:
            print(f"⚠️  Erreur lors de l'attribution des privilèges: {e}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Configuration PostgreSQL terminée avec succès!")
        print(f"Base de données: {DB_NAME}")
        print(f"Utilisateur: {DB_USER}")
        print(f"Mot de passe: {DB_PASSWORD}")
        print(f"Hôte: {DB_HOST}:{DB_PORT}")
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erreur de connexion à PostgreSQL: {e}")
        print("\nAssurez-vous que:")
        print("1. PostgreSQL est installé et en cours d'exécution")
        print("2. Le service PostgreSQL est démarré")
        print("3. L'utilisateur 'postgres' existe avec le bon mot de passe")
        return False
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def test_connection():
    """Teste la connexion à la nouvelle base de données"""
    
    DB_NAME = 'conformimed_db'
    DB_USER = 'conformimed_user'
    DB_PASSWORD = 'conformimed_password'
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        
        print(f"✅ Test de connexion réussi!")
        print(f"Version PostgreSQL: {version[0]}")
        return True
        
    except Exception as e:
        print(f"❌ Échec du test de connexion: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Configuration PostgreSQL pour ConformiMed")
    print("=" * 50)
    
    if create_database():
        print("\n" + "=" * 50)
        print("🧪 Test de la connexion...")
        test_connection()
        
        print("\n" + "=" * 50)
        print("📋 Prochaines étapes:")
        print("1. Exécutez: python manage.py makemigrations")
        print("2. Exécutez: python manage.py migrate")
        print("3. Exécutez: python manage.py createsuperuser")
        print("4. Démarrez le serveur: python manage.py runserver")
    else:
        sys.exit(1) 
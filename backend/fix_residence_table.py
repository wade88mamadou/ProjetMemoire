#!/usr/bin/env python
import os
import django
import psycopg2
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

def check_and_fix_residence_table():
    """Vérifie et corrige la structure de la table api_residence"""
    
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
        # 1. Vérifier si la table existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_residence'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        print(f"Table api_residence existe: {table_exists}")
        
        if not table_exists:
            print("La table api_residence n'existe pas. Création...")
            cursor.execute("""
                CREATE TABLE api_residence (
                    idResidence SERIAL PRIMARY KEY,
                    pays VARCHAR(100),
                    ville VARCHAR(100),
                    quartier VARCHAR(100),
                    adresseComplete VARCHAR(255)
                );
            """)
            conn.commit()
            print("Table api_residence créée avec succès!")
            return
        
        # 2. Vérifier la structure de la table
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'api_residence'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("Structure actuelle de la table api_residence:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
        # 3. Vérifier si idResidence existe
        column_names = [col[0] for col in columns]
        
        if 'idresidence' not in column_names:
            print("La colonne idResidence n'existe pas!")
            
            # Vérifier s'il y a une colonne id
            if 'id' in column_names:
                print("Il y a une colonne 'id' au lieu de 'idResidence'")
                print("Renommage de 'id' vers 'idResidence'...")
                
                cursor.execute("ALTER TABLE api_residence RENAME COLUMN id TO idResidence;")
                conn.commit()
                print("Colonne renommée avec succès!")
            else:
                print("Aucune colonne id trouvée. Ajout de la colonne idResidence...")
                cursor.execute("""
                    ALTER TABLE api_residence 
                    ADD COLUMN idResidence SERIAL PRIMARY KEY;
                """)
                conn.commit()
                print("Colonne idResidence ajoutée avec succès!")
        else:
            print("La colonne idResidence existe déjà!")
        
        # 4. Vérifier les autres colonnes nécessaires
        required_columns = ['pays', 'ville', 'quartier', 'adressecomplete']
        missing_columns = []
        
        for col in required_columns:
            if col not in column_names:
                missing_columns.append(col)
        
        if missing_columns:
            print(f"Colonnes manquantes: {missing_columns}")
            for col in missing_columns:
                cursor.execute(f"ALTER TABLE api_residence ADD COLUMN {col} VARCHAR(100);")
            conn.commit()
            print("Colonnes manquantes ajoutées!")
        else:
            print("Toutes les colonnes requises sont présentes!")
        
        # 5. Afficher la structure finale
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'api_residence'
            ORDER BY ordinal_position;
        """)
        
        final_columns = cursor.fetchall()
        print("\nStructure finale de la table api_residence:")
        for col in final_columns:
            print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
    except Exception as e:
        print(f"Erreur: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_and_fix_residence_table() 
#!/usr/bin/env python
import os
import django
import psycopg2
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

def fix_table_column_case():
    """Corrige les problèmes de casse dans toutes les tables"""
    
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
        # Liste des tables et colonnes à corriger
        tables_to_fix = [
            ('api_residence', 'idresidence', 'idResidence'),
            ('api_profession', 'idprofession', 'idProfession'),
            ('api_comportement', 'idcomportement', 'idComportement'),
            ('api_logement', 'idlogement', 'idLogement'),
            ('api_alimentation', 'idalimentation', 'idAlimentation'),
            ('api_patient', 'idpatient', 'idPatient'),
            ('api_dossiermedical', 'iddossier', 'idDossier'),
            ('api_analyse', 'idanalyse', 'idAnalyse'),
            ('api_resultatanalyse', 'idresultatanalyse', 'idResultatAnalyse'),
            ('api_alerte', 'idalerte', 'idAlerte'),
            ('api_vaccin', 'idvaccin', 'idVaccin'),
            ('api_infection', 'idinfection', 'idInfection'),
            ('api_parametreconformite', 'idparametre', 'idParametre'),
            ('api_rapport', 'idrapport', 'idRapport'),
            ('api_regleconformite', 'idregle', 'idRegle'),
        ]
        
        for table_name, current_col, target_col in tables_to_fix:
            try:
                # Vérifier si la table existe
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """, (table_name,))
                
                table_exists = cursor.fetchone()[0]
                
                if not table_exists:
                    print(f"Table {table_name} n'existe pas, ignorée.")
                    continue
                
                # Vérifier si la colonne actuelle existe
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns
                    WHERE table_name = %s AND column_name = %s;
                """, (table_name, current_col))
                
                current_exists = cursor.fetchone() is not None
                
                # Vérifier si la colonne cible existe
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns
                    WHERE table_name = %s AND column_name = %s;
                """, (table_name, target_col))
                
                target_exists = cursor.fetchone() is not None
                
                if current_exists and not target_exists:
                    print(f"Renommage de {table_name}.{current_col} vers {target_col}...")
                    cursor.execute(f'ALTER TABLE {table_name} RENAME COLUMN "{current_col}" TO "{target_col}";')
                    conn.commit()
                    print(f"✓ {table_name}.{current_col} renommé vers {target_col}")
                elif target_exists:
                    print(f"✓ {table_name}.{target_col} existe déjà")
                else:
                    print(f"⚠ {table_name}: ni {current_col} ni {target_col} trouvés")
                    
            except Exception as e:
                print(f"Erreur avec {table_name}: {e}")
                conn.rollback()
        
        # Afficher la structure finale des tables principales
        print("\n=== Structure finale des tables principales ===")
        
        for table_name, _, _ in tables_to_fix[:6]:  # Afficher seulement les 6 premières
            try:
                cursor.execute("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = %s
                    ORDER BY ordinal_position;
                """, (table_name,))
                
                columns = cursor.fetchall()
                if columns:
                    print(f"\n{table_name}:")
                    for col in columns:
                        print(f"  - {col[0]}: {col[1]}")
                        
            except Exception as e:
                print(f"Erreur lecture {table_name}: {e}")
        
    except Exception as e:
        print(f"Erreur générale: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_table_column_case() 
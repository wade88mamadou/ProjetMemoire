#!/usr/bin/env python3
"""
Script pour importer directement le fichier base.csv vers la base de données Django
"""

import os
import sys
import django
import pandas as pd
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from api.models import Patient, Profession, Logement, Residence, Comportement, DossierMedical

def import_csv_data():
    """Importe les données du fichier base.csv"""
    
    csv_file = 'base.csv'
    
    if not os.path.exists(csv_file):
        print(f"❌ Fichier {csv_file} non trouvé dans le répertoire courant")
        return
    
    try:
        print(f"📖 Lecture du fichier {csv_file}...")
        
        # Lecture du fichier CSV
        df = pd.read_csv(csv_file, encoding='ISO-8859-1', sep=';')
        
        print(f"✅ Fichier lu avec succès. {len(df)} lignes trouvées.")
        print(f"📊 Colonnes disponibles: {list(df.columns[:10])}...")  # Afficher les 10 premières colonnes
        
        # Vérification des colonnes requises
        required_columns = ['ID', 'Age', 'Sex', 'Place_birth', 'Edu_Level', 'weight', 'height']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Colonnes manquantes: {missing_columns}")
            return
        
        print("✅ Toutes les colonnes requises sont présentes.")
        
        # Statistiques
        patients_created = 0
        patients_skipped = 0
        errors = []
        
        print("🔄 Début de l'importation...")
        
        for index, row in df.iterrows():
            try:
                id_code = row['ID']
                
                # Ignorer les lignes vides
                if pd.isna(id_code):
                    continue
                
                # Vérifier si le patient existe déjà
                if Patient.objects.filter(id_code=id_code).exists():
                    patients_skipped += 1
                    continue
                
                # Préparer les données du patient
                patient_data = {
                    'id_code': id_code,
                    'age': row.get('Age'),
                    'sex': row.get('Sex'),
                    'place_birth': row.get('Place_birth'),
                    'niveau_etude': row.get('Edu_Level'),
                    'poids': row.get('weight'),
                    'taille': row.get('height'),
                }
                
                # Ajouter des champs optionnels s'ils existent
                if 'Date_birth' in row and not pd.isna(row.get('Date_birth')):
                    try:
                        patient_data['date_birth'] = pd.to_datetime(row.get('Date_birth')).date()
                    except:
                        pass
                
                if 'Place_grow' in row and not pd.isna(row.get('Place_grow')):
                    patient_data['place_grow'] = row.get('Place_grow')
                
                if 'Current_resid' in row and not pd.isna(row.get('Current_resid')):
                    patient_data['current_resid'] = row.get('Current_resid')
                
                # Nettoyer les valeurs NaN
                for key, value in patient_data.items():
                    if pd.isna(value):
                        patient_data[key] = None
                
                # Créer le patient
                patient = Patient.objects.create(**patient_data)
                patients_created += 1
                
                # Afficher le progrès tous les 100 patients
                if patients_created % 100 == 0:
                    print(f"📈 {patients_created} patients créés...")
                
            except Exception as e:
                errors.append(f"Ligne {index + 1}: {str(e)}")
                continue
        
        # Résultats finaux
        print("\n" + "="*50)
        print("📊 RÉSULTATS DE L'IMPORTATION")
        print("="*50)
        print(f"✅ Patients créés: {patients_created}")
        print(f"⏭️  Patients ignorés (doublons): {patients_skipped}")
        print(f"❌ Erreurs: {len(errors)}")
        
        if errors:
            print("\n🔍 Premières erreurs:")
            for error in errors[:5]:
                print(f"   - {error}")
        
        print(f"\n🎉 Importation terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'importation: {str(e)}")

if __name__ == "__main__":
    print("🚀 Démarrage de l'importation CSV...")
    import_csv_data() 
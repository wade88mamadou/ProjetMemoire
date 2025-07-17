#!/usr/bin/env python3
"""
Script complet pour importer toutes les données du fichier base.csv 
vers toutes les tables de la base de données Django
"""

import os
import sys
import django
import pandas as pd
from datetime import datetime, date
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from api.models import (
    Patient, Profession, Logement, Residence, Comportement, 
    DossierMedical, Analyse, ResultatAnalyse, Alerte, Vaccin, 
    Infection, Alimentation, Rapport, Acces, RegleConformite, 
    ParametreConformite
)

def clean_value(value):
    """Nettoie une valeur (NaN, espaces, etc.)"""
    if pd.isna(value) or value == '' or str(value).strip() == '':
        return None
    return str(value).strip()

def safe_float(value):
    """Convertit en float de manière sécurisée"""
    if pd.isna(value) or value == '':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def safe_int(value):
    """Convertit en int de manière sécurisée"""
    if pd.isna(value) or value == '':
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None

def safe_bool(value):
    """Convertit en bool de manière sécurisée"""
    if pd.isna(value) or value == '':
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        value = value.lower().strip()
        return value in ['true', '1', 'yes', 'oui', 'vrai']
    if isinstance(value, (int, float)):
        return bool(value)
    return None

def get_or_create_profession(row):
    """Crée ou récupère une profession"""
    nom_profession = clean_value(row.get('Job', ''))
    if not nom_profession:
        return None
    
    profession, created = Profession.objects.get_or_create(
        nomProfession=nom_profession,
        defaults={
            'typeProfession': clean_value(row.get('Job_type', '')),
            'environnementTravail': clean_value(row.get('Working_Env', '')),
            'travailleDehors': clean_value(row.get('Outdoor_Work_type', '')),
            'travailleSansEmploi': clean_value(row.get('Occup_if_jobless', '')),
            'situationSansEmploi': clean_value(row.get('Occup_if_jobless', '')),
            'revenu': clean_value(row.get('Incomes', '')),
            'freqRevenu': clean_value(row.get('Freq_Incomes', ''))
        }
    )
    return profession

def get_or_create_residence(row):
    """Crée ou récupère une résidence"""
    pays = clean_value(row.get('Place_birth', ''))
    if not pays:
        return None
    
    residence, created = Residence.objects.get_or_create(
        pays=pays,
        defaults={
            'ville': clean_value(row.get('Current_resid', '')),
            'quartier': clean_value(row.get('Current_resid', '')),
            'adresseComplete': f"{clean_value(row.get('Current_resid', ''))}, {pays}"
        }
    )
    return residence

def get_or_create_logement(row):
    """Crée ou récupère un logement"""
    type_logement = clean_value(row.get('Housing_type', ''))
    if not type_logement:
        return None
    
    logement, created = Logement.objects.get_or_create(
        typeLogement=type_logement,
        defaults={
            'nombrePersonnesFoyer': safe_int(row.get('Nr_people_house', 0)) or 1,
            'nbMursMaisonCouverts': safe_int(row.get('Wall_Covered', 0)) or 0,
            'nbSolsMaisonCouverts': safe_int(row.get('House_Ground_Covered', 0)) or 0,
            'nbToilettesMaison': safe_int(row.get('Toilet_Location', 0)) or 0,
            'toilettesInterieures': safe_bool(row.get('Toilet_Location', '')) or False
        }
    )
    return logement

def get_or_create_comportement(row):
    """Crée ou récupère un comportement"""
    lieu_repas = clean_value(row.get('Eating_Location', ''))
    if not lieu_repas:
        return None
    
    comportement, created = Comportement.objects.get_or_create(
        lieuRepas=lieu_repas,
        defaults={
            'mangeAvecLesMains': clean_value(row.get('Eating_Man', '')),
            'laveLesMainsAvantDeManger': clean_value(row.get('Wash_Hand_When_Eating', '')),
            'utiliseDuSavon': clean_value(row.get('Soab_Wash_Hand', '')),
            'laveLesMainsDesEnfants': clean_value(row.get('Wash_Hand_Child', '')),
            'utiliseGelHydroalcoolique': clean_value(row.get('Hand_Antisep_Use', ''))
        }
    )
    return comportement

def get_or_create_alimentation(row):
    """Crée ou récupère une alimentation"""
    type_repas = clean_value(row.get('Eating_way', ''))
    if not type_repas:
        return None
    
    alimentation, created = Alimentation.objects.get_or_create(
        typeRepas=type_repas
    )
    return alimentation

def create_patient(row, profession, residence, logement, comportement, alimentation):
    """Crée un patient"""
    id_code = clean_value(row.get('ID', ''))
    if not id_code:
        return None
    
    # Vérifier si le patient existe déjà
    if Patient.objects.filter(id_code=id_code).exists():
        return Patient.objects.get(id_code=id_code)
    
    # Convertir le sexe
    sexe_value = clean_value(row.get('Sex', ''))
    sexe = None
    if sexe_value:
        sexe = sexe_value.lower() in ['m', 'male', '1', 'homme']
    
    patient = Patient.objects.create(
        id_code=id_code,
        sexe=sexe,
        poids=safe_float(row.get('weight', 0)),
        taille=safe_float(row.get('height', 0)),
        lieuNaissance=clean_value(row.get('Place_birth', '')),
        niveauEtude=clean_value(row.get('Edu_Level', '')),
        profession=profession,
        comportement=comportement,
        logement=logement,
        alimentation=alimentation,
        residence=residence
    )
    return patient

def create_dossier_medical(patient, row):
    """Crée un dossier médical"""
    dossier, created = DossierMedical.objects.get_or_create(
        patient=patient,
        defaults={
            'dateCreation': datetime.now().date(),
            'commentaireGeneral': f"Dossier créé automatiquement pour le patient {patient.id_code}"
        }
    )
    return dossier

def create_analyse(dossier, row):
    """Crée une analyse"""
    analyse, created = Analyse.objects.get_or_create(
        dossier=dossier,
        defaults={
            'typeAnalyse': 'Analyse générale',
            'dateAnalyse': datetime.now().date()
        }
    )
    return analyse

def create_resultat_analyse(analyse, row):
    """Crée un résultat d'analyse"""
    # Vérifier si des données d'analyse existent
    glycemie = safe_float(row.get('Gluc_mM_L'))
    if glycemie is None:
        return None
    
    resultat, created = ResultatAnalyse.objects.get_or_create(
        analyse=analyse,
        defaults={
            'glycemie': glycemie,
            'cholesterol': safe_float(row.get('Cholesterol', 0)) or 0,
            'triglyceride': safe_float(row.get('Triglyceride', 0)) or 0,
            'hdl': safe_float(row.get('HDL', 0)) or 0,
            'ldl': safe_float(row.get('LDL', 0)) or 0,
            'creatinine': safe_float(row.get('Creatinine', 0)) or 0,
            'uree': safe_float(row.get('Uree', 0)) or 0,
            'proteinurie': safe_float(row.get('Proteinurie', 0)) or 0
        }
    )
    return resultat

def create_alerte(dossier, row):
    """Crée une alerte si nécessaire"""
    # Créer des alertes basées sur les conditions médicales
    alertes = []
    
    # Alerte pour diabète
    if clean_value(row.get('Diabetes', '')):
        alerte, created = Alerte.objects.get_or_create(
            dossier=dossier,
            typeAlerte='Diabète',
            defaults={
                'message': 'Patient diagnostiqué avec diabète',
                'dateAlerte': datetime.now().date()
            }
        )
        alertes.append(alerte)
    
    # Alerte pour hypertension
    ap_sys = safe_float(row.get('AP_Sys_mmHg'))
    if ap_sys and ap_sys > 140:
        alerte, created = Alerte.objects.get_or_create(
            dossier=dossier,
            typeAlerte='Hypertension',
            defaults={
                'message': f'Pression artérielle élevée: {ap_sys} mmHg',
                'dateAlerte': datetime.now().date()
            }
        )
        alertes.append(alerte)
    
    return alertes

def create_vaccin(dossier, row):
    """Crée un vaccin"""
    vaccin_recu = clean_value(row.get('Vacc_Received', ''))
    if not vaccin_recu:
        return None
    
    vaccin, created = Vaccin.objects.get_or_create(
        dossier=dossier,
        nomVaccin=vaccin_recu,
        defaults={
            'typeVaccination': clean_value(row.get('Vacc_Program', '')),
            'dose': safe_int(row.get('Last_Vac_year', 1)) or 1
        }
    )
    return vaccin

def create_infection(dossier, row):
    """Crée une infection"""
    infection_actuelle = clean_value(row.get('Cur_Infection1', ''))
    if not infection_actuelle:
        return None
    
    infection, created = Infection.objects.get_or_create(
        dossier=dossier,
        nomInfection=infection_actuelle,
        defaults={
            'typeInfection': clean_value(row.get('Cur_Infection1_type', ''))
        }
    )
    return infection

def import_complete_csv():
    """Importe toutes les données du CSV vers toutes les tables"""
    
    csv_file = 'base.csv'
    
    if not os.path.exists(csv_file):
        print(f"❌ Fichier {csv_file} non trouvé")
        return
    
    try:
        print(f"📖 Lecture du fichier {csv_file}...")
        df = pd.read_csv(csv_file, encoding='ISO-8859-1', sep=';')
        print(f"✅ Fichier lu avec succès. {len(df)} lignes trouvées.")
        
        # Statistiques
        stats = {
            'patients_created': 0,
            'patients_skipped': 0,
            'dossiers_created': 0,
            'analyses_created': 0,
            'resultats_created': 0,
            'alertes_created': 0,
            'vaccins_created': 0,
            'infections_created': 0,
            'errors': []
        }
        
        print("🔄 Début de l'importation complète...")
        
        for index, row in df.iterrows():
            try:
                # 1. Créer les objets de base
                profession = get_or_create_profession(row)
                residence = get_or_create_residence(row)
                logement = get_or_create_logement(row)
                comportement = get_or_create_comportement(row)
                alimentation = get_or_create_alimentation(row)
                
                # 2. Créer le patient
                patient = create_patient(row, profession, residence, logement, comportement, alimentation)
                if patient:
                    stats['patients_created'] += 1
                else:
                    stats['patients_skipped'] += 1
                    continue
                
                # 3. Créer le dossier médical
                dossier = create_dossier_medical(patient, row)
                if dossier:
                    stats['dossiers_created'] += 1
                
                # 4. Créer l'analyse
                analyse = create_analyse(dossier, row)
                if analyse:
                    stats['analyses_created'] += 1
                
                # 5. Créer le résultat d'analyse
                resultat = create_resultat_analyse(analyse, row)
                if resultat:
                    stats['resultats_created'] += 1
                
                # 6. Créer les alertes
                alertes = create_alerte(dossier, row)
                stats['alertes_created'] += len(alertes)
                
                # 7. Créer le vaccin
                vaccin = create_vaccin(dossier, row)
                if vaccin:
                    stats['vaccins_created'] += 1
                
                # 8. Créer l'infection
                infection = create_infection(dossier, row)
                if infection:
                    stats['infections_created'] += 1
                
                # Afficher le progrès
                if (index + 1) % 50 == 0:
                    print(f"📈 Traité {index + 1}/{len(df)} lignes...")
                
            except Exception as e:
                error_msg = f"Ligne {index + 1}: {str(e)}"
                stats['errors'].append(error_msg)
                continue
        
        # Résultats finaux
        print("\n" + "="*60)
        print("📊 RÉSULTATS DE L'IMPORTATION COMPLÈTE")
        print("="*60)
        print(f"✅ Patients créés: {stats['patients_created']}")
        print(f"⏭️  Patients ignorés: {stats['patients_skipped']}")
        print(f"📋 Dossiers médicaux créés: {stats['dossiers_created']}")
        print(f"🔬 Analyses créées: {stats['analyses_created']}")
        print(f"📊 Résultats d'analyses créés: {stats['resultats_created']}")
        print(f"⚠️  Alertes créées: {stats['alertes_created']}")
        print(f"💉 Vaccins créés: {stats['vaccins_created']}")
        print(f"🦠 Infections créées: {stats['infections_created']}")
        print(f"❌ Erreurs: {len(stats['errors'])}")
        
        if stats['errors']:
            print("\n🔍 Premières erreurs:")
            for error in stats['errors'][:5]:
                print(f"   - {error}")
        
        print(f"\n🎉 Importation complète terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'importation: {str(e)}")

if __name__ == "__main__":
    print("🚀 Démarrage de l'importation complète CSV...")
    import_complete_csv() 
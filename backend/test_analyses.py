#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from api.models import Patient, DossierMedical, Analyse, ResultatAnalyse

def test_analyses_data():
    print("=== Test des données d'analyses ===")
    
    # Récupérer tous les patients
    patients = Patient.objects.all()
    print(f"Nombre total de patients: {patients.count()}")
    
    for patient in patients:
        print(f"\n--- Patient {patient.idPatient} ---")
        
        # Récupérer les dossiers médicaux
        dossiers = patient.dossiermedical_set.all()
        print(f"Nombre de dossiers: {dossiers.count()}")
        
        for dossier in dossiers:
            print(f"  Dossier {dossier.idDossier}: {dossier.commentaireGeneral}")
            
            # Récupérer les analyses
            analyses = dossier.analyse_set.all()
            print(f"  Nombre d'analyses: {analyses.count()}")
            
            for analyse in analyses:
                print(f"    Analyse {analyse.idAnalyse}: {analyse.typeAnalyse} ({analyse.dateAnalyse})")
                
                # Vérifier la relation avec ResultatAnalyse
                try:
                    resultat = analyse.resultatanalyse
                    print(f"      ✓ Résultat trouvé: {resultat.idResultatAnalyse}")
                    print(f"        Glycémie: {resultat.glycemie}")
                    print(f"        Cholestérol: {resultat.cholesterol}")
                    print(f"        Triglycéride: {resultat.triglyceride}")
                    print(f"        HDL: {resultat.hdl}")
                    print(f"        LDL: {resultat.ldl}")
                    print(f"        Créatinine: {resultat.creatinine}")
                    print(f"        Urée: {resultat.uree}")
                    print(f"        Protéinurie: {resultat.proteinurie}")
                except ResultatAnalyse.DoesNotExist:
                    print(f"      ✗ Aucun résultat d'analyse trouvé")
                
                # Test avec hasattr
                print(f"      hasattr(analyse, 'resultatanalyse'): {hasattr(analyse, 'resultatanalyse')}")
                
                # Test avec getattr
                try:
                    ra = getattr(analyse, 'resultatanalyse', None)
                    print(f"      getattr(analyse, 'resultatanalyse'): {ra}")
                except Exception as e:
                    print(f"      Erreur getattr: {e}")

if __name__ == "__main__":
    test_analyses_data() 
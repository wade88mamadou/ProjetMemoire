import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from api.models import ResultatAnalyse
from api.services import DetectionSeuilsService


def audit_resultats():
    print('--- Audit rétroactif des seuils médicaux ---')
    total_alertes = 0
    for resultat in ResultatAnalyse.objects.all():
        alertes = DetectionSeuilsService.detecter_violations_resultat_analyse(resultat)
        if alertes:
            print(f'Résultat ID {resultat.idResultatAnalyse} : {len(alertes)} alerte(s) générée(s)')
            total_alertes += len(alertes)
    print(f'Total alertes générées : {total_alertes}')

if __name__ == '__main__':
    audit_resultats()
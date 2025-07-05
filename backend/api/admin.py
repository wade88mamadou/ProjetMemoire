from django.contrib import admin
from .models import (
    Patient, Profession, Logement, Residence, Comportement, Utilisateur,
    DossierMedical, Rapport, Vaccin, Infection, RegleConformite,
    ParametreConformite, Alerte, Analyse, ResultatAnalyse, Alimentation, Acces
)

admin.site.register(Patient)
admin.site.register(Profession)
admin.site.register(Logement)
admin.site.register(Residence)
admin.site.register(Comportement)
admin.site.register(Utilisateur)
admin.site.register(DossierMedical)
admin.site.register(Rapport)
admin.site.register(Vaccin)
admin.site.register(Infection)
admin.site.register(RegleConformite)
admin.site.register(ParametreConformite)
admin.site.register(Alerte)
admin.site.register(Analyse)
admin.site.register(ResultatAnalyse)
admin.site.register(Alimentation)
admin.site.register(Acces)

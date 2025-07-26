
# Optimisations pour les ViewSets
# À ajouter dans api/views.py

class PatientViewSet(AuditAccessMixin, viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    
    def get_queryset(self):
        return Patient.objects.select_related(
            'profession', 'residence', 'logement', 
            'comportement', 'alimentation'
        ).all()

class DossierMedicalViewSet(AuditAccessMixin, viewsets.ModelViewSet):
    serializer_class = DossierMedicalSerializer
    
    def get_queryset(self):
        return DossierMedical.objects.select_related(
            'patient__profession', 'patient__residence'
        ).prefetch_related(
            'analyse_set', 'alerte_set', 'vaccin_set', 'infection_set'
        ).all()

class AlerteViewSet(viewsets.ModelViewSet):
    serializer_class = AlerteSerializer
    
    def get_queryset(self):
        return Alerte.objects.select_related(
            'dossier__patient', 'utilisateur'
        ).order_by('-dateAlerte', '-idAlerte')

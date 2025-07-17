from .models import Acces
from django.utils import timezone

def log_audit(user, type_acces, donnees_concernees, regle=None, statut=None):
    """
    Enregistre un accès (audit) dans la table Acces.
    - user : utilisateur Django (request.user)
    - type_acces : 'CONSULTATION', 'MODIFICATION', 'SUPPRESSION', 'EXPORT', etc.
    - donnees_concernees : description courte (ex: 'Dossier #42')
    - regle : instance de RegleConformite (optionnel)
    - statut : 'SUCCES', 'REFUSE', etc. (optionnel, ignoré car non supporté par le modèle)
    """
    Acces.objects.create(
        dateAcces=timezone.now(),
        utilisateur=user,
        typeAcces=type_acces,
        donnees_concernees=donnees_concernees,
        regle=regle
        # statut=statut  # <-- supprimé car non supporté par le modèle
    )

class AuditAccessMixin:
    audit_model_name = None  # À surcharger dans le ViewSet si besoin

    def get_audit_model_name(self, instance):
        # Utilise le nom du modèle ou la valeur surchargée
        if self.audit_model_name:
            return self.audit_model_name
        return instance.__class__.__name__

    def log_audit_action(self, request, action, instance):
        donnees = f"{self.get_audit_model_name(instance)} #{getattr(instance, 'pk', None)}"
        log_audit(
            user=request.user,
            type_acces=action,
            donnees_concernees=donnees
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self.log_audit_action(request, 'CONSULTATION', instance)
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        self.log_audit_action(request, 'MODIFICATION', instance)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        self.log_audit_action(request, 'MODIFICATION', instance)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.log_audit_action(request, 'SUPPRESSION', instance)
        return super().destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # On récupère l'instance créée si possible
        if hasattr(self, 'get_object'):
            try:
                instance = self.get_object()
                self.log_audit_action(request, 'CREATION', instance)
            except Exception:
                pass
        return response 
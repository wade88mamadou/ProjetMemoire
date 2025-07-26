"""
Service de gestion des alertes de conformité RGPD/HIPAA/CDP
Gère la détection, création et notification des alertes de conformité
"""

import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.core.cache import cache
from django.conf import settings
from .models import (
    TypeAlerteConformite, AlerteConformite, RegleAlerteConformite,
    NotificationConformite, AuditConformite, Patient, DossierMedical,
    Utilisateur, Acces
)

logger = logging.getLogger(__name__)

class ServiceAlertesConformite:
    """Service principal pour la gestion des alertes de conformité"""
    
    @staticmethod
    def initialiser_types_alertes():
        """Initialise tous les types d'alertes de conformité"""
        types_alertes = [
            # RGPD Alertes
            {
                'code': 'RGPD_CONSENTEMENT_EXPIRE',
                'nom': 'Consentement RGPD expiré',
                'description': 'Le consentement du patient pour le traitement de ses données a expiré',
                'norme_conformite': 'RGPD',
                'niveau_critique': 3,
                'delai_notification': 24
            },
            {
                'code': 'RGPD_DROIT_ACCES',
                'nom': 'Demande de droit d\'accès',
                'description': 'Le patient a demandé l\'accès à ses données personnelles',
                'norme_conformite': 'RGPD',
                'niveau_critique': 2,
                'delai_notification': 48
            },
            {
                'code': 'RGPD_DROIT_RECTIFICATION',
                'nom': 'Demande de droit de rectification',
                'description': 'Le patient a demandé la rectification de ses données',
                'norme_conformite': 'RGPD',
                'niveau_critique': 2,
                'delai_notification': 48
            },
            {
                'code': 'RGPD_DROIT_EFFACEMENT',
                'nom': 'Demande de droit d\'effacement',
                'description': 'Le patient a demandé l\'effacement de ses données (droit à l\'oubli)',
                'norme_conformite': 'RGPD',
                'niveau_critique': 4,
                'delai_notification': 24
            },
            {
                'code': 'RGPD_VIOLATION_DONNEES',
                'nom': 'Violation de données personnelles',
                'description': 'Violation de la sécurité des données personnelles',
                'norme_conformite': 'RGPD',
                'niveau_critique': 5,
                'delai_notification': 1
            },
            
            # HIPAA Alertes
            {
                'code': 'HIPAA_PHI_ACCES_NON_AUTORISE',
                'nom': 'Accès non autorisé aux PHI',
                'description': 'Accès non autorisé aux informations de santé protégées (PHI)',
                'norme_conformite': 'HIPAA',
                'niveau_critique': 5,
                'delai_notification': 1
            },
            {
                'code': 'HIPAA_BREACH_NOTIFICATION',
                'nom': 'Notification de violation HIPAA',
                'description': 'Violation de données de santé nécessitant une notification',
                'norme_conformite': 'HIPAA',
                'niveau_critique': 5,
                'delai_notification': 1
            },
            {
                'code': 'HIPAA_AUDIT_TRAIL_MANQUANT',
                'nom': 'Audit trail manquant',
                'description': 'Traçabilité insuffisante des accès aux données de santé',
                'norme_conformite': 'HIPAA',
                'niveau_critique': 3,
                'delai_notification': 24
            },
            {
                'code': 'HIPAA_ENCRYPTION_MANQUANT',
                'nom': 'Chiffrement manquant',
                'description': 'Données de santé non chiffrées lors du stockage/transmission',
                'norme_conformite': 'HIPAA',
                'niveau_critique': 4,
                'delai_notification': 12
            },
            
            # CDP Sénégal Alertes
            {
                'code': 'CDP_NOTIFICATION_VIOLATION',
                'nom': 'Notification CDP violation',
                'description': 'Violation nécessitant une notification à la CDP Sénégal',
                'norme_conformite': 'CDP',
                'niveau_critique': 5,
                'delai_notification': 1
            },
            {
                'code': 'CDP_SECRET_MEDICAL_VIOLATION',
                'nom': 'Violation du secret médical',
                'description': 'Violation du secret médical protégé par la loi sénégalaise',
                'norme_conformite': 'CDP',
                'niveau_critique': 5,
                'delai_notification': 1
            },
            {
                'code': 'CDP_CONSENTEMENT_ECLAIRE',
                'nom': 'Consentement éclairé manquant',
                'description': 'Consentement éclairé du patient manquant ou invalide',
                'norme_conformite': 'CDP',
                'niveau_critique': 3,
                'delai_notification': 24
            },
            
            # Alertes Générales
            {
                'code': 'ACCES_NON_AUTORISE',
                'nom': 'Accès non autorisé',
                'description': 'Tentative d\'accès non autorisé à des données sensibles',
                'norme_conformite': 'GENERAL',
                'niveau_critique': 4,
                'delai_notification': 12
            },
            {
                'code': 'SUPPRESSION_ACCIDENTELLE',
                'nom': 'Suppression accidentelle',
                'description': 'Suppression accidentelle de données médicales',
                'norme_conformite': 'GENERAL',
                'niveau_critique': 5,
                'delai_notification': 1
            },
            {
                'code': 'CONSULTATION_EXCESSIVE',
                'nom': 'Consultation excessive',
                'description': 'Consultation excessive de dossiers patients',
                'norme_conformite': 'GENERAL',
                'niveau_critique': 3,
                'delai_notification': 24
            },
            {
                'code': 'SEUIL_MEDICAL_DEPASSE',
                'nom': 'Seuil médical dépassé',
                'description': 'Seuil médical critique dépassé nécessitant une intervention',
                'norme_conformite': 'GENERAL',
                'niveau_critique': 4,
                'delai_notification': 6
            },
        ]
        
        for type_alerte_data in types_alertes:
            TypeAlerteConformite.objects.get_or_create(
                code=type_alerte_data['code'],
                defaults=type_alerte_data
            )
        
        logger.info(f"Initialisation de {len(types_alertes)} types d'alertes de conformité")
    
    @staticmethod
    def detecter_violations_rgpd():
        """Détecte les violations RGPD"""
        violations = []
        
        # Vérifier les consentements expirés
        date_limite = timezone.now().date() - timedelta(days=365)  # 1 an
        patients_sans_consentement = Patient.objects.filter(
            dossiermedical__dateCreation__lt=date_limite
        ).distinct()
        
        for patient in patients_sans_consentement:
            violations.append({
                'type': 'RGPD_CONSENTEMENT_EXPIRE',
                'patient': patient,
                'description': f'Consentement RGPD expiré pour le patient {patient.id_code}',
                'niveau_critique': 3
            })
        
        # Vérifier les accès non autorisés
        acces_recents = Acces.objects.filter(
            dateAcces__gte=timezone.now() - timedelta(hours=24)
        )
        
        for acces in acces_recents:
            if not acces.utilisateur or not acces.utilisateur.is_authenticated:
                violations.append({
                    'type': 'RGPD_DROIT_ACCES',
                    'utilisateur': acces.utilisateur,
                    'description': f'Accès non autorisé détecté: {acces.typeAcces}',
                    'niveau_critique': 4
                })
        
        return violations
    
    @staticmethod
    def detecter_violations_hipaa():
        """Détecte les violations HIPAA"""
        violations = []
        
        # Vérifier les accès aux PHI sans autorisation
        acces_phi = Acces.objects.filter(
            dateAcces__gte=timezone.now() - timedelta(hours=24),
            donnees_concernees__icontains='PHI'
        )
        
        for acces in acces_phi:
            if not acces.utilisateur or not acces.utilisateur.is_authenticated:
                violations.append({
                    'type': 'HIPAA_PHI_ACCES_NON_AUTORISE',
                    'utilisateur': acces.utilisateur,
                    'description': f'Accès non autorisé aux PHI: {acces.typeAcces}',
                    'niveau_critique': 5
                })
        
        # Vérifier l'audit trail
        actions_sans_audit = AuditConformite.objects.filter(
            date_action__gte=timezone.now() - timedelta(hours=1),
            details={}
        ).count()
        
        if actions_sans_audit > 10:
            violations.append({
                'type': 'HIPAA_AUDIT_TRAIL_MANQUANT',
                'description': f'{actions_sans_audit} actions sans audit trail détaillé',
                'niveau_critique': 3
            })
        
        return violations
    
    @staticmethod
    def detecter_violations_cdp():
        """Détecte les violations CDP Sénégal"""
        violations = []
        
        # Vérifier les violations du secret médical
        consultations_excessives = AuditConformite.objects.filter(
            type_action='LECTURE',
            date_action__gte=timezone.now() - timedelta(hours=1)
        ).values('utilisateur').annotate(
            count=Count('id')
        ).filter(count__gt=50)
        
        for consultation in consultations_excessives:
            violations.append({
                'type': 'CDP_SECRET_MEDICAL_VIOLATION',
                'utilisateur_id': consultation['utilisateur'],
                'description': f'Consultation excessive: {consultation["count"]} dossiers en 1h',
                'niveau_critique': 4
            })
        
        # Vérifier les consentements éclairés
        patients_sans_consentement = Patient.objects.filter(
            dossiermedical__isnull=False
        ).exclude(
            dossiermedical__commentaireGeneral__icontains='consentement'
        )
        
        for patient in patients_sans_consentement[:10]:  # Limiter pour éviter trop d'alertes
            violations.append({
                'type': 'CDP_CONSENTEMENT_ECLAIRE',
                'patient': patient,
                'description': f'Consentement éclairé manquant pour le patient {patient.id_code}',
                'niveau_critique': 3
            })
        
        return violations
    
    @staticmethod
    def creer_alerte_conformite(type_code, titre, description, niveau_critique, 
                               utilisateur=None, patient=None, dossier=None, details_techniques=None):
        """Crée une nouvelle alerte de conformité"""
        try:
            type_alerte = TypeAlerteConformite.objects.get(code=type_code)
            
            alerte = AlerteConformite.objects.create(
                type_alerte=type_alerte,
                titre=titre,
                description=description,
                niveau_critique=niveau_critique,
                utilisateur_origine=utilisateur,
                patient=patient,
                dossier=dossier,
                details_techniques=details_techniques or {},
                statut='NOUVELLE'
            )
            
            # Créer les notifications appropriées
            ServiceAlertesConformite.creer_notifications_alerte(alerte)
            
            logger.info(f"Alerte de conformité créée: {alerte.titre} (Niveau: {niveau_critique})")
            return alerte
            
        except TypeAlerteConformite.DoesNotExist:
            logger.error(f"Type d'alerte non trouvé: {type_code}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'alerte: {e}")
            return None
    
    @staticmethod
    def creer_notifications_alerte(alerte):
        """Crée les notifications appropriées pour une alerte"""
        try:
            # Notifier l'admin par défaut
            if alerte.niveau_critique >= 3:
                admins = Utilisateur.objects.filter(role='ADMIN', is_active=True)
                for admin in admins:
                    NotificationConformite.objects.create(
                        alerte=alerte,
                        destinataire=admin,
                        type_notification='EMAIL',
                        destinataire_email=admin.email,
                        sujet=f"Alerte de conformité: {alerte.titre}",
                        contenu=f"Une alerte de conformité a été générée:\n\n{alerte.description}\n\nNiveau: {alerte.get_niveau_critique_display()}\nDate: {alerte.date_creation}"
                    )
            
            # Notifier le DPO si nécessaire
            if alerte.niveau_critique >= 4:
                # Chercher un utilisateur avec le rôle DPO ou admin
                dpo_users = Utilisateur.objects.filter(
                    Q(role='ADMIN') | Q(username__icontains='dpo'),
                    is_active=True
                )
                for dpo in dpo_users:
                    NotificationConformite.objects.create(
                        alerte=alerte,
                        destinataire=dpo,
                        type_notification='EMAIL',
                        destinataire_email=dpo.email,
                        sujet=f"ALERTE CRITIQUE - Conformité: {alerte.titre}",
                        contenu=f"ALERTE CRITIQUE DE CONFORMITÉ:\n\n{alerte.description}\n\nNiveau: {alerte.get_niveau_critique_display()}\nAction immédiate requise!"
                    )
            
            # Notifier la CDP si nécessaire
            if alerte.niveau_critique == 5:
                alerte.notifie_cdp = True
                alerte.date_notification_cdp = timezone.now()
                alerte.save()
                
                # Créer une notification pour la CDP
                NotificationConformite.objects.create(
                    alerte=alerte,
                    type_notification='API',
                    sujet=f"Notification CDP - Violation: {alerte.titre}",
                    contenu=f"Violation nécessitant notification CDP:\n\n{alerte.description}"
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de la création des notifications: {e}")
    
    @staticmethod
    def executer_surveillance_conformite():
        """Exécute la surveillance complète de conformité"""
        logger.info("Démarrage de la surveillance de conformité")
        
        # Détecter les violations
        violations_rgpd = ServiceAlertesConformite.detecter_violations_rgpd()
        violations_hipaa = ServiceAlertesConformite.detecter_violations_hipaa()
        violations_cdp = ServiceAlertesConformite.detecter_violations_cdp()
        
        # Créer les alertes
        alertes_crees = []
        
        for violation in violations_rgpd + violations_hipaa + violations_cdp:
            alerte = ServiceAlertesConformite.creer_alerte_conformite(
                type_code=violation['type'],
                titre=f"Violation {violation['type']}",
                description=violation['description'],
                niveau_critique=violation['niveau_critique'],
                utilisateur=violation.get('utilisateur'),
                patient=violation.get('patient'),
                dossier=violation.get('dossier')
            )
            if alerte:
                alertes_crees.append(alerte)
        
        logger.info(f"Surveillance terminée: {len(alertes_crees)} alertes créées")
        return alertes_crees
    
    @staticmethod
    def obtenir_statistiques_conformite():
        """Obtient les statistiques de conformité"""
        date_limite_7j = timezone.now() - timedelta(days=7)
        date_limite_30j = timezone.now() - timedelta(days=30)
        
        # Statistiques générales
        total_alertes = AlerteConformite.objects.count()
        alertes_nouvelles = AlerteConformite.objects.filter(statut='NOUVELLE').count()
        alertes_en_cours = AlerteConformite.objects.filter(statut='EN_COURS').count()
        alertes_resolues = AlerteConformite.objects.filter(statut='RESOLUE').count()
        
        # Par niveau de criticité
        alertes_critiques = AlerteConformite.objects.filter(niveau_critique=4).count()
        alertes_urgentes = AlerteConformite.objects.filter(niveau_critique=5).count()
        
        # Par norme de conformité
        alertes_rgpd = AlerteConformite.objects.filter(
            type_alerte__norme_conformite='RGPD'
        ).count()
        alertes_hipaa = AlerteConformite.objects.filter(
            type_alerte__norme_conformite='HIPAA'
        ).count()
        alertes_cdp = AlerteConformite.objects.filter(
            type_alerte__norme_conformite='CDP'
        ).count()
        
        # Tendances
        alertes_7_jours = AlerteConformite.objects.filter(
            date_creation__gte=date_limite_7j
        ).count()
        alertes_30_jours = AlerteConformite.objects.filter(
            date_creation__gte=date_limite_30j
        ).count()
        
        # Temps moyen de résolution
        alertes_resolues_recentes = AlerteConformite.objects.filter(
            statut='RESOLUE',
            date_resolution__isnull=False
        )
        temps_moyen_resolution = alertes_resolues_recentes.aggregate(
            avg_time=Avg('date_resolution' - 'date_creation')
        )['avg_time']
        
        # Taux de conformité (basé sur les alertes résolues)
        total_alertes_resolues = alertes_resolues_recentes.count()
        if total_alertes > 0:
            taux_conformite = (total_alertes_resolues / total_alertes) * 100
        else:
            taux_conformite = 100.0
        
        return {
            'total_alertes': total_alertes,
            'alertes_nouvelles': alertes_nouvelles,
            'alertes_en_cours': alertes_en_cours,
            'alertes_resolues': alertes_resolues,
            'alertes_critiques': alertes_critiques,
            'alertes_urgentes': alertes_urgentes,
            'alertes_rgpd': alertes_rgpd,
            'alertes_hipaa': alertes_hipaa,
            'alertes_cdp': alertes_cdp,
            'alertes_7_jours': alertes_7_jours,
            'alertes_30_jours': alertes_30_jours,
            'temps_moyen_resolution': temps_moyen_resolution.total_seconds() / 3600 if temps_moyen_resolution else 0,
            'taux_conformite': taux_conformite
        } 
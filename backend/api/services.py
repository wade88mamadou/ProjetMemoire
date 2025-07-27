from django.utils import timezone
from .models import ParametreConformite, Alerte, DossierMedical, Utilisateur
import logging
from .models import RegleConformite, ParametreConformite, Alerte

logger = logging.getLogger(__name__)

class DetectionSeuilsService:
    """
    Service pour la détection automatique des seuils médicaux dépassés
    et la génération d'alertes de conformité
    """
    
    @staticmethod
    def detecter_violation_seuil(nom_parametre, valeur, utilisateur=None, dossier=None):
        """
        Détecte si une valeur médicale dépasse les seuils configurés
        et génère une alerte si nécessaire
        
        Args:
            nom_parametre (str): Nom du paramètre médical (ex: 'Glycémie', 'Température')
            valeur (float): Valeur mesurée
            utilisateur (Utilisateur): Utilisateur qui a enregistré la valeur
            dossier (DossierMedical): Dossier médical concerné
            
        Returns:
            Alerte|None: Alerte créée si seuil dépassé, None sinon
        """
        try:
            # Chercher le paramètre de conformité correspondant
            parametre = ParametreConformite.objects.filter(
                nom__iexact=nom_parametre
            ).first()
            
            if not parametre:
                logger.info(f"Aucun seuil configuré pour le paramètre: {nom_parametre}")
                return None
            
            # Vérifier si la valeur dépasse les seuils
            seuil_min = float(parametre.seuilMin)
            seuil_max = float(parametre.seuilMax)
            
            if valeur < seuil_min or valeur > seuil_max:
                # Seuil dépassé - créer une alerte
                return DetectionSeuilsService._creer_alerte_seuil(
                    parametre, valeur, seuil_min, seuil_max, utilisateur, dossier
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection de seuil pour {nom_parametre}: {e}")
            return None
    
    @staticmethod
    def _creer_alerte_seuil(parametre, valeur, seuil_min, seuil_max, utilisateur, dossier):
        """
        Crée une alerte de violation de seuil médical
        """
        try:
            # Déterminer la gravité selon l'écart
            ecart_min = abs(valeur - seuil_min)
            ecart_max = abs(valeur - seuil_max)
            ecart_maximal = max(ecart_min, ecart_max)
            
            # Calculer le pourcentage d'écart
            marge = seuil_max - seuil_min
            pourcentage_ecart = (ecart_maximal / marge) * 100 if marge > 0 else 0
            
            # Déterminer la gravité
            if pourcentage_ecart > 50:
                gravite = 'critique'
                notifie_cdp = True
            elif pourcentage_ecart > 25:
                gravite = 'warning'
                notifie_cdp = False
            else:
                gravite = 'info'
                notifie_cdp = False
            
            # Construire le message
            if valeur < seuil_min:
                message = f"Valeur {parametre.nom} ({valeur} {parametre.unite}) en dessous du seuil minimum ({seuil_min} {parametre.unite})"
            else:
                message = f"Valeur {parametre.nom} ({valeur} {parametre.unite}) au-dessus du seuil maximum ({seuil_max} {parametre.unite})"
            
            # Informations sur la règle de conformité
            regle_info = ""
            if parametre.regle:
                regle_info = f" - Règle: {parametre.regle.nomRegle} ({parametre.regle.typeRegle})"
            
            message += regle_info
            
            # Créer l'alerte
            alerte = Alerte.objects.create(
                typeAlerte=f"Violation seuil médical - {parametre.nom}",
                message=message,
                dateAlerte=timezone.now().date(),
                gravite=gravite,
                notifie_cdp=notifie_cdp,
                utilisateur=utilisateur,
                dossier=dossier,
                donnees_concernees=f"Paramètre: {parametre.nom}, Valeur: {valeur} {parametre.unite}, Seuils: {seuil_min}-{seuil_max} {parametre.unite}"
            )
            
            logger.info(f"Alerte créée: {alerte.typeAlerte} - {message}")
            return alerte
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'alerte: {e}")
            return None
    
    @staticmethod
    def detecter_violations_resultat_analyse(resultat_analyse, utilisateur=None):
        """
        Détecte les violations de seuils pour tous les paramètres d'un résultat d'analyse
        """
        alertes_crees = []
        dossier = resultat_analyse.analyse.dossier if resultat_analyse.analyse else None
        
        # Mapping des champs du modèle vers les noms de paramètres
        champs_medicaux = {
            'glycemie': 'Glycémie',
            'cholesterol': 'Cholestérol',
            'triglyceride': 'Triglycérides',
            'hdl': 'HDL',
            'ldl': 'LDL',
            'creatinine': 'Créatinine',
            'uree': 'Urée',
            'proteinurie': 'Proteinurie'
        }
        
        for champ, nom_parametre in champs_medicaux.items():
            valeur = getattr(resultat_analyse, champ, None)
            if valeur is not None:
                alerte = DetectionSeuilsService.detecter_violation_seuil(
                    nom_parametre, valeur, utilisateur, dossier
                )
                if alerte:
                    alertes_crees.append(alerte)
        
        return alertes_crees
    
    @staticmethod
    def detecter_violations_patient(patient, utilisateur=None):
        """
        Détecte les violations de seuils pour les données du patient (poids, taille, etc.)
        """
        alertes_crees = []
        
        # Données anthropométriques
        if patient.poids is not None:
            alerte = DetectionSeuilsService.detecter_violation_seuil(
                'Poids', patient.poids, utilisateur, None
            )
            if alerte:
                alertes_crees.append(alerte)
        
        if patient.taille is not None:
            alerte = DetectionSeuilsService.detecter_violation_seuil(
                'Taille', patient.taille, utilisateur, None
            )
            if alerte:
                alertes_crees.append(alerte)
        
        # Calculer et vérifier le BMI si poids et taille sont disponibles
        if patient.poids is not None and patient.taille is not None and patient.taille > 0:
            bmi = patient.poids / ((patient.taille / 100) ** 2)
            alerte = DetectionSeuilsService.detecter_violation_seuil(
                'BMI', bmi, utilisateur, None
            )
            if alerte:
                alertes_crees.append(alerte)
        
        return alertes_crees


class AuditTrailService:
    """
    Service pour l'audit trail (traçabilité des accès et modifications)
    """
    
    @staticmethod
    def enregistrer_acces(utilisateur, type_acces, donnees_concernees=None):
        """
        Enregistre un accès aux données médicales
        """
        try:
            from .models import Acces
            
            acces = Acces.objects.create(
                typeAcces=type_acces,
                dateAcces=timezone.now().date(),
                utilisateur=utilisateur,
                donnees_concernees=donnees_concernees
            )
            
            logger.info(f"Accès enregistré: {utilisateur.username} - {type_acces}")
            return acces
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'accès: {e}")
            return None
    
    @staticmethod
    def enregistrer_modification(utilisateur, type_modification, donnees_avant, donnees_apres, objet_modifie=None):
        """
        Enregistre une modification de données médicales
        """
        try:
            message = f"Modification {type_modification} par {utilisateur.username}"
            if donnees_avant and donnees_apres:
                message += f" - Avant: {donnees_avant}, Après: {donnees_apres}"
            
            alerte = Alerte.objects.create(
                typeAlerte=f"Modification données - {type_modification}",
                message=message,
                dateAlerte=timezone.now().date(),
                gravite='info',
                notifie_cdp=False,
                utilisateur=utilisateur,
                donnees_concernees=f"Type: {type_modification}, Objet: {objet_modifie}"
            )
            
            logger.info(f"Modification enregistrée: {message}")
            return alerte
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de la modification: {e}")
            return None 
        
class ConformiteAlertService:
    """
    Service pour la gestion des alertes de conformité RGPD, HIPAA, CDP
    """

    @staticmethod
    def alerte_acces_non_autorise(utilisateur, donnees_concernees):
        from .models import Alerte
        message = f"Accès non autorisé détecté par {utilisateur.username} sur {donnees_concernees} - RGPD"
        return Alerte.objects.create(
            typeAlerte="Accès non autorisé",
            message=message,
            dateAlerte=timezone.now().date(),
            gravite="critique",
            notifie_cdp=True,
            utilisateur=utilisateur,
            donnees_concernees=donnees_concernees,
            norme_concernee="RGPD"
        )

    @staticmethod
    def alerte_export_massif(utilisateur, nb_dossiers):
        from .models import Alerte
        message = f"Export massif de {nb_dossiers} dossiers par {utilisateur.username} - RGPD"
        return Alerte.objects.create(
            typeAlerte="Export massif de données",
            message=message,
            dateAlerte=timezone.now().date(),
            gravite="warning",
            notifie_cdp=True,
            utilisateur=utilisateur,
            donnees_concernees=f"{nb_dossiers} dossiers",
            norme_concernee="RGPD"
        )

    @staticmethod
    def alerte_modification_consentement(utilisateur, patient):
        from .models import Alerte
        message = f"Modification du consentement patient {patient.id} par {utilisateur.username} - RGPD"
        return Alerte.objects.create(
            typeAlerte="Modification consentement",
            message=message,
            dateAlerte=timezone.now().date(),
            gravite="info",
            notifie_cdp=True,
            utilisateur=utilisateur,
            donnees_concernees=f"Patient: {patient.id}",
            norme_concernee="RGPD"
        )
    
        # --- HIPAA ---
    @staticmethod
    def alerte_acces_hors_horaire(utilisateur, donnees_concernees, heure_acces):
        from .models import Alerte
        message = f"Accès hors horaire autorisé ({heure_acces}) par {utilisateur.username} sur {donnees_concernees} - HIPAA"
        return Alerte.objects.create(
            typeAlerte="Accès hors horaire",
            message=message,
            dateAlerte=timezone.now().date(),
            gravite="warning",
            notifie_cdp=True,
            utilisateur=utilisateur,
            donnees_concernees=donnees_concernees,
            norme_concernee="HIPAA"
        )

    @staticmethod
    def alerte_consultation_excessive(utilisateur, nb_dossiers, periode):
        from .models import Alerte
        message = f"Consultation excessive de {nb_dossiers} dossiers en {periode} par {utilisateur.username} - HIPAA"
        return Alerte.objects.create(
            typeAlerte="Consultation excessive",
            message=message,
            dateAlerte=timezone.now().date(),
            gravite="warning",
            notifie_cdp=True,
            utilisateur=utilisateur,
            donnees_concernees=f"{nb_dossiers} dossiers en {periode}",
            norme_concernee="HIPAA"
        )

    @staticmethod
    def alerte_modification_donnee_sensible(utilisateur, champ_modifie, objet_modifie):
        from .models import Alerte
        message = f"Modification de donnée sensible ({champ_modifie}) sur {objet_modifie} par {utilisateur.username} - HIPAA"
        return Alerte.objects.create(
            typeAlerte="Modification donnée sensible",
            message=message,
            dateAlerte=timezone.now().date(),
            gravite="info",
            notifie_cdp=True,
            utilisateur=utilisateur,
            donnees_concernees=f"{champ_modifie} sur {objet_modifie}",
            norme_concernee="HIPAA"
        )

    # --- CDP ---
    @staticmethod
    def alerte_non_respect_regle_interne(utilisateur, regle, donnees_concernees):
        from .models import Alerte
        message = f"Non-respect de la règle interne ({regle}) par {utilisateur.username} sur {donnees_concernees} - CDP"
        return Alerte.objects.create(
            typeAlerte="Non-respect règle interne",
            message=message,
            dateAlerte=timezone.now().date(),
            gravite="critique",
            notifie_cdp=True,
            utilisateur=utilisateur,
            donnees_concernees=donnees_concernees,
            norme_concernee="CDP"
        )

    @staticmethod
    def alerte_suppression_donnee(utilisateur, objet_supprime):
        from .models import Alerte
        message = f"Suppression de donnée ({objet_supprime}) par {utilisateur.username} - CDP"
        return Alerte.objects.create(
            typeAlerte="Suppression de donnée",
            message=message,
            dateAlerte=timezone.now().date(),
            gravite="warning",
            notifie_cdp=True,
            utilisateur=utilisateur,
            donnees_concernees=f"{objet_supprime}",
            norme_concernee="CDP"
        )   



def verifier_et_declencher_alerte(type_acces, utilisateur, donnees_concernees, extra=None):
    """
    Vérifie la configuration des règles de sécurité et déclenche une alerte si besoin.
    type_acces: ex: 'CONSULTATION', 'SUPPRESSION', 'EXPORT', etc.
    utilisateur: Utilisateur concerné
    donnees_concernees: description ou objet concerné
    extra: dict, infos complémentaires (ex: nombre de tentatives)
    """
    # from .models import RegleConformite, ParametreConformite, Alerte

    # 1. Chercher la règle active correspondante
    regle = RegleConformite.objects.filter(
        nomRegle__iexact=type_acces,
        is_active=True
    ).first()
    if not regle:
        return None  # Pas de règle active pour cet événement

    # 2. Chercher le seuil associé (si besoin)
    param = ParametreConformite.objects.filter(regle=regle).first()
    seuil_min = getattr(param, 'seuilMin', None)
    seuil_max = getattr(param, 'seuilMax', None)

    # 3. Vérifier le seuil (exemple pour nombre de tentatives)
    declencher = True
    if seuil_min is not None and extra and 'valeur' in extra:
        if extra['valeur'] < seuil_min:
            declencher = False
    if seuil_max is not None and extra and 'valeur' in extra:
        if extra['valeur'] > seuil_max:
            declencher = True

    if declencher:
        # 4. Déclencher l'alerte selon le type d'accès
        return Alerte.objects.create(
            typeAlerte=type_acces,
            message=f"Alerte déclenchée pour {type_acces} par {utilisateur.username}",
            dateAlerte=timezone.now().date(),
            gravite="warning",
            notifie_cdp=True,
            utilisateur=utilisateur,
            donnees_concernees=str(donnees_concernees),
            norme_concernee="SECURITE"
        )
    return None
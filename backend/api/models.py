from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, AbstractUser
from django.utils import timezone


# Utilisateur (héritage)
class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrateur'),
        ('MEDECIN', 'Medecin'),
        ('user_simple', 'User Simple'),
    ]
    
    specialite = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user_simple'
    )
    statut = models.CharField(max_length=50, blank=True, null=True)
    medecin = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, limit_choices_to={'role': 'MEDECIN'}, related_name='users_simples')
    must_change_password = models.BooleanField(default=True, help_text="L'utilisateur doit changer son mot de passe à la première connexion")
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
    
    def __str__(self):
        return f"{self.username}"
    
    @property
    def is_admin(self):
        return self.role == 'ADMIN' or self.is_superuser
    
    @property
    def is_medecin(self):
        return self.role == 'MEDECIN'
    
    @property
    def is_user_simple(self):
        return self.role == 'user_simple'

class Profession(models.Model):
    idProfession = models.AutoField(primary_key=True)
    nomProfession = models.CharField(max_length=250)
    typeProfession = models.CharField(max_length=250)
    environnementTravail = models.CharField(max_length=250)
    travailleDehors = models.CharField(max_length=250)
    travailleSansEmploi = models.CharField(max_length=250)
    situationSansEmploi = models.CharField(max_length=250)
    revenu = models.CharField(max_length=250)
    freqRevenu = models.CharField(max_length=250)

class Residence(models.Model):
    idResidence = models.AutoField(primary_key=True)
    pays = models.CharField(max_length=250)
    ville = models.CharField(max_length=250)
    quartier = models.CharField(max_length=250)
    adresseComplete = models.CharField(max_length=255)
    groupe = models.CharField(max_length=100, null=True, blank=True, help_text="Groupe de résidence (Urban, Semi-urban, Europe, etc.)")

class Comportement(models.Model):
    idComportement = models.AutoField(primary_key=True)
    lieuRepas = models.CharField(max_length=250, null=True, blank=True)
    mangeAvecLesMains = models.CharField(max_length=250, null=True, blank=True)
    laveLesMainsAvantDeManger = models.CharField(max_length=250, null=True, blank=True)
    utiliseDuSavon = models.CharField(max_length=250, null=True, blank=True)
    laveLesMainsDesEnfants = models.CharField(max_length=250, null=True, blank=True)
    utiliseGelHydroalcoolique = models.CharField(max_length=250, null=True, blank=True)

class Logement(models.Model):
    idLogement = models.AutoField(primary_key=True)
    typeLogement = models.CharField(max_length=250)
    nombrePersonnesFoyer = models.IntegerField()
    nbMursMaisonCouverts = models.IntegerField()
    nbSolsMaisonCouverts = models.IntegerField()
    nbToilettesMaison = models.IntegerField()
    toilettesInterieures = models.BooleanField()

class Alimentation(models.Model):
    idAlimentation = models.AutoField(primary_key=True)
    typeRepas = models.CharField(max_length=250)

class Patient(models.Model):
    idPatient = models.AutoField(primary_key=True)
    id_code = models.CharField(max_length=250, unique=True, null=True, blank=True)
    sexe = models.BooleanField(null=True, blank=True)
    poids = models.FloatField(null=True, blank=True)
    taille = models.FloatField(null=True, blank=True)
    lieuNaissance = models.CharField(max_length=250, null=True, blank=True)
    niveauEtude = models.CharField(max_length=250, null=True, blank=True)
    profession = models.ForeignKey(Profession, on_delete=models.SET_NULL, null=True)
    comportement = models.ForeignKey(Comportement, on_delete=models.SET_NULL, null=True)
    logement = models.ForeignKey(Logement, on_delete=models.SET_NULL, null=True)
    alimentation = models.ForeignKey(Alimentation, on_delete=models.SET_NULL, null=True)
    residence = models.ForeignKey(Residence, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['idPatient']

# ===================== DOSSIER MÉDICAL =====================

class DossierMedical(models.Model):
    idDossier = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    dateCreation = models.DateField()
    commentaireGeneral = models.TextField()

class Analyse(models.Model):
    idAnalyse = models.AutoField(primary_key=True)
    dossier = models.ForeignKey(DossierMedical, on_delete=models.CASCADE)
    typeAnalyse = models.CharField(max_length=250)
    dateAnalyse = models.DateField()

class ResultatAnalyse(models.Model):
    idResultatAnalyse = models.AutoField(primary_key=True)
    analyse = models.OneToOneField(Analyse, on_delete=models.CASCADE)
    glycemie = models.FloatField()
    cholesterol = models.FloatField()
    triglyceride = models.FloatField()
    hdl = models.FloatField()
    ldl = models.FloatField()
    creatinine = models.FloatField()
    uree = models.FloatField()
    proteinurie = models.FloatField()

# ===================== SYSTÈME D'ALERTES DE CONFORMITÉ =====================

class TypeAlerteConformite(models.Model):
    """Types d'alertes de conformité RGPD/HIPAA/CDP"""
    TYPE_CHOICES = [
        # RGPD Alertes
        ('RGPD_CONSENTEMENT_EXPIRE', 'Consentement RGPD expiré'),
        ('RGPD_DROIT_ACCES', 'Demande de droit d\'accès'),
        ('RGPD_DROIT_RECTIFICATION', 'Demande de droit de rectification'),
        ('RGPD_DROIT_EFFACEMENT', 'Demande de droit d\'effacement'),
        ('RGPD_DROIT_PORTABILITE', 'Demande de droit à la portabilité'),
        ('RGPD_DROIT_OPPOSITION', 'Demande de droit d\'opposition'),
        ('RGPD_VIOLATION_DONNEES', 'Violation de données personnelles'),
        ('RGPD_TRANSFERT_INTERNATIONAL', 'Transfert international de données'),
        ('RGPD_DPO_NOTIFICATION', 'Notification DPO requise'),
        
        # HIPAA Alertes
        ('HIPAA_PHI_ACCES_NON_AUTORISE', 'Accès non autorisé aux PHI'),
        ('HIPAA_BREACH_NOTIFICATION', 'Notification de violation HIPAA'),
        ('HIPAA_BA_NOTIFICATION', 'Notification Business Associate'),
        ('HIPAA_AUDIT_TRAIL_MANQUANT', 'Audit trail manquant'),
        ('HIPAA_ENCRYPTION_MANQUANT', 'Chiffrement manquant'),
        ('HIPAA_ACCESS_CONTROL_VIOLATION', 'Violation de contrôle d\'accès'),
        ('HIPAA_RETENTION_POLICY_VIOLATION', 'Violation de politique de rétention'),
        
        # CDP Sénégal Alertes
        ('CDP_NOTIFICATION_VIOLATION', 'Notification CDP violation'),
        ('CDP_AUTORISATION_MANQUANT', 'Autorisation CDP manquante'),
        ('CDP_DROIT_PATIENT_VIOLATION', 'Violation des droits du patient'),
        ('CDP_SECRET_MEDICAL_VIOLATION', 'Violation du secret médical'),
        ('CDP_CONSENTEMENT_ECLAIRE', 'Consentement éclairé manquant'),
        
        # Alertes Générales
        ('ACCES_NON_AUTORISE', 'Accès non autorisé'),
        ('SUPPRESSION_ACCIDENTELLE', 'Suppression accidentelle'),
        ('MODIFICATION_NON_AUTORISEE', 'Modification non autorisée'),
        ('EXPORT_NON_AUTORISE', 'Export non autorisé'),
        ('CONSULTATION_EXCESSIVE', 'Consultation excessive'),
        ('SEUIL_MEDICAL_DEPASSE', 'Seuil médical dépassé'),
        ('BACKUP_MANQUANT', 'Sauvegarde manquante'),
        ('SECURITE_FAIBLE', 'Niveau de sécurité faible'),
    ]
    
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, choices=TYPE_CHOICES, unique=True)
    nom = models.CharField(max_length=200)
    description = models.TextField()
    norme_conformite = models.CharField(max_length=20, choices=[
        ('RGPD', 'RGPD'),
        ('HIPAA', 'HIPAA'),
        ('CDP', 'CDP Sénégal'),
        ('GENERAL', 'Général')
    ])
    niveau_critique = models.IntegerField(choices=[
        (1, 'Faible'),
        (2, 'Moyen'),
        (3, 'Élevé'),
        (4, 'Critique'),
        (5, 'Urgent')
    ], default=3)
    delai_notification = models.IntegerField(help_text="Délai en heures pour la notification", default=24)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Type d'alerte de conformité"
        verbose_name_plural = "Types d'alertes de conformité"
        ordering = ['norme_conformite', 'niveau_critique', 'nom']
    
    def __str__(self):
        return f"{self.get_norme_conformite_display()} - {self.nom}"

class AlerteConformite(models.Model):
    """Alertes de conformité RGPD/HIPAA/CDP"""
    STATUT_CHOICES = [
        ('NOUVELLE', 'Nouvelle'),
        ('EN_COURS', 'En cours de traitement'),
        ('RESOLUE', 'Résolue'),
        ('ESCALADEE', 'Escaladée'),
        ('FERMEE', 'Fermée'),
    ]
    
    id = models.AutoField(primary_key=True)
    type_alerte = models.ForeignKey(TypeAlerteConformite, on_delete=models.CASCADE)
    dossier = models.ForeignKey(DossierMedical, on_delete=models.CASCADE, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    utilisateur_origine = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='alertes_origine')
    utilisateur_traitement = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='alertes_traitement')
    
    titre = models.CharField(max_length=200)
    description = models.TextField()
    details_techniques = models.JSONField(default=dict, help_text="Détails techniques de l'alerte")
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    date_resolution = models.DateTimeField(null=True, blank=True)
    date_notification_cdp = models.DateTimeField(null=True, blank=True)
    
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='NOUVELLE')
    niveau_critique = models.IntegerField(choices=[
        (1, 'Faible'),
        (2, 'Moyen'),
        (3, 'Élevé'),
        (4, 'Critique'),
        (5, 'Urgent')
    ])
    
    notifie_cdp = models.BooleanField(default=False)
    notifie_dpo = models.BooleanField(default=False)
    notifie_admin = models.BooleanField(default=False)
    
    actions_prises = models.TextField(blank=True, null=True)
    commentaires = models.TextField(blank=True, null=True)
    
    # Données concernées par l'alerte
    donnees_concernees = models.JSONField(default=dict, help_text="Types de données concernées")
    impact_patients = models.IntegerField(default=0, help_text="Nombre de patients impactés")
    
    class Meta:
        verbose_name = "Alerte de conformité"
        verbose_name_plural = "Alertes de conformité"
        ordering = ['-date_creation', '-niveau_critique']
    
    def __str__(self):
        return f"{self.type_alerte.nom} - {self.titre} ({self.get_statut_display()})"
    
    def save(self, *args, **kwargs):
        # Mettre à jour la date de résolution si le statut change
        if self.pk:
            try:
                old_instance = AlerteConformite.objects.get(pk=self.pk)
                if old_instance.statut != 'RESOLUE' and self.statut == 'RESOLUE':
                    from django.utils import timezone
                    self.date_resolution = timezone.now()
            except AlerteConformite.DoesNotExist:
                pass
        super().save(*args, **kwargs)

class RegleAlerteConformite(models.Model):
    """Règles de déclenchement des alertes de conformité"""
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=200)
    description = models.TextField()
    
    type_alerte = models.ForeignKey(TypeAlerteConformite, on_delete=models.CASCADE)
    conditions = models.JSONField(default=dict, help_text="Conditions de déclenchement")
    
    # Paramètres de déclenchement
    seuil_min = models.IntegerField(null=True, blank=True)
    seuil_max = models.IntegerField(null=True, blank=True)
    periode_surveillance = models.IntegerField(default=24, help_text="Période en heures")
    
    # Actions automatiques
    action_automatique = models.CharField(max_length=50, choices=[
        ('NOTIFICATION', 'Notification automatique'),
        ('BLOQUER_ACCES', 'Bloquer l\'accès'),
        ('LOGGER', 'Enregistrer dans les logs'),
        ('ESCALADER', 'Escalader vers un supérieur'),
        ('FERMER_SESSION', 'Fermer la session'),
    ], default='NOTIFICATION')
    
    # Destinataires
    notifier_admin = models.BooleanField(default=True)
    notifier_dpo = models.BooleanField(default=False)
    notifier_cdp = models.BooleanField(default=False)
    notifier_medecin = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Règle d'alerte de conformité"
        verbose_name_plural = "Règles d'alertes de conformité"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.nom} - {self.type_alerte.nom}"

class NotificationConformite(models.Model):
    """Notifications envoyées pour les alertes de conformité"""
    TYPE_CHOICES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('NOTIFICATION_INTERNE', 'Notification interne'),
        ('WEBHOOK', 'Webhook'),
        ('API', 'API externe'),
    ]
    
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('ENVOYEE', 'Envoyée'),
        ('ECHEC', 'Échec'),
        ('LUE', 'Lue'),
    ]
    
    id = models.AutoField(primary_key=True)
    alerte = models.ForeignKey(AlerteConformite, on_delete=models.CASCADE)
    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, null=True, blank=True)
    
    type_notification = models.CharField(max_length=20, choices=TYPE_CHOICES)
    destinataire_email = models.EmailField(blank=True, null=True)
    destinataire_telephone = models.CharField(max_length=20, blank=True, null=True)
    
    sujet = models.CharField(max_length=200)
    contenu = models.TextField()
    contenu_html = models.TextField(blank=True, null=True)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_envoi = models.DateTimeField(null=True, blank=True)
    date_lecture = models.DateTimeField(null=True, blank=True)
    
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    tentatives = models.IntegerField(default=0)
    erreur = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Notification de conformité"
        verbose_name_plural = "Notifications de conformité"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Notification {self.type_notification} - {self.sujet}"

class AuditConformite(models.Model):
    """Audit trail pour la conformité"""
    TYPE_ACTION_CHOICES = [
        ('LECTURE', 'Lecture'),
        ('MODIFICATION', 'Modification'),
        ('SUPPRESSION', 'Suppression'),
        ('CREATION', 'Création'),
        ('EXPORT', 'Export'),
        ('IMPORT', 'Import'),
        ('ACCES', 'Accès'),
        ('CONNEXION', 'Connexion'),
        ('DECONNEXION', 'Déconnexion'),
        ('CHANGEMENT_PASSWORD', 'Changement de mot de passe'),
        ('MODIFICATION_PROFIL', 'Modification de profil'),
    ]
    
    id = models.AutoField(primary_key=True)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    type_action = models.CharField(max_length=20, choices=TYPE_ACTION_CHOICES)
    objet = models.CharField(max_length=100, help_text="Type d'objet concerné (Patient, Dossier, etc.)")
    objet_id = models.IntegerField(null=True, blank=True)
    
    details = models.JSONField(default=dict, help_text="Détails de l'action")
    donnees_avant = models.JSONField(default=dict, blank=True, null=True)
    donnees_apres = models.JSONField(default=dict, blank=True, null=True)
    
    date_action = models.DateTimeField(auto_now_add=True)
    duree_action = models.FloatField(null=True, blank=True, help_text="Durée en secondes")
    
    # Conformité
    conforme_rgpd = models.BooleanField(default=True)
    conforme_hipaa = models.BooleanField(default=True)
    conforme_cdp = models.BooleanField(default=True)
    
    alerte_generee = models.ForeignKey(AlerteConformite, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = "Audit de conformité"
        verbose_name_plural = "Audits de conformité"
        ordering = ['-date_action']
        indexes = [
            models.Index(fields=['utilisateur', 'date_action']),
            models.Index(fields=['type_action', 'date_action']),
            models.Index(fields=['objet', 'objet_id']),
        ]
    
    def __str__(self):
        return f"{self.utilisateur} - {self.type_action} - {self.objet} - {self.date_action}"

# Mise à jour du modèle Alerte existant pour compatibilité
class Alerte(models.Model):
    idAlerte = models.AutoField(primary_key=True)
    dossier = models.ForeignKey(DossierMedical, on_delete=models.CASCADE, null=True, blank=True)
    typeAlerte = models.CharField(max_length=250)
    message = models.TextField()
    dateAlerte = models.DateField()
    gravite = models.CharField(max_length=50, default='info')  # info, warning, critique
    notifie_cdp = models.BooleanField(default=False)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    donnees_concernees = models.TextField(blank=True, null=True)
    
    # Nouveaux champs pour compatibilité avec le nouveau système
    alerte_conformite = models.ForeignKey(AlerteConformite, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-dateAlerte', '-idAlerte']

class Vaccin(models.Model):
    idVaccin = models.AutoField(primary_key=True)
    dossier = models.ForeignKey(DossierMedical, on_delete=models.CASCADE)
    nomVaccin = models.CharField(max_length=250, null=True, blank=True)
    typeVaccination = models.CharField(max_length=250, null=True, blank=True)
    dose = models.IntegerField(null=True, blank=True)

class Infection(models.Model):
    idInfection = models.AutoField(primary_key=True)
    dossier = models.ForeignKey(DossierMedical, on_delete=models.CASCADE)
    nomInfection = models.CharField(max_length=250, null=True, blank=True)
    typeInfection = models.CharField(max_length=250, null=True, blank=True)

# ===================== CONFORMITÉ & RAPPORTS =====================

class RegleConformite(models.Model):
    idRegle = models.AutoField(primary_key=True)
    nomRegle = models.CharField(max_length=250)
    description = models.TextField()
    typeRegle = models.CharField(max_length=250)
    niveauCritique = models.IntegerField()
    is_active = models.BooleanField(default=True)

class Acces(models.Model): 
    typeAcces = models.CharField(max_length=250)
    dateAcces = models.DateTimeField(auto_now_add=True)
    regle = models.ForeignKey(RegleConformite, on_delete=models.CASCADE, null=True, blank=True)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    donnees_concernees = models.TextField(blank=True, null=True)

class ParametreConformite(models.Model):
    idParametre = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=250)
    seuilMin = models.IntegerField()
    seuilMax = models.IntegerField()
    unite = models.CharField(max_length=50)
    regle = models.ForeignKey('RegleConformite', on_delete=models.CASCADE, related_name='parametres', null=True, blank=True)

class Rapport(models.Model):
    idRapport = models.AutoField(primary_key=True)
    dateRapport = models.DateField()
    titre = models.CharField(max_length=250)
    contenu = models.TextField()
    statutConformite = models.CharField(max_length=250)
    niveauConformite = models.IntegerField()

# ===================== DEMANDES D'EXPORTATION =====================

class DemandeExportation(models.Model):
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('APPROUVEE', 'Approuvée'),
        ('REFUSEE', 'Refusée'),
    ]
    
    id = models.AutoField(primary_key=True)
    demandeur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='demandes_exportation')
    medecin = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='demandes_a_traiter', limit_choices_to={'role': 'MEDECIN'})
    date_demande = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    commentaire_medecin = models.TextField(blank=True, null=True)
    donnees_autorisees = models.JSONField(default=dict, help_text="Types de données autorisées pour l'export")
    utilisee = models.BooleanField(default=False, help_text="Indique si la demande approuvée a déjà été utilisée pour exporter")
    
    class Meta:
        verbose_name = "Demande d'exportation"
        verbose_name_plural = "Demandes d'exportation"
        ordering = ['-date_demande']

    def __str__(self):
        return f"Demande de {self.demandeur.username if self.demandeur else 'Unknown'} - {self.statut}"
    
    def save(self, *args, **kwargs):
        # Si le statut change vers APPROUVEE ou REFUSEE, mettre à jour date_traitement
        if self.pk:
            try:
                old_instance = DemandeExportation.objects.get(pk=self.pk)
                if old_instance.statut == 'EN_ATTENTE' and self.statut in ['APPROUVEE', 'REFUSEE']:
                    self.date_traitement = timezone.now()
            except DemandeExportation.DoesNotExist:
                pass
        super().save(*args, **kwargs)

   
    #def __str__(self):
      #  return self.id_code

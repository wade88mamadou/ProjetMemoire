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

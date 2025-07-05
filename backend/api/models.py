from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, AbstractUser

# Profession
class Profession(models.Model):
    nomProfession = models.CharField(max_length=255)
    typeProfession = models.CharField(max_length=255, blank=True, null=True)
    environnementTravail = models.CharField(max_length=255, blank=True, null=True)
    travailleChezSoi = models.CharField(max_length=10, blank=True, null=True)
    travailleDansEmploi = models.CharField(max_length=10, blank=True, null=True)
    revenu = models.FloatField(blank=True, null=True)
    freqRevenu = models.CharField(max_length=255, blank=True, null=True)

# Logement
class Logement(models.Model):
    typeLogement = models.CharField(max_length=255)
    nombrePersonnesFoyer = models.IntegerField()
    multiMaisonsCouverts = models.CharField(max_length=10, blank=True, null=True)
    sousMaisonCouverts = models.CharField(max_length=10, blank=True, null=True)
    toilettesInterieures = models.CharField(max_length=10, blank=True, null=True)

# Résidence
class Residence(models.Model):
    pays = models.CharField(max_length=255)
    ville = models.CharField(max_length=255)
    quartier = models.CharField(max_length=255)
    adresseComplete = models.CharField(max_length=500)

# Comportement
class Comportement(models.Model):
    viePrivee = models.CharField(max_length=255, blank=True, null=True)
    mangeAilleursMain = models.CharField(max_length=255, blank=True, null=True)
    vieAvecAussiEnfantDeManger = models.CharField(max_length=255, blank=True, null=True)
    utiliseSalon = models.CharField(max_length=255, blank=True, null=True)
    laveLesMainsEnfants = models.CharField(max_length=255, blank=True, null=True)
    utiliseSallyHydroalcoolique = models.CharField(max_length=255, blank=True, null=True)

# Patient
class Patient(models.Model):
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    dateNaissance = models.DateField()
    sexe = models.CharField(max_length=10)
    poids = models.FloatField(blank=True, null=True)
    taille = models.FloatField(blank=True, null=True)
    lieuNaissance = models.CharField(max_length=255, blank=True, null=True)
    nationalite = models.CharField(max_length=255, blank=True, null=True)
    niveauEtude = models.CharField(max_length=255, blank=True, null=True)
    etablissement = models.CharField(max_length=255, blank=True, null=True)
    profession = models.ForeignKey(Profession, on_delete=models.SET_NULL, null=True, blank=True)
    logement = models.OneToOneField(Logement, on_delete=models.SET_NULL, null=True, blank=True)
    residence = models.OneToOneField(Residence, on_delete=models.SET_NULL, null=True, blank=True)
    comportement = models.OneToOneField(Comportement, on_delete=models.SET_NULL, null=True, blank=True)

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
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == 'ADMIN' or self.is_superuser
    
    @property
    def is_medecin(self):
        return self.role == 'MEDECIN'
    
    @property
    def is_user_simple(self):
        return self.role == 'user_simple'

# Dossier Médical
class DossierMedical(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    nomDossier = models.CharField(max_length=255)
    dateCreation = models.DateField(auto_now_add=True)
    commentaireGeneral = models.TextField(blank=True, null=True)
    statut = models.CharField(max_length=50, default='Actif')

# Rapport
class Rapport(models.Model):
    dossier = models.ForeignKey(DossierMedical, on_delete=models.CASCADE)
    dateRapport = models.DateField(auto_now_add=True)
    titre = models.CharField(max_length=255)
    statut = models.CharField(max_length=50, default='Brouillon')
    contenu = models.TextField(blank=True, null=True)
    statutConformite = models.CharField(max_length=50, default='Non évalué')
    niveauConformite = models.IntegerField(blank=True, null=True)

# Vaccin
class Vaccin(models.Model):
    nomVaccin = models.CharField(max_length=255)
    typeVaccin = models.CharField(max_length=255)
    dateVaccination = models.DateField()
    dose = models.CharField(max_length=255)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

# Infection
class Infection(models.Model):
    nomInfection = models.CharField(max_length=255)
    typeInfection = models.CharField(max_length=255)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

# Règle de conformité
class RegleConformite(models.Model):
    nomRegle = models.CharField(max_length=255)
    description = models.TextField()
    typeRegle = models.CharField(max_length=255)
    niveauCritique = models.CharField(max_length=50)

# Paramètre de conformité
class ParametreConformite(models.Model):
    nom = models.CharField(max_length=255)
    seuilMin = models.FloatField()
    seuilMax = models.FloatField()
    unite = models.CharField(max_length=50)
    regle = models.ForeignKey(RegleConformite, on_delete=models.SET_NULL, null=True, blank=True)

# Alerte
class Alerte(models.Model):
    typeAlerte = models.CharField(max_length=255)
    message = models.TextField()
    dateAlerte = models.DateField()
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

# Analyse
class Analyse(models.Model):
    typeAnalyse = models.CharField(max_length=255)
    dateAnalyse = models.DateField()
    dossier = models.ForeignKey(DossierMedical, on_delete=models.CASCADE)

# Résultat analyse
class ResultatAnalyse(models.Model):
    analyse = models.ForeignKey(Analyse, on_delete=models.CASCADE)
    dateAnalyse = models.DateField()
    glycemie = models.FloatField(blank=True, null=True)
    hemoglobine = models.FloatField(blank=True, null=True)
    leucocytes = models.FloatField(blank=True, null=True)
    lymphocytes = models.FloatField(blank=True, null=True)
    neutrophiles = models.FloatField(blank=True, null=True)

# Alimentation
class Alimentation(models.Model):
    typeRepas = models.CharField(max_length=255)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

# Accès
class Acces(models.Model):
    typeAcces = models.CharField(max_length=255)
    dateAcces = models.DateField()
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    rapport = models.ForeignKey(Rapport, on_delete=models.CASCADE, null=True, blank=True)

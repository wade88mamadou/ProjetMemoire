import logging
logger = logging.getLogger(__name__)

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from .validators import validate_password_strength, validate_username, validate_email, sanitize_input
from django.core.mail import send_mail

from .models import (
    Utilisateur, Patient, Profession, Logement, Residence, Comportement,
    DossierMedical, Rapport, Vaccin, Infection, RegleConformite,
    ParametreConformite, Alerte, Analyse, ResultatAnalyse, Alimentation, Acces,
    DemandeExportation, TypeAlerteConformite, AlerteConformite, RegleAlerteConformite, NotificationConformite, AuditConformite
)

#classe serializer
class ImportSerializer(serializers.Serializer):
    file = serializers.FileField()

# Serializers d'authentification
class UserSerializer(serializers.ModelSerializer):
    """Serializer pour les détails de l'utilisateur"""
    medecin = serializers.PrimaryKeyRelatedField(queryset=Utilisateur.objects.filter(role='MEDECIN'), required=False, allow_null=True)
    class Meta:
        model = Utilisateur
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_superuser', 'specialite', 'statut', 'is_active', 'medecin']
        read_only_fields = ['id', 'is_staff', 'is_superuser']

class LoginSerializer(serializers.Serializer):
    """Serializer pour la connexion"""
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    
    def validate_username(self, value):
        """Valide le nom d'utilisateur"""
        # Temporairement, on ne fait que nettoyer les espaces
        return value.strip() if value else value
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Nom d\'utilisateur ou mot de passe incorrect.')
            if not user.is_active:
                raise serializers.ValidationError({
                    'error': 'Compte désactivé',
                    'message': 'Votre compte a été désactivé par l\'administrateur. Veuillez contacter votre administrateur pour réactiver votre compte.',
                    'code': 'ACCOUNT_DISABLED'
                })
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Nom d\'utilisateur et mot de passe requis.')

class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'utilisateur (admin seulement)"""
    password = serializers.CharField(
        write_only=True, 
        min_length=8,  # Réduit de 12 à 8 pour le développement
    )
    password_confirm = serializers.CharField(write_only=True)
    medecin = serializers.PrimaryKeyRelatedField(queryset=Utilisateur.objects.filter(role='MEDECIN'), required=False, allow_null=True)
    
    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'role', 'specialite', 'medecin']
    
    def validate_username(self, value):
        """Valide le nom d'utilisateur"""
        # Validation simplifiée pour le développement
        if len(value) < 3:
            raise serializers.ValidationError("Le nom d'utilisateur doit contenir au moins 3 caractères.")
        return value.strip()
    
    def validate_email(self, value):
        """Valide l'email"""
        # Validation simplifiée
        if '@' not in value or '.' not in value:
            raise serializers.ValidationError("Veuillez entrer une adresse email valide.")
        return value.lower().strip()
    
    def validate_first_name(self, value):
        """Valide le prénom"""
        return value.strip() if value else value
    
    def validate_last_name(self, value):
        """Valide le nom"""
        return value.strip() if value else value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        
        # Vérifier que l'email n'est pas déjà utilisé
        if Utilisateur.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        
        # Vérifier que le username n'est pas déjà utilisé
        if Utilisateur.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = Utilisateur(**validated_data)
        user.set_password(password)
        user.must_change_password = True  # Forcer le changement à la première connexion
        user.save()
        
        # Log de la création
        logger.info(f"Utilisateur créé par {self.context['request'].user.username}: {user.username}")

        # Envoi de l'email avec les identifiants (username comme identifiant)
        try:
            reset_url = 'https://conformed.sn/reset-password'  # À adapter selon votre front
            send_mail(
                subject='Création de votre compte sur Conformed',
                message=f'Bonjour {user.first_name},\n\nVotre compte a été créé.\nNom d’utilisateur (identifiant) : {user.username}\nMot de passe temporaire : {password}\n\nVeuillez vous connecter ici : https://conformed.sn/login\n\nPour des raisons de sécurité, vous devrez changer votre mot de passe à la première connexion.\nVous pouvez le faire directement ici : {reset_url}',
                from_email=None,  # Utilise DEFAULT_FROM_EMAIL
                recipient_list=[user.email],
                fail_silently=False,
            )
            logger.info(f"Email d'inscription envoyé à {user.email}")
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email à {user.email}: {e}")
        
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour d'utilisateur (admin seulement)"""
    password = serializers.CharField(
        write_only=True, 
        required=False, 
        min_length=8,  # Réduit de 12 à 8 pour le développement
    )
    password_confirm = serializers.CharField(write_only=True, required=False)
    medecin = serializers.PrimaryKeyRelatedField(queryset=Utilisateur.objects.filter(role='MEDECIN'), required=False, allow_null=True)
    
    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'role', 'specialite', 'is_active', 'medecin']
    
    def validate_username(self, value):
        """Valide le nom d'utilisateur"""
        # Validation simplifiée pour le développement
        if len(value) < 3:
            raise serializers.ValidationError("Le nom d'utilisateur doit contenir au moins 3 caractères.")
        return value.strip()
    
    def validate_email(self, value):
        """Valide l'email"""
        # Validation simplifiée
        if '@' not in value or '.' not in value:
            raise serializers.ValidationError("Veuillez entrer une adresse email valide.")
        return value.lower().strip()
    
    def validate_first_name(self, value):
        """Valide le prénom"""
        return value.strip() if value else value
    
    def validate_last_name(self, value):
        """Valide le nom"""
        return value.strip() if value else value
    
    def validate(self, attrs):
        if 'password' in attrs and 'password_confirm' in attrs:
            if attrs['password'] != attrs['password_confirm']:
                raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        
        return attrs
    
    def update(self, instance, validated_data):
        logger.info(f"Données reçues pour mise à jour: {validated_data}")
        
        if 'password_confirm' in validated_data:
            validated_data.pop('password_confirm')
        
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        
        for attr, value in validated_data.items():
            logger.info(f"Mise à jour {attr}: {value}")
            setattr(instance, attr, value)
        
        instance.save()
        logger.info(f"Utilisateur sauvegardé. is_active: {instance.is_active}")
        return instance

# Serializers pour les autres modèles
class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = '__all__'

class LogementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logement
        fields = '__all__'

class ResidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Residence
        fields = '__all__'

class ComportementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comportement
        fields = '__all__'

# Suppression du doublon - le UserSerializer en haut du fichier est suffisant

class ResultatAnalyseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultatAnalyse
        fields = '__all__'

class AnalyseWithResultatSerializer(serializers.ModelSerializer):
    resultat_analyse = ResultatAnalyseSerializer(source='resultatanalyse', read_only=True)
    class Meta:
        model = Analyse
        fields = '__all__'
        depth = 0

class DossierMedicalSerializer(serializers.ModelSerializer):
    analyses = serializers.SerializerMethodField()
    class Meta:
        model = DossierMedical
        fields = '__all__'
    def get_analyses(self, obj):
        analyses = Analyse.objects.filter(dossier=obj)
        return AnalyseWithResultatSerializer(analyses, many=True).data

class RapportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rapport
        fields = '__all__'

class VaccinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaccin
        fields = '__all__'

class InfectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Infection
        fields = '__all__'

class RegleConformiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegleConformite
        fields = '__all__'

class ParametreConformiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParametreConformite
        fields = '__all__'

class AlerteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alerte
        fields = '__all__'

class AnalyseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analyse
        fields = '__all__'

class AlimentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alimentation
        fields = '__all__'

class AccesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acces
        fields = '__all__'

# ===================== SERIALIZERS DEMANDES D'EXPORTATION =====================

class DemandeExportationSerializer(serializers.ModelSerializer):
    demandeur_nom = serializers.CharField(source='demandeur.username', read_only=True)
    medecin_nom = serializers.CharField(source='medecin.username', read_only=True)
    
    class Meta:
        model = DemandeExportation
        fields = [
            'id', 'demandeur', 'demandeur_nom', 'medecin', 'medecin_nom',
            'date_demande', 'date_traitement', 'statut', 'commentaire_medecin',
            'donnees_autorisees'
        ]
        read_only_fields = ['id', 'date_demande', 'date_traitement']

class DemandeExportationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeExportation
        fields = ['medecin', 'donnees_autorisees']
    
    def validate(self, attrs):
        user = self.context['request'].user
        
        # Vérifier qu'il n'y a pas déjà une demande en attente
        if DemandeExportation.objects.filter(
            demandeur=user, 
            statut='EN_ATTENTE'
        ).exists():
            raise serializers.ValidationError(
                "Vous avez déjà une demande d'exportation en attente."
            )
        
        # Vérifier que le médecin existe et est bien un médecin
        medecin = attrs.get('medecin')
        if not medecin or medecin.role != 'MEDECIN':
            raise serializers.ValidationError(
                "Veuillez sélectionner un médecin valide."
            )
        
        return attrs
    
    def create(self, validated_data):
        validated_data['demandeur'] = self.context['request'].user
        return super().create(validated_data)

class DemandeExportationTraitementSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeExportation
        fields = ['statut', 'commentaire_medecin', 'donnees_autorisees']
    
    def validate_statut(self, value):
        if value not in ['APPROUVEE', 'REFUSEE']:
            raise serializers.ValidationError(
                "Le statut doit être 'APPROUVEE' ou 'REFUSEE'."
            )
        return value 

# Supprimer les serializers de réinitialisation par email
# Garder seulement les serializers de base 

class ForgotPasswordVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')
        user_qs = Utilisateur.objects.filter(email=email, username=username)
        if not user_qs.exists():
            raise serializers.ValidationError('Identifiants invalides.')
        data['user'] = user_qs.first()
        return data

class ForgotPasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError('Les mots de passe ne correspondent pas.')
        # Vérification du token (sera fait dans la vue)
        return data 

# ===================== SÉRIALISEURS ALERTES DE CONFORMITÉ =====================

class TypeAlerteConformiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeAlerteConformite
        fields = '__all__'

class AlerteConformiteSerializer(serializers.ModelSerializer):
    type_alerte = TypeAlerteConformiteSerializer(read_only=True)
    type_alerte_id = serializers.PrimaryKeyRelatedField(
        queryset=TypeAlerteConformite.objects.all(),
        source='type_alerte',
        write_only=True
    )
    utilisateur_origine = UserSerializer(read_only=True)
    utilisateur_traitement = UserSerializer(read_only=True)
    dossier = DossierMedicalSerializer(read_only=True)
    patient = PatientSerializer(read_only=True)
    
    class Meta:
        model = AlerteConformite
        fields = '__all__'
        read_only_fields = ['date_creation', 'date_modification', 'date_resolution']

class RegleAlerteConformiteSerializer(serializers.ModelSerializer):
    type_alerte = TypeAlerteConformiteSerializer(read_only=True)
    type_alerte_id = serializers.PrimaryKeyRelatedField(
        queryset=TypeAlerteConformite.objects.all(),
        source='type_alerte',
        write_only=True
    )
    
    class Meta:
        model = RegleAlerteConformite
        fields = '__all__'
        read_only_fields = ['date_creation', 'date_modification']

class NotificationConformiteSerializer(serializers.ModelSerializer):
    alerte = AlerteConformiteSerializer(read_only=True)
    destinataire = UserSerializer(read_only=True)
    
    class Meta:
        model = NotificationConformite
        fields = '__all__'
        read_only_fields = ['date_creation', 'date_envoi', 'date_lecture']

class AuditConformiteSerializer(serializers.ModelSerializer):
    utilisateur = UserSerializer(read_only=True)
    alerte_generee = AlerteConformiteSerializer(read_only=True)
    
    class Meta:
        model = AuditConformite
        fields = '__all__'
        read_only_fields = ['date_action']

# Sérialiseurs pour les statistiques de conformité
class StatistiquesConformiteSerializer(serializers.Serializer):
    total_alertes = serializers.IntegerField()
    alertes_nouvelles = serializers.IntegerField()
    alertes_en_cours = serializers.IntegerField()
    alertes_resolues = serializers.IntegerField()
    alertes_critiques = serializers.IntegerField()
    alertes_urgentes = serializers.IntegerField()
    
    # Par norme de conformité
    alertes_rgpd = serializers.IntegerField()
    alertes_hipaa = serializers.IntegerField()
    alertes_cdp = serializers.IntegerField()
    
    # Par niveau de criticité
    niveau_faible = serializers.IntegerField()
    niveau_moyen = serializers.IntegerField()
    niveau_eleve = serializers.IntegerField()
    niveau_critique = serializers.IntegerField()
    niveau_urgent = serializers.IntegerField()
    
    # Tendances
    alertes_7_jours = serializers.IntegerField()
    alertes_30_jours = serializers.IntegerField()
    temps_moyen_resolution = serializers.FloatField()
    
    # Conformité
    taux_conformite_rgpd = serializers.FloatField()
    taux_conformite_hipaa = serializers.FloatField()
    taux_conformite_cdp = serializers.FloatField()

# Sérialiseur pour la configuration des alertes
class ConfigurationAlertesSerializer(serializers.Serializer):
    # Paramètres généraux
    activation_surveillance = serializers.BooleanField(default=True)
    delai_notification_defaut = serializers.IntegerField(default=24)
    escalation_automatique = serializers.BooleanField(default=True)
    
    # Seuils de déclenchement
    seuil_acces_non_autorise = serializers.IntegerField(default=3)
    seuil_consultation_excessive = serializers.IntegerField(default=50)
    seuil_modification_non_autorisee = serializers.IntegerField(default=2)
    
    # Notifications
    notifier_admin_par_defaut = serializers.BooleanField(default=True)
    notifier_dpo_par_defaut = serializers.BooleanField(default=False)
    notifier_cdp_par_defaut = serializers.BooleanField(default=False)
    
    # Actions automatiques
    bloquer_acces_automatique = serializers.BooleanField(default=False)
    fermer_session_automatique = serializers.BooleanField(default=False)
    logger_toutes_actions = serializers.BooleanField(default=True) 
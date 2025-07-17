from rest_framework import serializers
from django.contrib.auth import authenticate

from .models import (
    Utilisateur, Patient, Profession, Logement, Residence, Comportement,
    DossierMedical, Rapport, Vaccin, Infection, RegleConformite,
    ParametreConformite, Alerte, Analyse, ResultatAnalyse, Alimentation, Acces,
    DemandeExportation
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
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    medecin = serializers.PrimaryKeyRelatedField(queryset=Utilisateur.objects.filter(role='MEDECIN'), required=False, allow_null=True)
    
    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'role', 'specialite', 'medecin']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        
        # Empêcher la création d'admins via cette interface
        if attrs.get('role') == 'ADMIN':
            raise serializers.ValidationError("La création d'administrateurs n'est pas autorisée via cette interface.")
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = Utilisateur(**validated_data)
        user.set_password(password)  # <-- C'est cette ligne qui hash le mot de passe !
        user.save()
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour d'utilisateur (admin seulement)"""
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=False)
    medecin = serializers.PrimaryKeyRelatedField(queryset=Utilisateur.objects.filter(role='MEDECIN'), required=False, allow_null=True)
    
    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'role', 'specialite', 'is_active', 'medecin']
    
    def validate(self, attrs):
        if 'password' in attrs and 'password_confirm' in attrs:
            if attrs['password'] != attrs['password_confirm']:
                raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        
        # Empêcher la modification vers le rôle admin via cette interface
        if attrs.get('role') == 'ADMIN':
            raise serializers.ValidationError("La modification vers le rôle administrateur n'est pas autorisée via cette interface.")
        
        return attrs
    
    def update(self, instance, validated_data):
        print(f"Données reçues pour mise à jour: {validated_data}")  # Debug
        
        # Empêcher un admin de se désactiver lui-même
        if 'is_active' in validated_data and not validated_data['is_active']:
            if instance.role == 'ADMIN':
                raise serializers.ValidationError("Un administrateur ne peut pas se désactiver lui-même.")
        
        if 'password_confirm' in validated_data:
            validated_data.pop('password_confirm')
        
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        
        for attr, value in validated_data.items():
            print(f"Mise à jour {attr}: {value}")  # Debug
            setattr(instance, attr, value)
        
        instance.save()
        print(f"Utilisateur sauvegardé. is_active: {instance.is_active}")  # Debug
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
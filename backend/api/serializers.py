from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import (
    Utilisateur, Patient, Profession, Logement, Residence, Comportement,
    DossierMedical, Rapport, Vaccin, Infection, RegleConformite,
    ParametreConformite, Alerte, Analyse, ResultatAnalyse, Alimentation, Acces
)

# Serializers d'authentification
class UserSerializer(serializers.ModelSerializer):
    """Serializer pour les détails de l'utilisateur"""
    class Meta:
        model = Utilisateur
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_superuser', 'specialite', 'statut']
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
                raise serializers.ValidationError('Ce compte utilisateur est désactivé.')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Nom d\'utilisateur et mot de passe requis.')

class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'utilisateur (admin seulement)"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'role', 'specialite']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = Utilisateur(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour d'utilisateur (admin seulement)"""
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'role', 'specialite', 'is_active']
    
    def validate(self, attrs):
        if 'password' in attrs and 'password_confirm' in attrs:
            if attrs['password'] != attrs['password_confirm']:
                raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs
    
    def update(self, instance, validated_data):
        if 'password_confirm' in validated_data:
            validated_data.pop('password_confirm')
        
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
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

class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = '__all__'

class DossierMedicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierMedical
        fields = '__all__'

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

class ResultatAnalyseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultatAnalyse
        fields = '__all__'

class AlimentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alimentation
        fields = '__all__'

class AccesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acces
        fields = '__all__' 
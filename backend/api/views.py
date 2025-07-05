from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import (
    Patient, Profession, Logement, Residence, Comportement, Utilisateur,
    DossierMedical, Rapport, Vaccin, Infection, RegleConformite,
    ParametreConformite, Alerte, Analyse, ResultatAnalyse, Alimentation, Acces
)
from .serializers import (
    PatientSerializer, ProfessionSerializer, LogementSerializer, ResidenceSerializer, ComportementSerializer, UtilisateurSerializer,
    DossierMedicalSerializer, RapportSerializer, VaccinSerializer, InfectionSerializer, RegleConformiteSerializer,
    ParametreConformiteSerializer, AlerteSerializer, AnalyseSerializer, ResultatAnalyseSerializer, AlimentationSerializer, AccesSerializer,
    UserSerializer, LoginSerializer, UserCreateSerializer, UserUpdateSerializer
)


# Create your views here.

@api_view(['GET'])
def test_connexion(request):
    return Response({"message": "Connexion OK entre Django et React !"})

def accueil(request):
    return HttpResponse("Bienvenue sur l'API du Dashboard !")

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

class ProfessionViewSet(viewsets.ModelViewSet):
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer

class LogementViewSet(viewsets.ModelViewSet):
    queryset = Logement.objects.all()
    serializer_class = LogementSerializer

class ResidenceViewSet(viewsets.ModelViewSet):
    queryset = Residence.objects.all()
    serializer_class = ResidenceSerializer

class ComportementViewSet(viewsets.ModelViewSet):
    queryset = Comportement.objects.all()
    serializer_class = ComportementSerializer

class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurSerializer

class DossierMedicalViewSet(viewsets.ModelViewSet):
    queryset = DossierMedical.objects.all()
    serializer_class = DossierMedicalSerializer

class RapportViewSet(viewsets.ModelViewSet):
    queryset = Rapport.objects.all()
    serializer_class = RapportSerializer

class VaccinViewSet(viewsets.ModelViewSet):
    queryset = Vaccin.objects.all()
    serializer_class = VaccinSerializer

class InfectionViewSet(viewsets.ModelViewSet):
    queryset = Infection.objects.all()
    serializer_class = InfectionSerializer

class RegleConformiteViewSet(viewsets.ModelViewSet):
    queryset = RegleConformite.objects.all()
    serializer_class = RegleConformiteSerializer

class ParametreConformiteViewSet(viewsets.ModelViewSet):
    queryset = ParametreConformite.objects.all()
    serializer_class = ParametreConformiteSerializer

class AlerteViewSet(viewsets.ModelViewSet):
    queryset = Alerte.objects.all()
    serializer_class = AlerteSerializer

class AnalyseViewSet(viewsets.ModelViewSet):
    queryset = Analyse.objects.all()
    serializer_class = AnalyseSerializer

class ResultatAnalyseViewSet(viewsets.ModelViewSet):
    queryset = ResultatAnalyse.objects.all()
    serializer_class = ResultatAnalyseSerializer

class AlimentationViewSet(viewsets.ModelViewSet):
    queryset = Alimentation.objects.all()
    serializer_class = AlimentationSerializer

class AccesViewSet(viewsets.ModelViewSet):
    queryset = Acces.objects.all()
    serializer_class = AccesSerializer

class LoginView(APIView):
    """Vue pour la connexion utilisateur"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': 'Connexion réussie',
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """Vue pour la déconnexion utilisateur"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({
                'success': True,
                'message': 'Déconnexion réussie'
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Erreur lors de la déconnexion'
            }, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    """Vue pour récupérer les détails de l'utilisateur connecté"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UserAdminViewSet(generics.ListCreateAPIView):
    """Vue pour la gestion des utilisateurs (admin seulement)"""
    queryset = Utilisateur.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserCreateSerializer
    
    def get_queryset(self):
        return Utilisateur.objects.all().order_by('-date_joined')

class UserAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour la gestion détaillée d'un utilisateur (admin seulement)"""
    queryset = Utilisateur.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserUpdateSerializer

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """Vue pour changer le mot de passe"""
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    new_password_confirm = request.data.get('new_password_confirm')
    
    if not user.check_password(old_password):
        return Response({
            'error': 'Ancien mot de passe incorrect'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if new_password != new_password_confirm:
        return Response({
            'error': 'Les nouveaux mots de passe ne correspondent pas'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if len(new_password) < 8:
        return Response({
            'error': 'Le nouveau mot de passe doit contenir au moins 8 caractères'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(new_password)
    user.save()
    
    return Response({
        'success': True,
        'message': 'Mot de passe modifié avec succès'
    })

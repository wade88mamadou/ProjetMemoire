"""
Vues pour la gestion des alertes de conformité RGPD/HIPAA/CDP
"""

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta

from .models import (
    TypeAlerteConformite, AlerteConformite, RegleAlerteConformite,
    NotificationConformite, AuditConformite
)
from .serializers import (
    TypeAlerteConformiteSerializer, AlerteConformiteSerializer,
    RegleAlerteConformiteSerializer, NotificationConformiteSerializer,
    AuditConformiteSerializer, StatistiquesConformiteSerializer,
    ConfigurationAlertesSerializer
)
from .services_conformite import ServiceAlertesConformite

# ===================== VIEWSETS =====================

class TypeAlerteConformiteViewSet(viewsets.ModelViewSet):
    """ViewSet pour les types d'alertes de conformité"""
    queryset = TypeAlerteConformite.objects.all()
    serializer_class = TypeAlerteConformiteSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        return TypeAlerteConformite.objects.filter(is_active=True)

class AlerteConformiteViewSet(viewsets.ModelViewSet):
    """ViewSet pour les alertes de conformité"""
    serializer_class = AlerteConformiteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'ADMIN':
            # Admin voit toutes les alertes
            return AlerteConformite.objects.select_related(
                'type_alerte', 'utilisateur_origine', 'utilisateur_traitement',
                'dossier', 'patient'
            ).all()
        elif user.role == 'MEDECIN':
            # Médecin voit les alertes de ses patients
            return AlerteConformite.objects.filter(
                Q(patient__medecin=user) | Q(dossier__patient__medecin=user)
            ).select_related(
                'type_alerte', 'utilisateur_origine', 'utilisateur_traitement',
                'dossier', 'patient'
            )
        else:
            # User simple voit ses propres alertes
            return AlerteConformite.objects.filter(
                utilisateur_origine=user
            ).select_related(
                'type_alerte', 'utilisateur_origine', 'utilisateur_traitement',
                'dossier', 'patient'
            )
    
    @action(detail=True, methods=['post'])
    def resoudre(self, request, pk=None):
        """Marquer une alerte comme résolue"""
        alerte = self.get_object()
        alerte.statut = 'RESOLUE'
        alerte.utilisateur_traitement = request.user
        alerte.actions_prises = request.data.get('actions_prises', '')
        alerte.commentaires = request.data.get('commentaires', '')
        alerte.save()
        
        return Response({
            'message': 'Alerte marquée comme résolue',
            'alerte': AlerteConformiteSerializer(alerte).data
        })
    
    @action(detail=True, methods=['post'])
    def escalader(self, request, pk=None):
        """Escalader une alerte"""
        alerte = self.get_object()
        alerte.statut = 'ESCALADEE'
        alerte.utilisateur_traitement = request.user
        alerte.commentaires = request.data.get('commentaires', '')
        alerte.save()
        
        return Response({
            'message': 'Alerte escaladée',
            'alerte': AlerteConformiteSerializer(alerte).data
        })
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """Obtenir les statistiques des alertes"""
        stats = ServiceAlertesConformite.obtenir_statistiques_conformite()
        serializer = StatistiquesConformiteSerializer(stats)
        return Response(serializer.data)

class RegleAlerteConformiteViewSet(viewsets.ModelViewSet):
    """ViewSet pour les règles d'alertes de conformité"""
    queryset = RegleAlerteConformite.objects.all()
    serializer_class = RegleAlerteConformiteSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        return RegleAlerteConformite.objects.filter(is_active=True)

class NotificationConformiteViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les notifications de conformité"""
    serializer_class = NotificationConformiteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return NotificationConformite.objects.filter(
            destinataire=user
        ).select_related('alerte', 'destinataire')

class AuditConformiteViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour l'audit de conformité"""
    serializer_class = AuditConformiteSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        return AuditConformite.objects.select_related(
            'utilisateur', 'alerte_generee'
        ).all()

# ===================== VUES API =====================

@api_view(['POST'])
@permission_classes([IsAdminUser])
def initialiser_types_alertes(request):
    """Initialiser tous les types d'alertes de conformité"""
    try:
        ServiceAlertesConformite.initialiser_types_alertes()
        return Response({
            'message': 'Types d\'alertes de conformité initialisés avec succès'
        })
    except Exception as e:
        return Response({
            'error': f'Erreur lors de l\'initialisation: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def executer_surveillance_conformite(request):
    """Exécuter la surveillance de conformité"""
    try:
        alertes_crees = ServiceAlertesConformite.executer_surveillance_conformite()
        return Response({
            'message': f'Surveillance terminée: {len(alertes_crees)} alertes créées',
            'alertes_crees': len(alertes_crees)
        })
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la surveillance: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alertes_conformite_critiques(request):
    """Obtenir les alertes de conformité critiques"""
    try:
        user = request.user
        queryset = AlerteConformite.objects.filter(
            niveau_critique__gte=4,
            statut__in=['NOUVELLE', 'EN_COURS']
        )
        
        if user.role != 'ADMIN':
            queryset = queryset.filter(
                Q(utilisateur_origine=user) | 
                Q(patient__medecin=user) | 
                Q(dossier__patient__medecin=user)
            )
        
        alertes = queryset.select_related(
            'type_alerte', 'utilisateur_origine', 'patient', 'dossier'
        ).order_by('-niveau_critique', '-date_creation')[:20]
        
        serializer = AlerteConformiteSerializer(alertes, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la récupération des alertes: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def statistiques_conformite_detaillees(request):
    """Obtenir des statistiques détaillées de conformité"""
    try:
        # Statistiques par norme de conformité
        stats_par_norme = AlerteConformite.objects.values(
            'type_alerte__norme_conformite'
        ).annotate(
            total=Count('id'),
            nouvelles=Count('id', filter=Q(statut='NOUVELLE')),
            en_cours=Count('id', filter=Q(statut='EN_COURS')),
            resolues=Count('id', filter=Q(statut='RESOLUE')),
            critiques=Count('id', filter=Q(niveau_critique=4)),
            urgentes=Count('id', filter=Q(niveau_critique=5))
        )
        
        # Statistiques par niveau de criticité
        stats_par_criticite = AlerteConformite.objects.values(
            'niveau_critique'
        ).annotate(
            total=Count('id')
        ).order_by('niveau_critique')
        
        # Tendances des 30 derniers jours
        date_limite = timezone.now() - timedelta(days=30)
        tendances = AlerteConformite.objects.filter(
            date_creation__gte=date_limite
        ).extra(
            select={'jour': 'DATE(date_creation)'}
        ).values('jour').annotate(
            total=Count('id'),
            rgpd=Count('id', filter=Q(type_alerte__norme_conformite='RGPD')),
            hipaa=Count('id', filter=Q(type_alerte__norme_conformite='HIPAA')),
            cdp=Count('id', filter=Q(type_alerte__norme_conformite='CDP'))
        ).order_by('jour')
        
        return Response({
            'stats_par_norme': list(stats_par_norme),
            'stats_par_criticite': list(stats_par_criticite),
            'tendances': list(tendances)
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la récupération des statistiques: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def configurer_alertes_conformite(request):
    """Configurer les paramètres des alertes de conformité"""
    try:
        serializer = ConfigurationAlertesSerializer(data=request.data)
        if serializer.is_valid():
            # Sauvegarder la configuration dans le cache
            config = serializer.validated_data
            cache.set('config_alertes_conformite', config, 3600)  # 1 heure
            
            return Response({
                'message': 'Configuration des alertes mise à jour',
                'config': config
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la configuration: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtenir_configuration_alertes(request):
    """Obtenir la configuration actuelle des alertes"""
    try:
        config = cache.get('config_alertes_conformite', {})
        if not config:
            # Configuration par défaut
            config = {
                'activation_surveillance': True,
                'delai_notification_defaut': 24,
                'escalation_automatique': True,
                'seuil_acces_non_autorise': 3,
                'seuil_consultation_excessive': 50,
                'seuil_modification_non_autorisee': 2,
                'notifier_admin_par_defaut': True,
                'notifier_dpo_par_defaut': False,
                'notifier_cdp_par_defaut': False,
                'bloquer_acces_automatique': False,
                'fermer_session_automatique': False,
                'logger_toutes_actions': True
            }
        
        serializer = ConfigurationAlertesSerializer(config)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la récupération de la configuration: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rapport_conformite(request):
    """Générer un rapport de conformité"""
    try:
        # Période du rapport
        date_debut = request.GET.get('date_debut')
        date_fin = request.GET.get('date_fin')
        
        if date_debut and date_fin:
            queryset = AlerteConformite.objects.filter(
                date_creation__range=[date_debut, date_fin]
            )
        else:
            # Derniers 30 jours par défaut
            date_limite = timezone.now() - timedelta(days=30)
            queryset = AlerteConformite.objects.filter(
                date_creation__gte=date_limite
            )
        
        # Statistiques du rapport
        total_alertes = queryset.count()
        alertes_resolues = queryset.filter(statut='RESOLUE').count()
        taux_resolution = (alertes_resolues / total_alertes * 100) if total_alertes > 0 else 0
        
        # Par norme de conformité
        stats_rgpd = queryset.filter(type_alerte__norme_conformite='RGPD').count()
        stats_hipaa = queryset.filter(type_alerte__norme_conformite='HIPAA').count()
        stats_cdp = queryset.filter(type_alerte__norme_conformite='CDP').count()
        
        # Alertes critiques
        alertes_critiques = queryset.filter(niveau_critique__gte=4).count()
        
        # Top des types d'alertes
        top_types = queryset.values(
            'type_alerte__nom'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        return Response({
            'periode': {
                'debut': date_debut or (timezone.now() - timedelta(days=30)).date(),
                'fin': date_fin or timezone.now().date()
            },
            'statistiques_generales': {
                'total_alertes': total_alertes,
                'alertes_resolues': alertes_resolues,
                'taux_resolution': round(taux_resolution, 2),
                'alertes_critiques': alertes_critiques
            },
            'par_norme': {
                'rgpd': stats_rgpd,
                'hipaa': stats_hipaa,
                'cdp': stats_cdp
            },
            'top_types_alertes': list(top_types),
            'recommandations': [
                'Renforcer la formation sur la conformité RGPD',
                'Améliorer les contrôles d\'accès HIPAA',
                'Mettre en place des audits réguliers CDP'
            ] if total_alertes > 10 else [
                'Niveau de conformité satisfaisant',
                'Continuer la surveillance active'
            ]
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la génération du rapport: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
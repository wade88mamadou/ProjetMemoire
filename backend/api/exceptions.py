from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)
security_logger = logging.getLogger('django.security')

class SecurityException(Exception):
    """Exception personnalisée pour les erreurs de sécurité"""
    def __init__(self, message, code=None, details=None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)

class RateLimitException(SecurityException):
    """Exception pour les limites de taux dépassées"""
    pass

class SuspiciousActivityException(SecurityException):
    """Exception pour les activités suspectes"""
    pass

class DataValidationException(Exception):
    """Exception pour les erreurs de validation de données"""
    def __init__(self, message, field_errors=None):
        self.message = message
        self.field_errors = field_errors or {}
        super().__init__(self.message)

def custom_exception_handler(exc, context):
    """
    Gestionnaire d'exceptions personnalisé
    """
    # Log de l'erreur
    request = context.get('request')
    view = context.get('view')
    
    logger.error(f"Exception dans {view.__class__.__name__}: {str(exc)}")
    
    # Gestion des exceptions de sécurité
    if isinstance(exc, SecurityException):
        security_logger.warning(f"Erreur de sécurité: {exc.message} - IP: {_get_client_ip(request)}")
        
        return Response({
            'error': 'Erreur de sécurité',
            'message': exc.message,
            'code': exc.code
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Gestion des exceptions de validation
    if isinstance(exc, DataValidationException):
        return Response({
            'error': 'Erreur de validation',
            'message': exc.message,
            'field_errors': exc.field_errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Gestion des erreurs de base de données
    if 'database' in str(exc).lower():
        logger.error(f"Erreur de base de données: {str(exc)}")
        return Response({
            'error': 'Erreur interne',
            'message': 'Une erreur est survenue lors du traitement de votre demande.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Gestion des erreurs de permission
    if 'permission' in str(exc).lower():
        return Response({
            'error': 'Permission refusée',
            'message': 'Vous n\'avez pas les permissions nécessaires pour effectuer cette action.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Gestion des erreurs d'authentification
    if 'authentication' in str(exc).lower():
        return Response({
            'error': 'Authentification requise',
            'message': 'Veuillez vous connecter pour accéder à cette ressource.'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Gestion des erreurs 404
    if 'not found' in str(exc).lower():
        return Response({
            'error': 'Ressource non trouvée',
            'message': 'La ressource demandée n\'existe pas.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Gestion des erreurs génériques
    return Response({
        'error': 'Erreur interne',
        'message': 'Une erreur inattendue s\'est produite.'
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def _get_client_ip(request):
    """Récupère l'IP du client"""
    if not request:
        return 'unknown'
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class SecurityMiddleware:
    """
    Middleware pour la détection d'activités suspectes
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Vérifications de sécurité avant le traitement
        if self._is_suspicious_request(request):
            security_logger.warning(f"Requête suspecte détectée: {request.path}")
            return Response({
                'error': 'Requête suspecte détectée',
                'message': 'Votre requête a été bloquée pour des raisons de sécurité.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        response = self.get_response(request)
        
        # Vérifications après le traitement
        if response.status_code >= 400:
            logger.warning(f"Erreur {response.status_code} pour {request.path}")
        
        return response
    
    def _is_suspicious_request(self, request):
        """Détecte les requêtes suspectes"""
        suspicious_patterns = [
            'script', 'javascript', 'vbscript', 'onload', 'onerror',
            'union', 'select', 'insert', 'update', 'delete', 'drop',
            'exec', 'eval', 'system', 'shell'
        ]
        
        # Vérifier l'URL
        path = request.path.lower()
        for pattern in suspicious_patterns:
            if pattern in path:
                return True
        
        # Vérifier les paramètres
        for key, value in request.GET.items():
            if any(pattern in str(value).lower() for pattern in suspicious_patterns):
                return True
        
        # Vérifier le body pour les requêtes POST
        if request.method == 'POST':
            for key, value in request.POST.items():
                if any(pattern in str(value).lower() for pattern in suspicious_patterns):
                    return True
        
        return False 
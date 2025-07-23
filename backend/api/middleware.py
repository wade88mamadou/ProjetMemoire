import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

logger = logging.getLogger(__name__)
security_logger = logging.getLogger('django.security')

class SecurityMiddleware(MiddlewareMixin):
    """Middleware pour la sécurité et l'audit"""
    
    def process_request(self, request):
        # Log de l'accès
        start_time = time.time()
        request.start_time = start_time
        
        # Vérification du rate limiting
        if self._is_rate_limited(request):
            security_logger.warning(f"Rate limit dépassé pour IP: {self._get_client_ip(request)}")
            return HttpResponseForbidden("Trop de requêtes. Veuillez réessayer plus tard.")
        
        # Log des tentatives d'accès suspectes
        if self._is_suspicious_request(request):
            security_logger.warning(f"Requête suspecte détectée: {request.path} depuis {self._get_client_ip(request)}")
        
        return None
    
    def process_response(self, request, response):
        # Calcul du temps de réponse
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(f"Requête {request.method} {request.path} - {response.status_code} - {duration:.3f}s")
        
        # Headers de sécurité
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response
    
    def _get_client_ip(self, request):
        """Récupère l'IP réelle du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _is_rate_limited(self, request):
        """Vérifie si l'IP a dépassé la limite de requêtes"""
        client_ip = self._get_client_ip(request)
        cache_key = f"rate_limit:{client_ip}"
        
        # Limite: 100 requêtes par minute
        current_count = cache.get(cache_key, 0)
        if current_count >= 100:
            return True
        
        cache.set(cache_key, current_count + 1, 60)  # Expire en 60 secondes
        return False
    
    def _is_suspicious_request(self, request):
        """Détecte les requêtes suspectes"""
        suspicious_patterns = [
            '/admin/',
            '/api/admin/',
            'sql',
            'script',
            'union',
            'select',
            'drop',
            'delete',
            'insert',
            'update'
        ]
        
        path = request.path.lower()
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        # Vérifier les patterns suspects dans l'URL
        for pattern in suspicious_patterns:
            if pattern in path:
                return True
        
        # Vérifier les User-Agents suspects
        suspicious_agents = ['sqlmap', 'nikto', 'nmap', 'scanner']
        for agent in suspicious_agents:
            if agent in user_agent:
                return True
        
        return False

class AuditMiddleware(MiddlewareMixin):
    """Middleware pour l'audit des accès"""
    
    def process_request(self, request):
        if request.user.is_authenticated:
            logger.info(f"Accès authentifié: {request.user.username} - {request.method} {request.path}")
        else:
            logger.info(f"Accès anonyme: {request.method} {request.path} depuis {self._get_client_ip(request)}")
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 

class SessionSecurityMiddleware:
    """
    Middleware pour la gestion sécurisée des sessions utilisateur
    - Surveillance de l'activité
    - Déconnexion automatique après inactivité
    - Logs de sécurité
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.session_timeout = 60  # 1 minute en secondes
        self.warning_time = 30     # 30 secondes avant expiration
        
    def __call__(self, request):
        # Ignorer les requêtes non authentifiées
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Vérifier l'activité de session
        session_key = f"user_activity_{request.user.id}"
        last_activity = cache.get(session_key)
        current_time = timezone.now()
        
        # Première activité ou mise à jour
        if not last_activity:
            cache.set(session_key, current_time, self.session_timeout)
            logger.info(f"Session démarrée pour l'utilisateur {request.user.username}")
        else:
            # Vérifier si la session a expiré
            time_diff = (current_time - last_activity).total_seconds()
            
            if time_diff > self.session_timeout:
                # Session expirée - déconnexion forcée
                logger.warning(f"Session expirée pour l'utilisateur {request.user.username} après {time_diff:.1f}s d'inactivité")
                
                # Nettoyer le cache
                cache.delete(session_key)
                
                # Réponse d'erreur pour les requêtes API
                if request.path.startswith('/api/'):
                    return JsonResponse({
                        'error': 'Session expirée',
                        'message': 'Votre session a expiré en raison d\'inactivité. Veuillez vous reconnecter.',
                        'code': 'SESSION_EXPIRED'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
                # Redirection pour les autres requêtes
                from django.shortcuts import redirect
                from django.contrib.auth import logout
                logout(request)
                return redirect('/login?expired=true')
            
            # Mettre à jour l'activité
            cache.set(session_key, current_time, self.session_timeout)
            
            # Avertissement si proche de l'expiration
            if time_diff > self.warning_time:
                logger.info(f"Session proche de l'expiration pour {request.user.username} ({self.session_timeout - time_diff:.1f}s restant)")
        
        response = self.get_response(request)
        
        # Ajouter des headers de sécurité
        response['X-Session-Timeout'] = str(self.session_timeout)
        response['X-Session-Warning'] = str(self.warning_time)
        
        return response

class JWTSecurityMiddleware:
    """
    Middleware pour la validation stricte des tokens JWT
    - Vérification de l'expiration
    - Blacklist des tokens révoqués
    - Logs de sécurité
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Vérifier les tokens JWT dans les headers
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            try:
                # Valider le token
                access_token = AccessToken(token)
                
                # Vérifier si le token est dans la blacklist
                jti = access_token.get('jti')
                if jti and cache.get(f"blacklist_{jti}"):
                    logger.warning(f"Token JWT blacklisté détecté: {jti}")
                    return JsonResponse({
                        'error': 'Token invalide',
                        'message': 'Ce token a été révoqué.',
                        'code': 'TOKEN_BLACKLISTED'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
                # Log de l'activité JWT
                user_id = access_token.get('user_id')
                if user_id:
                    logger.debug(f"Token JWT valide pour l'utilisateur {user_id}")
                    
            except (InvalidToken, TokenError) as e:
                logger.warning(f"Token JWT invalide: {str(e)}")
                return JsonResponse({
                    'error': 'Token invalide',
                    'message': 'Votre token d\'authentification est invalide ou expiré.',
                    'code': 'INVALID_TOKEN'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        return self.get_response(request) 
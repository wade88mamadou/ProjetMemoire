import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.core.cache import cache

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
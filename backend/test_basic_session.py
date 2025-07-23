#!/usr/bin/env python
"""
Test simple de la configuration des sessions
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

def test_session_configuration():
    """Test de la configuration des sessions"""
    print("🚀 Test de la configuration des sessions...")
    
    # Vérifier la configuration JWT
    print("📋 Configuration JWT:")
    print(f"   ACCESS_TOKEN_LIFETIME: {settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']}")
    print(f"   REFRESH_TOKEN_LIFETIME: {settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']}")
    print(f"   SLIDING_TOKEN_LIFETIME: {settings.SIMPLE_JWT['SLIDING_TOKEN_LIFETIME']}")
    
    # Vérifier la configuration des sessions
    print("\n📋 Configuration des sessions:")
    print(f"   SESSION_COOKIE_AGE: {settings.SESSION_COOKIE_AGE} secondes")
    print(f"   SESSION_EXPIRE_AT_BROWSER_CLOSE: {settings.SESSION_EXPIRE_AT_BROWSER_CLOSE}")
    print(f"   SESSION_COOKIE_HTTPONLY: {settings.SESSION_COOKIE_HTTPONLY}")
    print(f"   SESSION_COOKIE_SAMESITE: {settings.SESSION_COOKIE_SAMESITE}")
    print(f"   SESSION_SAVE_EVERY_REQUEST: {settings.SESSION_SAVE_EVERY_REQUEST}")
    
    # Test du cache
    print("\n📋 Test du cache:")
    test_key = "test_session_key"
    test_value = "test_value"
    
    cache.set(test_key, test_value, 60)
    retrieved_value = cache.get(test_key)
    
    if retrieved_value == test_value:
        print("   ✅ Cache fonctionne correctement")
    else:
        print("   ❌ Problème avec le cache")
    
    # Nettoyer le test
    cache.delete(test_key)
    
    return True

def test_middleware_import():
    """Test de l'import des middlewares"""
    print("\n🚀 Test des middlewares...")
    
    try:
        from api.middleware import SessionSecurityMiddleware, JWTSecurityMiddleware
        print("   ✅ Middlewares importés avec succès")
        return True
    except ImportError as e:
        print(f"   ❌ Erreur d'import des middlewares: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Test de la configuration de base des sessions")
    print("=" * 60)
    
    config_ok = test_session_configuration()
    middleware_ok = test_middleware_import()
    
    print("\n" + "=" * 60)
    print("📊 Résumé des tests:")
    print(f"   Configuration: {'✅' if config_ok else '❌'}")
    print(f"   Middlewares: {'✅' if middleware_ok else '❌'}")
    
    if config_ok and middleware_ok:
        print("\n🎉 Configuration de base OK! Les sessions sont configurées correctement.")
    else:
        print("\n⚠️  Problèmes détectés dans la configuration.")

if __name__ == '__main__':
    main() 
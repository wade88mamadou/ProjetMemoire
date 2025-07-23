#!/usr/bin/env python
"""
Script de test pour la politique de sécurité des sessions
"""
import os
import sys
import django
import time
from datetime import timedelta

# Configuration Django AVANT tout import
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.tokens import RefreshToken
from api.views import LoginView, refresh_session, session_status, logout_user

def test_session_timeout():
    """Test de l'expiration de session après 1 minute"""
    print("🚀 Test d'expiration de session...")
    
    try:
        # Créer un utilisateur de test
        user, created = get_user_model().objects.get_or_create(
            username='test_session_user',
            defaults={
                'email': 'test_session@test.com',
                'first_name': 'Test',
                'last_name': 'Session',
                'role': 'user_simple'
            }
        )
        
        if created:
            user.set_password('test123')
            user.save()
            print("👤 Utilisateur de test créé")
        
        # Simuler une connexion
        factory = APIRequestFactory()
        login_request = factory.post('/api/auth/login/', {
            'username': 'test_session_user',
            'password': 'test123'
        }, content_type='application/json')
        
        login_view = LoginView.as_view()
        login_response = login_view(login_request)
        
        if login_response.status_code == 200:
            print("✅ Connexion réussie")
            
            # Extraire le token
            access_token = login_response.data.get('access')
            
            # Vérifier le statut initial de la session
            status_request = factory.get('/api/auth/session-status/')
            status_request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
            
            status_view = session_status.as_view()
            status_response = status_view(status_request)
            
            if status_response.status_code == 200:
                print("✅ Statut de session récupéré")
                print(f"   Temps restant: {status_response.data.get('time_remaining')}s")
                
                # Attendre 2 secondes et vérifier le temps restant
                print("⏳ Attente de 2 secondes...")
                time.sleep(2)
                
                status_response2 = status_view(status_request)
                if status_response2.status_code == 200:
                    time_remaining = status_response2.data.get('time_remaining')
                    print(f"   Temps restant après 2s: {time_remaining}s")
                    
                    if time_remaining < 58:  # Devrait être inférieur à 58s
                        print("✅ Décrémentation du temps fonctionne")
                        return True
                    else:
                        print("❌ Décrémentation du temps ne fonctionne pas")
                        return False
                else:
                    print(f"❌ Erreur lors de la vérification du statut: {status_response2.status_code}")
                    return False
            else:
                print(f"❌ Erreur lors de la récupération du statut: {status_response.status_code}")
                return False
        else:
            print(f"❌ Erreur de connexion: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_session_refresh():
    """Test du refresh de session"""
    print("\n🚀 Test de refresh de session...")
    
    try:
        # Créer un utilisateur de test
        user, created = get_user_model().objects.get_or_create(
            username='test_refresh_user',
            defaults={
                'email': 'test_refresh@test.com',
                'first_name': 'Test',
                'last_name': 'Refresh',
                'role': 'user_simple'
            }
        )
        
        if created:
            user.set_password('test123')
            user.save()
            print("👤 Utilisateur de test créé")
        
        # Simuler une connexion
        factory = APIRequestFactory()
        login_request = factory.post('/api/auth/login/', {
            'username': 'test_refresh_user',
            'password': 'test123'
        })
        
        login_view = LoginView.as_view()
        login_response = login_view(login_request)
        
        if login_response.status_code == 200:
            print("✅ Connexion réussie")
            
            # Extraire le token
            access_token = login_response.data.get('access')
            
            # Tester le refresh de session
            refresh_request = factory.post('/api/auth/refresh-session/')
            refresh_request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
            
            refresh_view = refresh_session.as_view()
            refresh_response = refresh_view(refresh_request)
            
            if refresh_response.status_code == 200:
                print("✅ Refresh de session réussi")
                print(f"   Nouveau token: {refresh_response.data.get('access_token')[:20]}...")
                print(f"   Expires in: {refresh_response.data.get('expires_in')}s")
                return True
            else:
                print(f"❌ Erreur lors du refresh: {refresh_response.status_code}")
                return False
        else:
            print(f"❌ Erreur de connexion: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def test_secure_logout():
    """Test de déconnexion sécurisée"""
    print("\n🚀 Test de déconnexion sécurisée...")
    
    try:
        # Créer un utilisateur de test
        user, created = get_user_model().objects.get_or_create(
            username='test_logout_user',
            defaults={
                'email': 'test_logout@test.com',
                'first_name': 'Test',
                'last_name': 'Logout',
                'role': 'user_simple'
            }
        )
        
        if created:
            user.set_password('test123')
            user.save()
            print("👤 Utilisateur de test créé")
        
        # Simuler une connexion
        factory = APIRequestFactory()
        login_request = factory.post('/api/auth/login/', {
            'username': 'test_logout_user',
            'password': 'test123'
        })
        
        login_view = LoginView.as_view()
        login_response = login_view(login_request)
        
        if login_response.status_code == 200:
            print("✅ Connexion réussie")
            
            # Extraire le token
            access_token = login_response.data.get('access')
            
            # Tester la déconnexion sécurisée
            logout_request = factory.post('/api/auth/logout-secure/')
            logout_request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
            
            logout_view = logout_user.as_view()
            logout_response = logout_view(logout_request)
            
            if logout_response.status_code == 200:
                print("✅ Déconnexion sécurisée réussie")
                
                # Vérifier que la session a été nettoyée
                session_key = f"user_activity_{user.id}"
                session_exists = cache.get(session_key)
                
                if not session_exists:
                    print("✅ Session nettoyée du cache")
                    return True
                else:
                    print("❌ Session pas nettoyée du cache")
                    return False
            else:
                print(f"❌ Erreur lors de la déconnexion: {logout_response.status_code}")
                return False
        else:
            print(f"❌ Erreur de connexion: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def cleanup_test_users():
    """Nettoyer les utilisateurs de test"""
    print("\n🧹 Nettoyage des utilisateurs de test...")
    
    try:
        # Supprimer les utilisateurs de test
        test_users = get_user_model().objects.filter(
            username__in=['test_session_user', 'test_refresh_user', 'test_logout_user']
        )
        count = test_users.count()
        test_users.delete()
        print(f"✅ {count} utilisateurs de test supprimés")
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")

def main():
    """Fonction principale"""
    print("🚀 Test de la politique de sécurité des sessions")
    print("=" * 60)
    
    # Tests
    timeout_ok = test_session_timeout()
    refresh_ok = test_session_refresh()
    logout_ok = test_secure_logout()
    
    # Nettoyage
    cleanup_test_users()
    
    print("\n" + "=" * 60)
    print("📊 Résumé des tests:")
    print(f"   Expiration de session: {'✅' if timeout_ok else '❌'}")
    print(f"   Refresh de session: {'✅' if refresh_ok else '❌'}")
    print(f"   Déconnexion sécurisée: {'✅' if logout_ok else '❌'}")
    
    if timeout_ok and refresh_ok and logout_ok:
        print("\n🎉 Tous les tests sont passés! La politique de sécurité fonctionne.")
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifiez la configuration.")

if __name__ == '__main__':
    main() 
#!/usr/bin/env python
"""
Script de test pour la création d'utilisateur avec envoi d'email
"""
import os
import sys
import django

# Configuration Django AVANT tout import
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from api.serializers import UserCreateSerializer
from rest_framework.test import APIRequestFactory

def test_user_creation():
    """Test de création d'utilisateur avec envoi d'email"""
    print("🚀 Test de création d'utilisateur...")
    
    # Données de test
    user_data = {
        'username': 'test_user_123',
        'email': 'test_user_123@gmail.com',  # Email unique pour le test
        'password': 'testpassword123',
        'password_confirm': 'testpassword123',
        'first_name': 'Test',
        'last_name': 'User',
        'role': 'user_simple'  # Correction: en minuscules
    }
    
    print(f"📝 Données utilisateur: {user_data}")
    
    try:
        # Créer un utilisateur admin pour le contexte
        admin_user, created = get_user_model().objects.get_or_create(
            username='admin_test',
            defaults={
                'email': 'admin@test.com',
                'first_name': 'Admin',
                'last_name': 'Test',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            print("👤 Utilisateur admin créé pour le test")
        
        # Créer le serializer avec contexte
        factory = APIRequestFactory()
        request = factory.post('/api/admin/users/')
        request.user = admin_user
        
        serializer = UserCreateSerializer(data=user_data, context={'request': request})
        
        if serializer.is_valid():
            print("✅ Données valides")
            
            # Créer l'utilisateur
            user = serializer.save()
            print(f"✅ Utilisateur créé: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Must change password: {user.must_change_password}")
            
            # Vérifier que l'utilisateur existe en base
            user_in_db = get_user_model().objects.filter(username=user_data['username']).first()
            if user_in_db:
                print("✅ Utilisateur trouvé en base de données")
            else:
                print("❌ Utilisateur non trouvé en base de données")
            
            return True
            
        else:
            print("❌ Erreurs de validation:")
            for field, errors in serializer.errors.items():
                print(f"   {field}: {errors}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_email_sending():
    """Test d'envoi d'email simple"""
    print("\n📧 Test d'envoi d'email...")
    
    try:
        from django.core.mail import send_mail
        
        result = send_mail(
            subject='Test Création Utilisateur - Conformed',
            message='Ceci est un test d\'envoi d\'email lors de la création d\'utilisateur.',
            from_email=None,
            recipient_list=['test_user_123@gmail.com'],
            fail_silently=False,
        )
        print(f"✅ Email de test envoyé! Résultat: {result}")
        return True
    except Exception as e:
        print(f"❌ Erreur d'envoi d'email: {e}")
        return False

def cleanup_test_users():
    """Nettoyer les utilisateurs de test"""
    print("\n🧹 Nettoyage des utilisateurs de test...")
    
    try:
        # Supprimer les utilisateurs de test
        test_users = get_user_model().objects.filter(
            username__in=['test_user_123', 'admin_test']
        )
        count = test_users.count()
        test_users.delete()
        print(f"✅ {count} utilisateurs de test supprimés")
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")

def main():
    """Fonction principale"""
    print("🚀 Test complet de création d'utilisateur avec email")
    print("=" * 60)
    
    # Test d'envoi d'email
    email_ok = test_email_sending()
    
    # Test de création d'utilisateur
    user_ok = test_user_creation()
    
    # Nettoyage
    cleanup_test_users()
    
    print("\n" + "=" * 60)
    print("📊 Résumé des tests:")
    print(f"   Envoi d'email: {'✅' if email_ok else '❌'}")
    print(f"   Création utilisateur: {'✅' if user_ok else '❌'}")
    
    if email_ok and user_ok:
        print("\n🎉 Tous les tests sont passés! L'envoi d'email fonctionne.")
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifiez la configuration.")

if __name__ == '__main__':
    main() 
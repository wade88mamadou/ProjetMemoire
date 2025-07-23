#!/usr/bin/env python
"""
Script de test pour la suppression d'utilisateur
"""
import os
import sys
import django

# Configuration Django AVANT tout import
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from api.serializers import UserCreateSerializer
from rest_framework.test import APIRequestFactory
from api.views import UserAdminDetailView
from rest_framework import status

def test_user_deletion():
    """Test de suppression d'utilisateur"""
    print("🚀 Test de suppression d'utilisateur...")
    
    try:
        # Créer un utilisateur admin pour le test
        admin_user, created = get_user_model().objects.get_or_create(
            username='admin_test_delete',
            defaults={
                'email': 'admin_delete@test.com',
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
        
        # Créer un utilisateur à supprimer
        user_to_delete, created = get_user_model().objects.get_or_create(
            username='user_to_delete',
            defaults={
                'email': 'user_to_delete@test.com',
                'first_name': 'User',
                'last_name': 'ToDelete',
                'role': 'user_simple',
                'password': 'test123'
            }
        )
        
        if created:
            user_to_delete.set_password('test123')
            user_to_delete.save()
            print("👤 Utilisateur à supprimer créé")
        
        print(f"📝 Utilisateur à supprimer: {user_to_delete.username} (ID: {user_to_delete.id})")
        
        # Créer la vue et la requête
        factory = APIRequestFactory()
        request = factory.delete(f'/api/admin/users/{user_to_delete.id}/')
        request.user = admin_user
        
        # Ajouter l'authentification
        from rest_framework.test import force_authenticate
        force_authenticate(request, user=admin_user)
        
        # Ajouter l'authentification
        from rest_framework.test import force_authenticate
        force_authenticate(request, user=admin_user)
        
        view = UserAdminDetailView.as_view()
        response = view(request, pk=user_to_delete.id)
        
        print(f"📊 Réponse de suppression: {response.status_code}")
        
        if response.status_code == status.HTTP_204_NO_CONTENT:
            print("✅ Suppression réussie!")
            
            # Vérifier que l'utilisateur n'existe plus
            user_exists = get_user_model().objects.filter(id=user_to_delete.id).exists()
            if not user_exists:
                print("✅ Utilisateur supprimé de la base de données")
                return True
            else:
                print("❌ Utilisateur existe encore en base")
                return False
        else:
            print(f"❌ Erreur de suppression: {response.data}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_self_deletion_prevention():
    """Test de prévention de suppression de son propre compte"""
    print("\n🚀 Test de prévention de suppression de son propre compte...")
    
    try:
        # Créer un utilisateur admin
        admin_user, created = get_user_model().objects.get_or_create(
            username='admin_self_delete',
            defaults={
                'email': 'admin_self@test.com',
                'first_name': 'Admin',
                'last_name': 'Self',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            print("👤 Utilisateur admin créé pour le test")
        
        # Essayer de se supprimer soi-même
        factory = APIRequestFactory()
        request = factory.delete(f'/api/admin/users/{admin_user.id}/')
        request.user = admin_user
        
        # Ajouter l'authentification
        from rest_framework.test import force_authenticate
        force_authenticate(request, user=admin_user)
        
        # Ajouter l'authentification
        from rest_framework.test import force_authenticate
        force_authenticate(request, user=admin_user)
        
        view = UserAdminDetailView.as_view()
        response = view(request, pk=admin_user.id)
        
        print(f"📊 Réponse de tentative de suppression: {response.status_code}")
        
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            print("✅ Prévention de suppression de son propre compte fonctionne!")
            return True
        else:
            print("❌ La prévention ne fonctionne pas")
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
            username__in=['admin_test_delete', 'admin_self_delete']
        )
        count = test_users.count()
        test_users.delete()
        print(f"✅ {count} utilisateurs de test supprimés")
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")

def main():
    """Fonction principale"""
    print("🚀 Test complet de suppression d'utilisateur")
    print("=" * 60)
    
    # Test de suppression normale
    deletion_ok = test_user_deletion()
    
    # Test de prévention de suppression de son propre compte
    prevention_ok = test_self_deletion_prevention()
    
    # Nettoyage
    cleanup_test_users()
    
    print("\n" + "=" * 60)
    print("📊 Résumé des tests:")
    print(f"   Suppression normale: {'✅' if deletion_ok else '❌'}")
    print(f"   Prévention auto-suppression: {'✅' if prevention_ok else '❌'}")
    
    if deletion_ok and prevention_ok:
        print("\n🎉 Tous les tests sont passés! La suppression fonctionne correctement.")
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifiez la configuration.")

if __name__ == '__main__':
    main() 
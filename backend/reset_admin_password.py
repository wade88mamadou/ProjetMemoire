#!/usr/bin/env python
"""
Script pour réinitialiser le mot de passe de l'admin
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from api.models import Utilisateur

def reset_admin_password():
    """Réinitialise le mot de passe de l'admin"""
    try:
        # Trouver l'utilisateur admin
        admin = Utilisateur.objects.get(username='admin')
        
        # Nouveau mot de passe simple pour le développement
        new_password = 'admin123'
        
        # Mettre à jour le mot de passe
        admin.set_password(new_password)
        admin.is_superuser = True
        admin.is_staff = True
        admin.is_active = True
        admin.save()
        
        print(f"✅ Mot de passe de l'admin réinitialisé avec succès!")
        print(f"Nom d'utilisateur: admin")
        print(f"Nouveau mot de passe: {new_password}")
        print(f"URL de connexion: http://127.0.0.1:8000/api/auth/login/")
        
    except Utilisateur.DoesNotExist:
        print("❌ Utilisateur 'admin' non trouvé")
        print("Création d'un nouvel utilisateur admin...")
        
        # Créer un nouvel admin
        admin = Utilisateur.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='ADMIN',
            is_superuser=True,
            is_staff=True,
            is_active=True
        )
        
        print(f"✅ Nouvel admin créé avec succès!")
        print(f"Nom d'utilisateur: admin")
        print(f"Mot de passe: admin123")
        print(f"URL de connexion: http://127.0.0.1:8000/api/auth/login/")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    reset_admin_password() 
#!/usr/bin/env python3
"""
Script de déploiement sécurisé pour ConformiMed
"""

import os
import sys
import secrets
import string
from pathlib import Path

def generate_secret_key(length=50):
    """Génère une clé secrète sécurisée"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_jwt_secret(length=50):
    """Génère une clé JWT séparée"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_env_file():
    """Crée le fichier .env avec des valeurs sécurisées"""
    print("🔧 Création du fichier .env sécurisé...")
    
    # Générer des clés sécurisées
    secret_key = generate_secret_key()
    jwt_secret = generate_jwt_secret()
    
    env_content = f"""# Configuration Django
SECRET_KEY={secret_key}
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,votre-domaine.com

# Base de données PostgreSQL
DB_NAME=conformimed_db
DB_USER=conformimed_user
DB_PASSWORD=mot-de-passe-très-sécurisé-pour-postgresql
DB_HOST=localhost
DB_PORT=5432

# JWT Configuration
JWT_SECRET_KEY={jwt_secret}
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=1440

# Email Configuration (pour notifications et réinitialisation de mot de passe)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=mot-de-passe-app-gmail
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=votre-email@gmail.com

# Sécurité HTTPS
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS=https://votre-domaine.com,https://www.votre-domaine.com

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://votre-domaine.com

# Redis Cache (optionnel mais recommandé)
REDIS_URL=redis://127.0.0.1:6379/1

# Logging
LOG_LEVEL=INFO
SECURITY_LOG_LEVEL=WARNING

# Rate Limiting
RATE_LIMIT_ANON=100/hour
RATE_LIMIT_USER=1000/hour

# File Upload Limits
FILE_UPLOAD_MAX_SIZE=10485760
DATA_UPLOAD_MAX_SIZE=10485760
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Fichier .env créé avec des clés sécurisées")

def create_logs_directory():
    """Crée le répertoire de logs"""
    print("📁 Création du répertoire de logs...")
    
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Créer les fichiers de log vides
    (logs_dir / 'django.log').touch()
    (logs_dir / 'security.log').touch()
    
    print("✅ Répertoire de logs créé")

def check_dependencies():
    """Vérifie les dépendances de sécurité"""
    print("📦 Vérification des dépendances de sécurité...")
    
    required_packages = [
        ('django-axes', 'axes'),
        ('django-redis', 'django_redis'),
        ('django-ratelimit', 'ratelimit'),
        ('cryptography', 'cryptography'),
        ('redis', 'redis')
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name} installé")
        except ImportError:
            missing_packages.append(package_name)
            print(f"❌ {package_name} manquant")
    
    if missing_packages:
        print(f"\n⚠️ Packages manquants: {', '.join(missing_packages)}")
        print("Installez-les avec: pip install " + " ".join(missing_packages))
        return False
    
    return True

def create_security_checklist():
    """Crée une checklist de sécurité"""
    print("📋 Création de la checklist de sécurité...")
    
    checklist_content = """# Checklist de Sécurité - ConformiMed

## ✅ Configuration de Base
- [ ] Fichier .env créé avec des clés sécurisées
- [ ] DEBUG = False en production
- [ ] SECRET_KEY générée de manière sécurisée
- [ ] ALLOWED_HOSTS configuré

## ✅ Base de Données
- [ ] PostgreSQL configuré
- [ ] Utilisateur de base de données avec privilèges limités
- [ ] Mot de passe fort pour la base de données
- [ ] Connexion SSL activée

## ✅ Authentification
- [ ] JWT configuré avec clé séparée
- [ ] Durée de vie des tokens limitée
- [ ] Protection contre les attaques par force brute (django-axes)
- [ ] Validation des mots de passe renforcée

## ✅ Validation des Données
- [ ] Validateurs personnalisés implémentés
- [ ] Sanitisation des entrées utilisateur
- [ ] Validation des emails (exclusion des emails temporaires)
- [ ] Validation des noms d'utilisateur

## ✅ Logging et Monitoring
- [ ] Logs de sécurité configurés
- [ ] Logs d'audit activés
- [ ] Middleware de sécurité implémenté
- [ ] Détection d'activités suspectes

## ✅ Rate Limiting
- [ ] Limitation de taux configurée
- [ ] Protection contre les attaques DDoS
- [ ] Cache configuré pour les sessions

## ✅ Headers de Sécurité
- [ ] X-Frame-Options: DENY
- [ ] X-Content-Type-Options: nosniff
- [ ] X-XSS-Protection: 1; mode=block
- [ ] Referrer-Policy configuré

## ✅ HTTPS/SSL
- [ ] SSL/TLS configuré
- [ ] HSTS activé
- [ ] Cookies sécurisés
- [ ] CSRF protection

## ✅ Gestion des Erreurs
- [ ] Gestionnaire d'exceptions personnalisé
- [ ] Messages d'erreur sécurisés
- [ ] Logs d'erreur configurés

## 🔄 Actions Requises
1. Modifier les valeurs dans .env selon votre environnement
2. Configurer votre serveur SMTP pour les emails
3. Configurer votre domaine dans CORS_ALLOWED_ORIGINS
4. Configurer HTTPS sur votre serveur
5. Tester toutes les fonctionnalités de sécurité

## 📞 Support
En cas de problème, consultez la documentation Django et les logs de sécurité.
"""
    
    with open('SECURITY_CHECKLIST.md', 'w', encoding='utf-8') as f:
        f.write(checklist_content)
    
    print("✅ Checklist de sécurité créée")

def main():
    """Fonction principale"""
    print("🚀 Déploiement sécurisé de ConformiMed")
    print("=" * 50)
    
    # Vérifier les dépendances
    if not check_dependencies():
        print("\n❌ Déploiement interrompu - Dépendances manquantes")
        sys.exit(1)
    
    # Créer le fichier .env
    create_env_file()
    
    # Créer le répertoire de logs
    create_logs_directory()
    
    # Créer la checklist
    create_security_checklist()
    
    print("\n" + "=" * 50)
    print("🎉 Déploiement sécurisé terminé !")
    print("=" * 50)
    print("📋 Consultez SECURITY_CHECKLIST.md pour les prochaines étapes")
    print("🔧 Modifiez le fichier .env selon votre environnement")
    print("🧪 Exécutez python test_security_simple.py pour vérifier la configuration")

if __name__ == "__main__":
    main() 
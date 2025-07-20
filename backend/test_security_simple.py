#!/usr/bin/env python3
"""
Script de test des fonctionnalités de sécurité (version simplifiée)
"""

import os
import sys
import django
from django.core.cache import cache

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from api.validators import validate_password_strength, validate_username, validate_email, sanitize_input

def test_password_strength():
    """Test de la validation de force du mot de passe"""
    print("🔐 Test de validation de force du mot de passe...")
    
    # Test mot de passe faible
    weak_passwords = [
        "123456",
        "password",
        "abc123",
        "qwerty",
        "admin123"
    ]
    
    passed = 0
    total = len(weak_passwords)
    
    for password in weak_passwords:
        try:
            validate_password_strength(password)
            print(f"❌ Mot de passe faible accepté: {password}")
        except Exception as e:
            print(f"✅ Mot de passe faible rejeté: {password} - {str(e)}")
            passed += 1
    
    # Test mot de passe fort
    strong_password = "SecurePass123!"
    try:
        validate_password_strength(strong_password)
        print(f"✅ Mot de passe fort accepté: {strong_password}")
        passed += 1
    except Exception as e:
        print(f"❌ Mot de passe fort rejeté: {strong_password} - {str(e)}")
    
    total += 1
    return passed, total

def test_username_validation():
    """Test de la validation du nom d'utilisateur"""
    print("\n👤 Test de validation du nom d'utilisateur...")
    
    # Test noms d'utilisateur valides
    valid_usernames = ["john_doe", "user123", "test_user"]
    passed = 0
    total = len(valid_usernames)
    
    for username in valid_usernames:
        try:
            validate_username(username)
            print(f"✅ Nom d'utilisateur valide: {username}")
            passed += 1
        except Exception as e:
            print(f"❌ Nom d'utilisateur valide rejeté: {username} - {str(e)}")
    
    # Test noms d'utilisateur invalides
    invalid_usernames = ["admin", "root", "system", "test", "guest"]
    for username in invalid_usernames:
        try:
            validate_username(username)
            print(f"❌ Nom d'utilisateur réservé accepté: {username}")
        except Exception as e:
            print(f"✅ Nom d'utilisateur réservé rejeté: {username} - {str(e)}")
            passed += 1
        total += 1
    
    return passed, total

def test_email_validation():
    """Test de la validation d'email"""
    print("\n📧 Test de validation d'email...")
    
    # Test emails valides
    valid_emails = ["test@example.com", "user@domain.org", "john.doe@company.co.uk"]
    passed = 0
    total = len(valid_emails)
    
    for email in valid_emails:
        try:
            validate_email(email)
            print(f"✅ Email valide: {email}")
            passed += 1
        except Exception as e:
            print(f"❌ Email valide rejeté: {email} - {str(e)}")
    
    # Test emails temporaires
    temp_emails = ["test@10minutemail.com", "user@guerrillamail.com", "temp@yopmail.com"]
    for email in temp_emails:
        try:
            validate_email(email)
            print(f"❌ Email temporaire accepté: {email}")
        except Exception as e:
            print(f"✅ Email temporaire rejeté: {email} - {str(e)}")
            passed += 1
        total += 1
    
    return passed, total

def test_input_sanitization():
    """Test de la sanitisation des entrées"""
    print("\n🧹 Test de sanitisation des entrées...")
    
    # Test entrées malveillantes
    malicious_inputs = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "admin' OR '1'='1",
        "'; DROP TABLE users; --"
    ]
    
    passed = 0
    total = len(malicious_inputs)
    
    for malicious_input in malicious_inputs:
        sanitized = sanitize_input(malicious_input)
        if "<script>" in sanitized or "javascript:" in sanitized:
            print(f"❌ Entrée malveillante non nettoyée: {malicious_input}")
        else:
            print(f"✅ Entrée malveillante nettoyée: {malicious_input} -> {sanitized}")
            passed += 1
    
    return passed, total

def test_logging():
    """Test du système de logging"""
    print("\n📝 Test du système de logging...")
    
    log_file = "logs/django.log"
    security_log_file = "logs/security.log"
    
    passed = 0
    total = 2
    
    if os.path.exists(log_file):
        print(f"✅ Fichier de log principal créé: {log_file}")
        passed += 1
    else:
        print(f"❌ Fichier de log principal manquant: {log_file}")
    
    if os.path.exists(security_log_file):
        print(f"✅ Fichier de log de sécurité créé: {security_log_file}")
        passed += 1
    else:
        print(f"❌ Fichier de log de sécurité manquant: {security_log_file}")
    
    return passed, total

def main():
    """Fonction principale"""
    print("🔒 Démarrage des tests de sécurité...")
    print("=" * 50)
    
    total_passed = 0
    total_tests = 0
    
    # Tests
    passed, total = test_password_strength()
    total_passed += passed
    total_tests += total
    
    passed, total = test_username_validation()
    total_passed += passed
    total_tests += total
    
    passed, total = test_email_validation()
    total_passed += passed
    total_tests += total
    
    passed, total = test_input_sanitization()
    total_passed += passed
    total_tests += total
    
    passed, total = test_logging()
    total_passed += passed
    total_tests += total
    
    print("\n" + "=" * 50)
    print("📊 Résultats des tests de sécurité:")
    print("=" * 50)
    print(f"✅ Tests réussis: {total_passed}")
    print(f"❌ Tests échoués: {total_tests - total_passed}")
    print(f"📈 Taux de réussite: {(total_passed/total_tests*100):.1f}%")
    
    if total_passed == total_tests:
        print("🎉 Tous les tests de sécurité sont passés !")
    else:
        print("⚠️ Certains tests de sécurité ont échoué. Vérifiez la configuration.")

if __name__ == "__main__":
    main() 
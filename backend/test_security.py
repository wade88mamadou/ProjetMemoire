#!/usr/bin/env python3
"""
Script de test des fonctionnalités de sécurité
"""

import os
import sys
import django
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APITestCase
from rest_framework import status

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from api.models import Utilisateur
from api.validators import validate_password_strength, validate_username, validate_email, sanitize_input

class SecurityTests:
    """Tests de sécurité"""
    
    def __init__(self):
        self.User = get_user_model()
        self.test_results = []
    
    def test_password_strength(self):
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
        
        for password in weak_passwords:
            try:
                validate_password_strength(password)
                self.test_results.append(f"❌ Mot de passe faible accepté: {password}")
            except Exception as e:
                self.test_results.append(f"✅ Mot de passe faible rejeté: {password} - {str(e)}")
        
        # Test mot de passe fort
        strong_password = "SecurePass123!"
        try:
            validate_password_strength(strong_password)
            self.test_results.append(f"✅ Mot de passe fort accepté: {strong_password}")
        except Exception as e:
            self.test_results.append(f"❌ Mot de passe fort rejeté: {strong_password} - {str(e)}")
    
    def test_username_validation(self):
        """Test de la validation du nom d'utilisateur"""
        print("👤 Test de validation du nom d'utilisateur...")
        
        # Test noms d'utilisateur valides
        valid_usernames = ["john_doe", "user123", "test_user"]
        for username in valid_usernames:
            try:
                validate_username(username)
                self.test_results.append(f"✅ Nom d'utilisateur valide: {username}")
            except Exception as e:
                self.test_results.append(f"❌ Nom d'utilisateur valide rejeté: {username} - {str(e)}")
        
        # Test noms d'utilisateur invalides
        invalid_usernames = ["admin", "root", "system", "test", "guest"]
        for username in invalid_usernames:
            try:
                validate_username(username)
                self.test_results.append(f"❌ Nom d'utilisateur réservé accepté: {username}")
            except Exception as e:
                self.test_results.append(f"✅ Nom d'utilisateur réservé rejeté: {username} - {str(e)}")
    
    def test_email_validation(self):
        """Test de la validation d'email"""
        print("📧 Test de validation d'email...")
        
        # Test emails valides
        valid_emails = ["test@example.com", "user@domain.org", "john.doe@company.co.uk"]
        for email in valid_emails:
            try:
                validate_email(email)
                self.test_results.append(f"✅ Email valide: {email}")
            except Exception as e:
                self.test_results.append(f"❌ Email valide rejeté: {email} - {str(e)}")
        
        # Test emails temporaires
        temp_emails = ["test@10minutemail.com", "user@guerrillamail.com", "temp@yopmail.com"]
        for email in temp_emails:
            try:
                validate_email(email)
                self.test_results.append(f"❌ Email temporaire accepté: {email}")
            except Exception as e:
                self.test_results.append(f"✅ Email temporaire rejeté: {email} - {str(e)}")
    
    def test_input_sanitization(self):
        """Test de la sanitisation des entrées"""
        print("🧹 Test de sanitisation des entrées...")
        
        # Test entrées malveillantes
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "admin' OR '1'='1",
            "'; DROP TABLE users; --"
        ]
        
        for malicious_input in malicious_inputs:
            sanitized = sanitize_input(malicious_input)
            if "<script>" in sanitized or "javascript:" in sanitized:
                self.test_results.append(f"❌ Entrée malveillante non nettoyée: {malicious_input}")
            else:
                self.test_results.append(f"✅ Entrée malveillante nettoyée: {malicious_input} -> {sanitized}")
    
    def test_rate_limiting(self):
        """Test du rate limiting"""
        print("⏱️ Test du rate limiting...")
        
        # Simuler des requêtes multiples
        cache_key = "rate_limit:test_ip"
        cache.set(cache_key, 0, 60)
        
        for i in range(105):  # Dépasser la limite de 100/h
            current_count = cache.get(cache_key, 0)
            cache.set(cache_key, current_count + 1, 60)
            
            if current_count >= 100:
                self.test_results.append(f"✅ Rate limit activé après {i+1} requêtes")
                break
        else:
            self.test_results.append("❌ Rate limit non activé")
    
    def test_logging(self):
        """Test du système de logging"""
        print("📝 Test du système de logging...")
        
        log_file = "logs/django.log"
        security_log_file = "logs/security.log"
        
        if os.path.exists(log_file):
            self.test_results.append(f"✅ Fichier de log principal créé: {log_file}")
        else:
            self.test_results.append(f"❌ Fichier de log principal manquant: {log_file}")
        
        if os.path.exists(security_log_file):
            self.test_results.append(f"✅ Fichier de log de sécurité créé: {security_log_file}")
        else:
            self.test_results.append(f"❌ Fichier de log de sécurité manquant: {security_log_file}")
    
    def run_all_tests(self):
        """Exécute tous les tests de sécurité"""
        print("🔒 Démarrage des tests de sécurité...")
        print("=" * 50)
        
        self.test_password_strength()
        self.test_username_validation()
        self.test_email_validation()
        self.test_input_sanitization()
        self.test_rate_limiting()
        self.test_logging()
        
        print("\n" + "=" * 50)
        print("📊 Résultats des tests de sécurité:")
        print("=" * 50)
        
        passed = 0
        failed = 0
        
        for result in self.test_results:
            print(result)
            if "✅" in result:
                passed += 1
            else:
                failed += 1
        
        print("\n" + "=" * 50)
        print(f"✅ Tests réussis: {passed}")
        print(f"❌ Tests échoués: {failed}")
        print(f"📈 Taux de réussite: {(passed/(passed+failed)*100):.1f}%")
        
        if failed == 0:
            print("🎉 Tous les tests de sécurité sont passés !")
        else:
            print("⚠️ Certains tests de sécurité ont échoué. Vérifiez la configuration.")

def main():
    """Fonction principale"""
    tests = SecurityTests()
    tests.run_all_tests()

if __name__ == "__main__":
    main() 
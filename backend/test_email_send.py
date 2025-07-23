#!/usr/bin/env python
"""
Script de test pour diagnostiquer l'envoi d'email
"""
import os
import sys
import django
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

def test_smtp_connection():
    """Test de connexion SMTP directe"""
    print("🔍 Test de connexion SMTP directe...")
    
    # Récupérer les paramètres email depuis les settings
    email_host = getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com')
    email_port = getattr(settings, 'EMAIL_PORT', 587)
    email_user = getattr(settings, 'EMAIL_HOST_USER', '')
    email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
    email_use_tls = getattr(settings, 'EMAIL_USE_TLS', True)
    
    print(f"📧 Configuration email détectée:")
    print(f"   HOST: {email_host}")
    print(f"   PORT: {email_port}")
    print(f"   USER: {email_user}")
    print(f"   PASSWORD: {'*' * len(email_password) if email_password else 'Non défini'}")
    print(f"   TLS: {email_use_tls}")
    
    try:
        # Test de connexion SMTP
        server = smtplib.SMTP(email_host, email_port)
        server.starttls()
        server.login(email_user, email_password)
        print("✅ Connexion SMTP réussie!")
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion SMTP: {e}")
        return False

def test_django_email():
    """Test d'envoi d'email via Django"""
    print("\n🔍 Test d'envoi d'email via Django...")
    
    try:
        # Test avec send_mail
        result = send_mail(
            subject='Test Email - Conformed',
            message='Ceci est un test d\'envoi d\'email depuis Django.',
            from_email=None,  # Utilise DEFAULT_FROM_EMAIL
            recipient_list=['mamadouwade944@gmail.com'],
            fail_silently=False,
        )
        print(f"✅ Email envoyé via Django! Résultat: {result}")
        return True
    except Exception as e:
        print(f"❌ Erreur d'envoi Django: {e}")
        return False

def test_email_message():
    """Test avec EmailMessage"""
    print("\n🔍 Test avec EmailMessage...")
    
    try:
        email = EmailMessage(
            subject='Test EmailMessage - Conformed',
            body='Ceci est un test avec EmailMessage.',
            from_email=None,
            to=['mamadouwade944@gmail.com'],
        )
        result = email.send(fail_silently=False)
        print(f"✅ EmailMessage envoyé! Résultat: {result}")
        return True
    except Exception as e:
        print(f"❌ Erreur EmailMessage: {e}")
        return False

def check_settings():
    """Vérifier la configuration des settings"""
    print("\n🔍 Vérification de la configuration...")
    
    print(f"EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'Non défini')}")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Non défini')}")
    print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Non défini')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Non défini')}")
    print(f"EMAIL_HOST_PASSWORD: {'Défini' if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else 'Non défini'}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Non défini')}")
    print(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Non défini')}")

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests d'email...")
    print("=" * 50)
    
    # Vérifier la configuration
    check_settings()
    
    # Tests
    smtp_ok = test_smtp_connection()
    django_ok = test_django_email()
    message_ok = test_email_message()
    
    print("\n" + "=" * 50)
    print("📊 Résumé des tests:")
    print(f"   SMTP direct: {'✅' if smtp_ok else '❌'}")
    print(f"   Django send_mail: {'✅' if django_ok else '❌'}")
    print(f"   EmailMessage: {'✅' if message_ok else '❌'}")
    
    if not smtp_ok:
        print("\n💡 Suggestions:")
        print("   1. Vérifiez que EMAIL_HOST_USER et EMAIL_HOST_PASSWORD sont corrects")
        print("   2. Assurez-vous d'utiliser un mot de passe d'application Gmail")
        print("   3. Vérifiez que la validation en deux étapes est activée sur Gmail")
        print("   4. Testez avec un autre compte Gmail")

if __name__ == '__main__':
    main() 
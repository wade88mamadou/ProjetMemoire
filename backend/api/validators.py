import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_password_strength(password):
    """
    Valide la force du mot de passe selon les standards de sécurité
    """
    if len(password) < 12:
        raise ValidationError(_('Le mot de passe doit contenir au moins 12 caractères.'))
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError(_('Le mot de passe doit contenir au moins une lettre majuscule.'))
    
    if not re.search(r'[a-z]', password):
        raise ValidationError(_('Le mot de passe doit contenir au moins une lettre minuscule.'))
    
    if not re.search(r'\d', password):
        raise ValidationError(_('Le mot de passe doit contenir au moins un chiffre.'))
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError(_('Le mot de passe doit contenir au moins un caractère spécial.'))
    
    # Vérifier les mots de passe communs
    common_passwords = [
        'password', '123456', 'qwerty', 'admin', 'letmein',
        'welcome', 'monkey', 'password123', 'admin123'
    ]
    
    if password.lower() in common_passwords:
        raise ValidationError(_('Ce mot de passe est trop commun. Veuillez choisir un mot de passe plus sécurisé.'))

def validate_username(username):
    """
    Valide le nom d'utilisateur
    """
    if len(username) < 3:
        raise ValidationError(_('Le nom d\'utilisateur doit contenir au moins 3 caractères.'))
    
    if len(username) > 30:
        raise ValidationError(_('Le nom d\'utilisateur ne peut pas dépasser 30 caractères.'))
    
    # Vérifier les caractères autorisés
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValidationError(_('Le nom d\'utilisateur ne peut contenir que des lettres, chiffres et underscores.'))
    
    # Vérifier les noms d'utilisateur réservés
    reserved_usernames = [
        'admin', 'administrator', 'root', 'system', 'test',
        'guest', 'anonymous', 'null', 'undefined'
    ]
    
    if username.lower() in reserved_usernames:
        raise ValidationError(_('Ce nom d\'utilisateur est réservé.'))

def validate_email(email):
    """
    Valide l'email
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        raise ValidationError(_('Veuillez entrer une adresse email valide.'))
    
    # Vérifier les domaines d'email temporaires
    temp_domains = [
        '10minutemail.com', 'guerrillamail.com', 'tempmail.org',
        'mailinator.com', 'yopmail.com', 'throwaway.email'
    ]
    
    domain = email.split('@')[1].lower()
    if domain in temp_domains:
        raise ValidationError(_('Les adresses email temporaires ne sont pas autorisées.'))

def validate_file_size(file):
    """
    Valide la taille du fichier
    """
    max_size = 10 * 1024 * 1024  # 10MB
    
    if file.size > max_size:
        raise ValidationError(_('Le fichier ne peut pas dépasser 10MB.'))

def validate_file_type(file):
    """
    Valide le type de fichier
    """
    allowed_types = [
        'text/csv',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ]
    
    if file.content_type not in allowed_types:
        raise ValidationError(_('Seuls les fichiers CSV et Excel sont autorisés.'))

def sanitize_input(text):
    """
    Nettoie les entrées utilisateur
    """
    if not text:
        return text
    
    # Supprimer les caractères dangereux
    dangerous_chars = ['<', '>', '"', "'", '&', 'script', 'javascript']
    
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def validate_phone_number(phone):
    """
    Valide le numéro de téléphone
    """
    # Format international
    phone_pattern = r'^\+?[1-9]\d{1,14}$'
    
    if not re.match(phone_pattern, phone):
        raise ValidationError(_('Veuillez entrer un numéro de téléphone valide.')) 
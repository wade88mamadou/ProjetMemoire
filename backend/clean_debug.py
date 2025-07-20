#!/usr/bin/env python3
"""
Script pour nettoyer les print() de debug et les remplacer par du logging
"""

import os
import re

def clean_debug_prints(file_path):
    """Nettoie les print() de debug dans un fichier"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remplacer les print() de debug par du logging
    patterns = [
        # Pattern pour les print() de debug
        (r'print\(f"=== DEBUG ([^"]+)"\)', r'logger.info(f"=== \1 ===")'),
        (r'print\(f"([^"]*DEBUG[^"]*)"\)', r'logger.info(f"\1")'),
        (r'print\(f"([^"]*)"\)  # Debug', r'logger.info(f"\1")'),
        (r'print\(f"([^"]*)"\)  # Debug', r'logger.info(f"\1")'),
        (r'print\(f"([^"]*)"\)', r'logger.info(f"\1")'),
        (r'print\("([^"]*)"\)', r'logger.info("\1")'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Ajouter l'import logging si nécessaire
    if 'logger.info(' in content and 'import logging' not in content:
        content = 'import logging\nlogger = logging.getLogger(__name__)\n\n' + content
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fichier nettoyé: {file_path}")

def main():
    """Fonction principale"""
    print("🧹 Nettoyage des print() de debug...")
    
    # Fichiers à nettoyer
    files_to_clean = [
        'api/views.py',
        'api/serializers.py',
        'api/models.py',
    ]
    
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            clean_debug_prints(file_path)
        else:
            print(f"⚠️  Fichier non trouvé: {file_path}")
    
    print("🎉 Nettoyage terminé!")

if __name__ == "__main__":
    main() 
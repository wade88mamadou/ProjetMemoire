# Migration vers PostgreSQL - ConformiMed

Ce guide explique comment migrer le projet ConformiMed de SQLite vers PostgreSQL.

## 🎯 Avantages de PostgreSQL

- **Performance** : Meilleure gestion des requêtes complexes
- **Sécurité** : Chiffrement des données et authentification robuste
- **Conformité** : Support des standards de sécurité médicale
- **Scalabilité** : Gestion de grandes quantités de données
- **Fonctionnalités avancées** : JSON, géolocalisation, etc.

## 📋 Prérequis

### 1. Installation de PostgreSQL

#### Windows
```bash
# Télécharger depuis https://www.postgresql.org/download/windows/
# Ou utiliser Chocolatey
choco install postgresql
```

#### macOS
```bash
# Avec Homebrew
brew install postgresql
brew services start postgresql
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Vérification de l'installation
```bash
psql --version
```

## 🚀 Configuration

### 1. Exécuter le script de configuration
```bash
cd backend
python setup_postgres.py
```

Ce script va :
- Créer l'utilisateur `conformimed_user`
- Créer la base de données `conformimed_db`
- Accorder les privilèges nécessaires

### 2. Configuration des variables d'environnement
Copiez le fichier `env.example` vers `.env` :
```bash
cp env.example .env
```

Modifiez les valeurs dans `.env` selon votre configuration.

## 🔄 Migration des données

### 1. Sauvegarder les données SQLite existantes
```bash
python migrate_to_postgres.py
```

### 2. Appliquer les migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Créer un superutilisateur
```bash
python manage.py createsuperuser
```

## 🧪 Test de la configuration

### 1. Tester la connexion
```bash
python manage.py dbshell
```

### 2. Vérifier les tables
```sql
\dt
SELECT * FROM api_utilisateur LIMIT 5;
\q
```

### 3. Démarrer le serveur
```bash
python manage.py runserver
```

## 🔧 Configuration avancée

### Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|---------|
| `DB_NAME` | Nom de la base de données | `conformimed_db` |
| `DB_USER` | Utilisateur PostgreSQL | `conformimed_user` |
| `DB_PASSWORD` | Mot de passe | `conformimed_password` |
| `DB_HOST` | Hôte PostgreSQL | `localhost` |
| `DB_PORT` | Port PostgreSQL | `5432` |

### Configuration de production

Pour la production, utilisez des variables d'environnement sécurisées :

```bash
export DB_NAME="conformimed_prod"
export DB_USER="conformimed_prod_user"
export DB_PASSWORD="mot_de_passe_securise"
export DB_HOST="votre-serveur-postgresql.com"
export DB_PORT="5432"
```

## 🔒 Sécurité

### 1. Chiffrement SSL
En production, activez SSL :
```python
'OPTIONS': {
    'sslmode': 'require',
}
```

### 2. Pool de connexions
Pour améliorer les performances :
```python
'OPTIONS': {
    'MAX_CONNS': 20,
    'MIN_CONNS': 5,
}
```

### 3. Sauvegarde automatique
Configurez des sauvegardes régulières :
```bash
# Script de sauvegarde
pg_dump -h localhost -U conformimed_user -d conformimed_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

## 🐛 Dépannage

### Erreur de connexion
```bash
# Vérifier que PostgreSQL est démarré
sudo systemctl status postgresql

# Vérifier les logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### Erreur de permissions
```sql
-- Se connecter en tant que postgres
sudo -u postgres psql

-- Accorder les privilèges
GRANT ALL PRIVILEGES ON DATABASE conformimed_db TO conformimed_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO conformimed_user;
```

### Erreur de migration
```bash
# Réinitialiser les migrations
python manage.py migrate --fake-initial

# Ou forcer la migration
python manage.py migrate --run-syncdb
```

## 📊 Monitoring

### Vérifier les performances
```sql
-- Requêtes lentes
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Utilisation de l'espace
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## ✅ Checklist de migration

- [ ] PostgreSQL installé et configuré
- [ ] Script de configuration exécuté
- [ ] Variables d'environnement configurées
- [ ] Données SQLite sauvegardées
- [ ] Migrations appliquées
- [ ] Superutilisateur créé
- [ ] Tests de connexion réussis
- [ ] Application fonctionnelle
- [ ] Sauvegarde configurée

## 🆘 Support

En cas de problème :
1. Vérifiez les logs PostgreSQL
2. Consultez la documentation officielle
3. Testez la connexion manuellement
4. Vérifiez les permissions utilisateur 
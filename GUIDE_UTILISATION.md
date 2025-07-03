# Guide d'Utilisation - Projet Django-React

## 🎉 Félicitations ! Votre projet est prêt

Vous avez maintenant un projet complet avec :
- **Backend Django** avec API REST (port 8000)
- **Frontend React** avec interface moderne (port 3000)
- **Communication** entre les deux serveurs configurée

## 🚀 Démarrage Rapide

### Option 1 : Script automatique (Recommandé)
Double-cliquez sur `start-servers.bat` (Windows) ou exécutez `./start-servers.sh` (Linux/Mac)

### Option 2 : Démarrage manuel

#### Backend Django
```bash
cd backend
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac

python manage.py runserver
```

#### Frontend React
```bash
cd frontend
npm start
```

## 🌐 Accès aux Applications

- **Frontend React** : http://localhost:3000
- **Backend API** : http://localhost:8000/api/
- **Admin Django** : http://localhost:8000/admin/
  - Utilisateur : `admin`
  - Mot de passe : `admin123`

## 📋 Fonctionnalités

### Frontend React
- ✅ Interface moderne et responsive
- ✅ Formulaire d'ajout d'éléments
- ✅ Liste des éléments avec actions
- ✅ Activation/désactivation d'éléments
- ✅ Suppression d'éléments
- ✅ Gestion des erreurs
- ✅ Design adaptatif (mobile/desktop)

### Backend Django
- ✅ API REST complète
- ✅ Modèle Item avec CRUD
- ✅ Sérialisation automatique
- ✅ Interface d'administration
- ✅ Configuration CORS pour React
- ✅ Pagination automatique

## 🔧 Structure du Projet

```
Projet/
├── backend/                 # Application Django
│   ├── backend_project/     # Configuration Django
│   ├── api/                # Application API
│   ├── venv/               # Environnement virtuel
│   └── manage.py           # Script de gestion Django
├── frontend/               # Application React
│   ├── src/
│   │   ├── components/     # Composants React
│   │   ├── App.js          # Composant principal
│   │   └── App.css         # Styles principaux
│   └── package.json        # Dépendances Node.js
├── requirements.txt        # Dépendances Python
├── start-servers.bat       # Script de démarrage Windows
├── start-servers.sh        # Script de démarrage Linux/Mac
└── README.md              # Documentation principale
```

## 🛠️ API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/` | Page d'accueil de l'API |
| GET | `/api/items/` | Liste des éléments |
| POST | `/api/items/` | Créer un élément |
| GET | `/api/items/{id}/` | Détails d'un élément |
| PUT | `/api/items/{id}/` | Modifier un élément |
| PATCH | `/api/items/{id}/` | Modifier partiellement |
| DELETE | `/api/items/{id}/` | Supprimer un élément |

## 📝 Modèle de Données

### Item
- `id` : Identifiant unique (auto-généré)
- `name` : Nom de l'élément (obligatoire)
- `description` : Description (optionnelle)
- `created_at` : Date de création (auto-générée)
- `updated_at` : Date de modification (auto-générée)
- `is_active` : Statut actif/inactif (booléen)

## 🎨 Personnalisation

### Ajouter de nouveaux champs
1. Modifiez `backend/api/models.py`
2. Créez une migration : `python manage.py makemigrations`
3. Appliquez la migration : `python manage.py migrate`
4. Mettez à jour le sérialiseur dans `backend/api/serializers.py`
5. Modifiez les composants React dans `frontend/src/components/`

### Modifier le design
- Styles principaux : `frontend/src/App.css`
- Styles des composants : `frontend/src/components/*.css`

## 🔍 Dépannage

### Problème de connexion entre frontend et backend
- Vérifiez que les deux serveurs sont démarrés
- Vérifiez les ports (3000 pour React, 8000 pour Django)
- Vérifiez la configuration CORS dans `backend/backend_project/settings.py`

### Erreur de modules React
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Erreur de migrations Django
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### Problème d'environnement virtuel
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
pip install -r ../requirements.txt
```

## 🚀 Déploiement

### Backend (Production)
- Utilisez PostgreSQL au lieu de SQLite
- Configurez `DEBUG = False`
- Utilisez un serveur WSGI comme Gunicorn
- Configurez un reverse proxy (Nginx)

### Frontend (Production)
```bash
cd frontend
npm run build
```
Les fichiers de production seront dans `frontend/build/`

## 📚 Ressources Utiles

- [Documentation Django](https://docs.djangoproject.com/)
- [Documentation Django REST Framework](https://www.django-rest-framework.org/)
- [Documentation React](https://reactjs.org/docs/)
- [Documentation Axios](https://axios-http.com/)

## 🤝 Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs dans les terminaux
2. Consultez la documentation des frameworks
3. Vérifiez la configuration CORS
4. Assurez-vous que tous les ports sont disponibles

---

**Bon développement ! 🚀** 
<<<<<<< HEAD
# Projet Django-React

Ce projet est composé d'un backend Django et d'un frontend React qui communiquent via une API REST.

## Structure du projet

```
Projet/
├── backend/          # Application Django
├── frontend/         # Application React
├── requirements.txt  # Dépendances Python
└── README.md        # Ce fichier
```

## Installation et démarrage

### Backend Django

1. Créer un environnement virtuel :
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

2. Installer les dépendances :
```bash
pip install -r ../requirements.txt
```

3. Appliquer les migrations :
```bash
python manage.py migrate
```

4. Créer un superutilisateur :
```bash
python manage.py createsuperuser
```

5. Démarrer le serveur :
```bash
python manage.py runserver
```

Le backend sera accessible sur http://localhost:8000

### Frontend React

1. Installer les dépendances :
```bash
cd frontend
npm install
```

2. Démarrer le serveur de développement :
```bash
npm start
```

Le frontend sera accessible sur http://localhost:3000

## API Endpoints

- `GET /api/items/` - Liste des éléments
- `POST /api/items/` - Créer un élément
- `GET /api/items/{id}/` - Détails d'un élément
- `PUT /api/items/{id}/` - Modifier un élément
- `DELETE /api/items/{id}/` - Supprimer un élément

## Configuration CORS

Le backend est configuré pour accepter les requêtes du frontend React (localhost:3000). 
=======
# Dashboard
DashboardDjangoReact
>>>>>>> 68c20743f62c9d2e25ba6f17164bfcfa2046a503

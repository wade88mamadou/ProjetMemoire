#!/bin/bash

echo "========================================"
echo "  Démarrage du projet Django-React"
echo "========================================"
echo

echo "1. Démarrage du serveur Django (Backend)..."
cd backend
source venv/bin/activate
python manage.py runserver &
DJANGO_PID=$!

echo "2. Démarrage du serveur React (Frontend)..."
cd ../frontend
npm start &
REACT_PID=$!

echo
echo "========================================"
echo "  Serveurs démarrés !"
echo "========================================"
echo "Backend Django: http://localhost:8000"
echo "Frontend React: http://localhost:3000"
echo "Admin Django: http://localhost:8000/admin"
echo "========================================"
echo
echo "Appuyez sur Ctrl+C pour arrêter les serveurs"
echo

# Fonction pour arrêter les serveurs proprement
cleanup() {
    echo "Arrêt des serveurs..."
    kill $DJANGO_PID
    kill $REACT_PID
    exit
}

# Capturer Ctrl+C
trap cleanup SIGINT

# Attendre que les processus se terminent
wait 
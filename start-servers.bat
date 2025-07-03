@echo off
echo ========================================
echo   Demarrage du projet Django-React
echo ========================================
echo.

echo 1. Demarrage du serveur Django (Backend)...
cd backend
start "Django Backend" cmd /k "venv\Scripts\activate && python manage.py runserver"

echo 2. Demarrage du serveur React (Frontend)...
cd ..\frontend
start "React Frontend" cmd /k "npm start"

echo.
echo ========================================
echo   Serveurs demarres !
echo ========================================
echo Backend Django: http://localhost:8000
echo Frontend React: http://localhost:3000
echo Admin Django: http://localhost:8000/admin
echo ========================================
echo.
pause 
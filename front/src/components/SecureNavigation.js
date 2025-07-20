import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const SecureNavigation = () => {
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Fonction pour vérifier si une route est protégée
    const isProtectedRoute = (pathname) => {
      const protectedRoutes = [
        '/dashboard',
        '/admin',
        '/medecin',
        '/user',
        '/import-data',
        '/alertes-critiques',
        '/config-alertes-securite',
        '/rapport-audit'
      ];
      return protectedRoutes.some(route => pathname.startsWith(route));
    };

    // Fonction pour vérifier si l'utilisateur a accès à la route actuelle
    const hasAccessToRoute = (pathname, userRole) => {
      if (!userRole) return false;
      
      // Routes publiques - toujours accessibles
      const publicRoutes = ['/', '/contact', '/about', '/login', '/simple-reset', '/unauthorized'];
      if (publicRoutes.includes(pathname)) return true;
      
      // Routes admin
      if (pathname.startsWith('/admin') && userRole === 'ADMIN') return true;
      
      // Routes médecin
      if (pathname.startsWith('/medecin') && (userRole === 'MEDECIN' || userRole === 'ADMIN')) return true;
      
      // Routes utilisateur simple
      if (pathname.startsWith('/user') && (userRole === 'user_simple' || userRole === 'MEDECIN' || userRole === 'ADMIN')) return true;
      
      // Routes partagées
      if (pathname === '/import-data' && (userRole === 'MEDECIN' || userRole === 'ADMIN')) return true;
      
      return false;
    };

    // Fonction pour rediriger vers le dashboard approprié
    const redirectToAppropriateDashboard = () => {
      if (!user) return;
      
      switch (user.role) {
        case 'ADMIN':
          navigate('/admin/dashboard', { replace: true });
          break;
        case 'MEDECIN':
          navigate('/medecin/dashboard', { replace: true });
          break;
        case 'user_simple':
          navigate('/user/dashboard', { replace: true });
          break;
        default:
          navigate('/dashboard', { replace: true });
      }
    };

    // Gérer la navigation intelligemment
    if (isAuthenticated && location.pathname === '/login') {
      // Si l'utilisateur est connecté et essaie d'accéder à login, rediriger vers son dashboard
      redirectToAppropriateDashboard();
    } else if (!isAuthenticated && isProtectedRoute(location.pathname)) {
      // Si l'utilisateur n'est pas connecté et essaie d'accéder à une page protégée
      navigate('/login', { replace: true });
    } else if (isAuthenticated && user && !hasAccessToRoute(location.pathname, user.role)) {
      // Si l'utilisateur est connecté mais n'a pas accès à cette route
      redirectToAppropriateDashboard();
    }
    // Si l'utilisateur est connecté et a accès à la route, ne rien faire (permettre la navigation normale)
    
  }, [isAuthenticated, user, location.pathname, navigate]);

  // Ce composant ne rend rien visuellement
  return null;
};

export default SecureNavigation; 
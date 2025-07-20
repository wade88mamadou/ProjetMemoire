import React, { useEffect } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = ({ children, requiredRole = null }) => {
  const { isAuthenticated, loading, hasRole, user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  // Vérification supplémentaire pour empêcher l'accès direct
  useEffect(() => {
    // Si l'utilisateur n'est pas authentifié et qu'on n'est pas en train de charger
    if (!loading && !isAuthenticated) {
      // Nettoyer le localStorage au cas où il y aurait des données corrompues
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('role');
      
      // Rediriger vers login seulement si on n'y est pas déjà
      if (location.pathname !== '/login') {
        navigate('/login', { state: { from: location }, replace: true });
      }
    }
  }, [loading, isAuthenticated, location, navigate]);

  // Afficher un loader pendant la vérification de l'authentification
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Vérification de l'authentification...</p>
        </div>
      </div>
    );
  }

  // Si l'utilisateur n'est pas connecté, rediriger vers la page de connexion
  if (!isAuthenticated || !user) {
    console.log('Utilisateur non authentifié, redirection vers /login');
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Si un rôle spécifique est requis et que l'utilisateur ne l'a pas
  if (requiredRole && !hasRole(requiredRole)) {
    console.log(`Rôle requis: ${requiredRole}, rôle utilisateur: ${user.role}`);
    // Rediriger vers le dashboard approprié selon le rôle de l'utilisateur
    return <Navigate to="/unauthorized" replace />;
  }

  // Si tout est OK, afficher le contenu protégé
  return children;
};

export default ProtectedRoute; 
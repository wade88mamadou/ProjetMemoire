import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const DashboardRedirect = () => {
  const { user, loading, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading) {
      // Si l'utilisateur n'est pas authentifié, rediriger vers la page de connexion
      if (!isAuthenticated || !user) {
        navigate('/login');
        return;
      }

      // Redirection selon le rôle
      switch (user.role) {
        case 'ADMIN':
          navigate('/admin/dashboard');
          break;
        case 'MEDECIN':
          navigate('/medecin/dashboard');
          break;
        case 'user_simple':
          navigate('/user/dashboard');
          break;
        default:
          navigate('/user/dashboard');
      }
    }
  }, [user, loading, isAuthenticated, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Redirection en cours...</p>
      </div>
    </div>
  );
};

export default DashboardRedirect; 
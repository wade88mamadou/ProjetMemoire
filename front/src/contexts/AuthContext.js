import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Vérifier si l'utilisateur est connecté au chargement de l'app
  useEffect(() => {
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    
    if (token && savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
        
        // Vérifier si le token est toujours valide
        authService.getUserDetails()
          .then(response => {
            setUser(response.data);
            localStorage.setItem('user', JSON.stringify(response.data));
            setLoading(false);
          })
          .catch((error) => {
            console.error('Token invalide:', error);
            // Token invalide, déconnecter l'utilisateur
            logout();
            setLoading(false);
          });
      } catch (error) {
        console.error('Erreur lors du parsing des données utilisateur:', error);
        logout();
        setLoading(false);
      }
    } else {
      // Pas de token ou d'utilisateur, s'assurer que l'état est propre
      setUser(null);
      setLoading(false);
    }
  }, []);

  // Fonction de connexion
  const login = async (credentials) => {
    try {
      setError(null);
      const response = await authService.login(credentials);
      
      if (response.data.success) {
        const { token, user: userData } = response.data;
        
        // Stocker le token et les données utilisateur
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(userData));
        localStorage.setItem('role', userData.role);
        
        setUser(userData);
        return { success: true, user: userData };
      } else {
        setError('Erreur de connexion');
        return { success: false, error: 'Erreur de connexion' };
      }
    } catch (error) {
      // Gestion spéciale pour les comptes désactivés
      if (error.response?.status === 403 && error.response?.data?.code === 'ACCOUNT_DISABLED') {
        const errorData = error.response.data;
        const inactiveError = {
          type: 'account_disabled',
          title: errorData.error,
          message: errorData.message,
          code: errorData.code
        };
        setError(inactiveError);
        return { 
          success: false, 
          error: errorData.message,
          errorType: 'account_disabled'
        };
      }
      
      // Toujours transmettre une string si ce n'est pas un compte inactif
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.error || 
                          'Erreur de connexion';
      setError(typeof errorMessage === 'string' ? errorMessage : 'Erreur de connexion');
      return { success: false, error: errorMessage };
    }
  };

  // Fonction de déconnexion
  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        await authService.logout(refreshToken);
      }
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error);
    } finally {
      // Nettoyer le localStorage
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      localStorage.removeItem('role');
      
      // Nettoyer l'état
      setUser(null);
      setError(null);
    }
  };

  // Fonction pour changer le mot de passe
  const changePassword = async (passwords) => {
    try {
      setError(null);
      await authService.changePassword(passwords);
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Erreur lors du changement de mot de passe';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Fonction pour vérifier les permissions selon le rôle
  const hasRole = (requiredRole) => {
    if (!user) return false;
    
    // Logique de permissions selon les rôles du backend
    switch (requiredRole) {
      case 'ADMIN':
        return user.role === 'ADMIN' || user.is_superuser;
      case 'MEDECIN':
        return user.role === 'MEDECIN' || user.role === 'ADMIN' || user.is_superuser;
      case 'user_simple':
        return user.role === 'user_simple' || user.role === 'MEDECIN' || user.role === 'ADMIN' || user.is_superuser;
      default:
        return false;
    }
  };

  // Fonction pour vérifier si l'utilisateur est admin
  const isAdmin = () => {
    return user && (user.role === 'ADMIN' || user.is_superuser);
  };

  // Fonction pour vérifier si l'utilisateur est médecin
  const isMedecin = () => {
    return user && (user.role === 'MEDECIN' || user.role === 'ADMIN' || user.is_superuser);
  };

  const value = {
    user,
    loading,
    error,
    login,
    logout,
    changePassword,
    hasRole,
    isAdmin,
    isMedecin,
    isAuthenticated: !!user,
    mustChangePassword: user?.must_change_password || false,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 
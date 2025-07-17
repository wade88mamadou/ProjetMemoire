import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showInactiveModal, setShowInactiveModal] = useState(false);
  
  const { login, error } = useAuth();
  const navigate = useNavigate();

  // Ajout du log pour debug
  console.log('Erreur reçue dans LoginPage:', error);

  // Afficher la modal si erreur inactif
  React.useEffect(() => {
    if (error && typeof error === 'object' && error.type === 'account_disabled') {
      setShowInactiveModal(true);
    }
  }, [error]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const result = await login(formData);
      
      if (result.success) {
        // Redirection selon le rôle
        const role = result.user.role;
        console.log('Rôle de l\'utilisateur:', role);
        console.log('Données utilisateur complètes:', result.user);
        
        switch (role) {
          case 'admin':
            console.log('Redirection vers dashboard admin');
            navigate('/admin/dashboard');
            break;
          case 'medecin':
            console.log('Redirection vers dashboard médecin');
            navigate('/medecin/dashboard');
            break;
          case 'user_simple':
            console.log('Redirection vers dashboard utilisateur');
            navigate('/user/dashboard');
            break;
          default:
            console.log('Rôle non reconnu, redirection par défaut');
            navigate('/dashboard');
        }
      }
    } catch (err) {
      console.error('Erreur de connexion:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Connexion
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Accédez à votre espace personnel
          </p>
        </div>

        {/* Formulaire */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="bg-white py-8 px-6 shadow-lg rounded-lg">
            {/* Message d'erreur */}
            {error && !(typeof error === 'object' && error.type === 'account_disabled') && (
              <div className={`mb-4 px-4 py-3 rounded-md bg-red-50 border border-red-200 text-red-700`}>
                <div className="flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  {typeof error === 'string' ? error : 'Erreur de connexion'}
                </div>
              </div>
            )}

            {/* Nom d'utilisateur */}
            <div className="mb-4">
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                Nom d'utilisateur
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                value={formData.username}
                onChange={handleChange}
                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Entrez votre nom d'utilisateur"
              />
            </div>

            {/* Mot de passe */}
            <div className="mb-6">
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Mot de passe
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="appearance-none relative block w-full px-3 py-2 pr-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                  placeholder="Entrez votre mot de passe"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                    </svg>
                  ) : (
                    <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {/* Bouton de connexion */}
            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
              >
                {isLoading ? (
                  <div className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Connexion en cours...
                  </div>
                ) : (
                  'Se connecter'
                )}
              </button>
            </div>

            {/* Liens utiles */}
            <div className="mt-6 text-center">
              <Link
                to="/"
                className="text-sm text-blue-600 hover:text-blue-500 transition-colors duration-200"
              >
                ← Retour à l'accueil
              </Link>
            </div>
          </div>
        </form>

        {/* Informations sur les rôles */}
        <div className="bg-white p-4 rounded-lg shadow-sm">
          <h3 className="text-sm font-medium text-gray-900 mb-2">Rôles disponibles :</h3>
          <div className="text-xs text-gray-600 space-y-1">
            <div className="flex items-center">
              <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
              <strong>Administrateur :</strong> Accès complet à toutes les fonctionnalités
            </div>
            <div className="flex items-center">
              <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
              <strong>Médecin :</strong> Gestion des patients et dossiers médicaux
            </div>
            <div className="flex items-center">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
              <strong>Utilisateur simple :</strong> Consultation des informations de base
            </div>
          </div>
        </div>
      </div>
      {showInactiveModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
          <div className="bg-white p-6 rounded shadow-lg max-w-sm w-full">
            <div className="flex items-center mb-3">
              <svg className="w-6 h-6 text-orange-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <h2 className="text-lg font-bold text-orange-700">Impossible de te connecter, vous êtes inactif</h2>
            </div>
            <p className="mb-4 text-gray-700">Votre compte a été désactivé par l'administrateur.<br/>Veuillez contacter votre administrateur pour réactiver votre compte.</p>
            <button
              onClick={() => setShowInactiveModal(false)}
              className="mt-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-medium w-full"
            >
              Fermer
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default LoginPage; 
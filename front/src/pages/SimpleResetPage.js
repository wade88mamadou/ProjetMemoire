import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/api';

const SimpleResetPage = () => {
  // État pour l'étape du formulaire
  const [step, setStep] = useState(1);
  // Formulaire étape 1
  const [verifyData, setVerifyData] = useState({ username: '', email: '' });
  // Formulaire étape 2
  const [passwordData, setPasswordData] = useState({ new_password: '', confirm_password: '' });
  // Token temporaire
  const [resetToken, setResetToken] = useState('');
  // UI states
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const navigate = useNavigate();

  // Gestion du formulaire étape 1
  const handleVerifyChange = (e) => {
    const { name, value } = e.target;
    setVerifyData(prev => ({ ...prev, [name]: value }));
  };

  // Gestion du formulaire étape 2
  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({ ...prev, [name]: value }));
  };

  // Soumission étape 1 : vérification username + email
  const handleVerifySubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      const res = await authService.verifyUsername({ username: verifyData.username, email: verifyData.email });
      setResetToken(res.token);
      setStep(2);
    } catch (err) {
      setError(err.response?.data?.detail || "Nom d'utilisateur ou email invalide.");
    } finally {
      setIsLoading(false);
    }
  };

  // Soumission étape 2 : nouveau mot de passe
  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    if (passwordData.new_password !== passwordData.confirm_password) {
      setError('Les mots de passe ne correspondent pas.');
      return;
    }
    if (passwordData.new_password.length < 8) {
      setError('Le mot de passe doit contenir au moins 8 caractères.');
      return;
    }
    setIsLoading(true);
    setError('');
    try {
      await authService.simplePasswordResetWithToken({
        token: resetToken,
        new_password: passwordData.new_password,
        confirm_password: passwordData.confirm_password
      });
      setSuccess(true);
      setPasswordData({ new_password: '', confirm_password: '' });
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la réinitialisation.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-blue-600 rounded-full flex items-center justify-center mb-4">
            <span className="text-2xl text-white font-bold">🔑</span>
          </div>
          <h2 className="text-3xl font-extrabold text-gray-900 mb-2">
            Réinitialisation
          </h2>
          <p className="text-gray-600">
            {step === 1 ? "Entrez votre nom d'utilisateur et votre email pour vérifier votre identité" : "Définissez un nouveau mot de passe"}
          </p>
        </div>
        <div className="bg-white py-8 px-6 shadow-xl rounded-lg">
          {success ? (
            <div className="text-center">
              <div className="mx-auto h-12 w-12 bg-green-100 rounded-full flex items-center justify-center mb-4">
                <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Mot de passe mis à jour !
              </h3>
              <p className="text-gray-600 mb-6">
                Votre mot de passe a été réinitialisé avec succès.
              </p>
              <p className="text-sm text-gray-500">
                Redirection vers la page de connexion...
              </p>
            </div>
          ) : (
            step === 1 ? (
              <form onSubmit={handleVerifySubmit} className="space-y-6">
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-md p-4">
                    <div className="flex">
                      <div className="flex-shrink-0">
                        <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <div className="ml-3">
                        <p className="text-sm text-red-800">{error}</p>
                      </div>
                    </div>
                  </div>
                )}
                <div>
                  <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                    Nom d'utilisateur
                  </label>
                  <input
                    id="username"
                    name="username"
                    type="text"
                    autoComplete="username"
                    required
                    value={verifyData.username}
                    onChange={handleVerifyChange}
                    className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                    placeholder="Entrez votre nom d'utilisateur"
                  />
                </div>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Email associé
                  </label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={verifyData.email}
                    onChange={handleVerifyChange}
                    className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                    placeholder="Entrez votre email associé"
                  />
                </div>
                <div>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {isLoading ? (
                      <div className="flex items-center">
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Vérification...
                      </div>
                    ) : (
                      'Vérifier'
                    )}
                  </button>
                </div>
                <div className="text-center">
                  <Link
                    to="/login"
                    className="text-sm text-blue-600 hover:text-blue-500 transition-colors"
                  >
                    ← Retour à la connexion
                  </Link>
                </div>
              </form>
            ) : (
              <form onSubmit={handlePasswordSubmit} className="space-y-6">
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-md p-4">
                    <div className="flex">
                      <div className="flex-shrink-0">
                        <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <div className="ml-3">
                        <p className="text-sm text-red-800">{error}</p>
                      </div>
                    </div>
                  </div>
                )}
                <div>
                  <label htmlFor="new_password" className="block text-sm font-medium text-gray-700 mb-2">
                    Nouveau mot de passe
                  </label>
                  <div className="relative">
                    <input
                      id="new_password"
                      name="new_password"
                      type={showPassword ? "text" : "password"}
                      autoComplete="new-password"
                      required
                      value={passwordData.new_password}
                      onChange={handlePasswordChange}
                      className="appearance-none relative block w-full px-3 py-2 pr-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                      placeholder="Votre nouveau mot de passe"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    >
                      {showPassword ? (
                        <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                        </svg>
                      ) : (
                        <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      )}
                    </button>
                  </div>
                  <p className="mt-1 text-xs text-gray-500">
                    Le mot de passe doit contenir au moins 8 caractères
                  </p>
                </div>
                <div>
                  <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700 mb-2">
                    Confirmer le mot de passe
                  </label>
                  <div className="relative">
                    <input
                      id="confirm_password"
                      name="confirm_password"
                      type={showConfirmPassword ? "text" : "password"}
                      autoComplete="new-password"
                      required
                      value={passwordData.confirm_password}
                      onChange={handlePasswordChange}
                      className="appearance-none relative block w-full px-3 py-2 pr-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                      placeholder="Confirmez votre nouveau mot de passe"
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    >
                      {showConfirmPassword ? (
                        <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                        </svg>
                      ) : (
                        <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      )}
                    </button>
                  </div>
                </div>
                <div>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {isLoading ? (
                      <div className="flex items-center">
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Mise à jour en cours...
                      </div>
                    ) : (
                      'Réinitialiser le mot de passe'
                    )}
                  </button>
                </div>
                <div className="text-center">
                  <Link
                    to="/login"
                    className="text-sm text-blue-600 hover:text-blue-500 transition-colors"
                  >
                    ← Retour à la connexion
                  </Link>
                </div>
              </form>
            )
          )}
        </div>
        <div className="text-center">
          <p className="text-xs text-gray-500">
            ⚠️ Cette méthode est réservée aux administrateurs et au développement
          </p>
        </div>
      </div>
    </div>
  );
};

export default SimpleResetPage; 
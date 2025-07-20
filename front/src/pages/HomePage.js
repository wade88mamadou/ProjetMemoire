import React from 'react';
import { Link } from 'react-router-dom';
import LogoHeader from '../components/LogoHeader';
import Footer from '../components/Footer';

const HomePage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-6 w-full">
            {/* Bloc gauche : Logo + Conformed */}
            <div className="flex items-center gap-2 flex-shrink-0 pl-0">
              <LogoHeader />
              <span className="ml-2 text-2xl font-bold text-blue-700 tracking-wide animate-fade-in">Conformed</span>
            </div>

            {/* Bloc centre : Liens de navigation */}
            <nav className="flex-1 flex justify-center space-x-8">
              <Link
                to="/"
                className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors duration-200"
              >
                Accueil
              </Link>
              <Link
                to="/contact"
                className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors duration-200"
              >
                Contact
              </Link>
              <Link
                to="/about"
                className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors duration-200"
              >
                À propos
              </Link>
            </nav>

            {/* Bloc droit : Connexion */}
            <div className="flex-shrink-0 ml-auto pr-4">
              <Link
                to="/login"
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md text-sm font-semibold transition-all duration-300 shadow-sm hover:shadow-lg transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-400"
              >
                Connexion
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h2 className="text-4xl font-extrabold text-gray-900 sm:text-5xl md:text-6xl animate-fade-in">
            <span className="block animate-slide-in-left">Gestion Médicale</span>
            <span className="block text-blue-600 animate-slide-in-right">Intelligente</span>
          </h2>
          <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl animate-fade-in-up">
            Plateforme complète de gestion des dossiers médicaux, patients et rapports pour les professionnels de santé.
          </p>
          <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8 animate-bounce-in">
            <div className="rounded-md shadow">
              <Link
                to="/login"
                className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 md:py-4 md:text-lg md:px-10 transition-all duration-300 transform hover:scale-105 hover:shadow-lg"
              >
                Commencer
              </Link>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="py-12 bg-white rounded-lg shadow-lg">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="lg:text-center">
              <h3 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
                Fonctionnalités Principales
              </h3>
              <p className="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
                Une solution complète pour la gestion médicale moderne
              </p>
            </div>

            <div className="mt-10">
              <div className="grid grid-cols-1 gap-10 sm:grid-cols-2 lg:grid-cols-3">
                {/* Feature 1 */}
                <div className="text-center transform hover:scale-105 transition-all duration-300 hover:shadow-lg rounded-lg p-4">
                  <div className="flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white mx-auto hover:bg-blue-600 transition-colors duration-200">
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <h4 className="mt-4 text-lg font-medium text-gray-900">Gestion des Patients</h4>
                  <p className="mt-2 text-base text-gray-500">
                    Enregistrement et suivi complet des informations patients avec historique médical.
                  </p>
                </div>

                {/* Feature 2 */}
                <div className="text-center transform hover:scale-105 transition-all duration-300 hover:shadow-lg rounded-lg p-4">
                  <div className="flex items-center justify-center h-12 w-12 rounded-md bg-green-500 text-white mx-auto hover:bg-green-600 transition-colors duration-200">
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <h4 className="mt-4 text-lg font-medium text-gray-900">Dossiers Médicaux</h4>
                  <p className="mt-2 text-base text-gray-500">
                    Dossiers médicaux numériques sécurisés avec accès contrôlé par rôle.
                  </p>
                </div>

                {/* Feature 3 */}
                <div className="text-center transform hover:scale-105 transition-all duration-300 hover:shadow-lg rounded-lg p-4">
                  <div className="flex items-center justify-center h-12 w-12 rounded-md bg-red-500 text-white mx-auto hover:bg-red-600 transition-colors duration-200">
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                  </div>
                  <h4 className="mt-4 text-lg font-medium text-gray-900">Système d'Alertes</h4>
                  <p className="mt-2 text-base text-gray-500">
                    Notifications automatiques pour les cas urgents et les rappels importants.
                  </p>
                </div>

                {/* Feature 4 */}
                <div className="text-center transform hover:scale-105 transition-all duration-300 hover:shadow-lg rounded-lg p-4">
                  <div className="flex items-center justify-center h-12 w-12 rounded-md bg-purple-500 text-white mx-auto hover:bg-purple-600 transition-colors duration-200">
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <h4 className="mt-4 text-lg font-medium text-gray-900">Rapports & Analyses</h4>
                  <p className="mt-2 text-base text-gray-500">
                    Génération de rapports détaillés et analyses statistiques pour le suivi médical.
                  </p>
                </div>

                {/* Feature 5 */}
                <div className="text-center transform hover:scale-105 transition-all duration-300 hover:shadow-lg rounded-lg p-4">
                  <div className="flex items-center justify-center h-12 w-12 rounded-md bg-yellow-500 text-white mx-auto hover:bg-yellow-600 transition-colors duration-200">
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </div>
                  <h4 className="mt-4 text-lg font-medium text-gray-900">Sécurité Avancée</h4>
                  <p className="mt-2 text-base text-gray-500">
                    Authentification sécurisée et gestion des permissions par rôle utilisateur.
                  </p>
                </div>

                {/* Feature 6 */}
                <div className="text-center transform hover:scale-105 transition-all duration-300 hover:shadow-lg rounded-lg p-4">
                  <div className="flex items-center justify-center h-12 w-12 rounded-md bg-indigo-500 text-white mx-auto hover:bg-indigo-600 transition-colors duration-200">
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <h4 className="mt-4 text-lg font-medium text-gray-900">Interface Moderne</h4>
                  <p className="mt-2 text-base text-gray-500">
                    Interface utilisateur intuitive et responsive pour une expérience optimale.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-16 text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            Prêt à commencer ?
          </h3>
          <p className="text-lg text-gray-600 mb-8">
            Rejoignez notre plateforme et améliorez votre gestion médicale dès aujourd'hui.
          </p>
          <Link
            to="/login"
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-all duration-300 transform hover:scale-105 hover:shadow-lg"
          >
            Se connecter maintenant
          </Link>
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default HomePage; 
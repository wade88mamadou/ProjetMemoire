import React from 'react';
import { Link } from 'react-router-dom';
import LogoHeader from '../components/LogoHeader';
import Footer from '../components/Footer';

const AboutPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
          <div className="flex items-center gap-2">
              <LogoHeader />
              <span className="ml-2 text-2xl font-bold text-blue-700 tracking-wide animate-fade-in">Conformed</span>
            </div>
            
            {/* Navigation Links */}
            <nav className="hidden md:flex space-x-8">
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
                className="text-blue-600 px-3 py-2 text-sm font-medium border-b-2 border-blue-600"
              >
                À propos
              </Link>
            </nav>
            
            <div className="flex space-x-4">
              <Link
                to="/login"
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200"
              >
                Connexion
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl">
            À propos de nous
          </h1>
          <p className="mt-4 text-xl text-gray-600">
            Découvrez notre mission et notre équipe dédiée à l'innovation médicale
          </p>
        </div>

        {/* Notre Mission */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-12">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Notre Mission</h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Nous développons des solutions technologiques innovantes pour moderniser 
              la gestion médicale et améliorer la qualité des soins. Notre plateforme 
              vise à simplifier le travail des professionnels de santé tout en garantissant 
              la sécurité et la confidentialité des données médicales.
            </p>
          </div>
        </div>

        {/* Nos Valeurs */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <div className="bg-white rounded-lg shadow-lg p-6 text-center">
            <div className="flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white mx-auto mb-4">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Sécurité</h3>
            <p className="text-gray-600">
              Protection maximale des données médicales avec des protocoles de sécurité avancés
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6 text-center">
            <div className="flex items-center justify-center h-12 w-12 rounded-md bg-green-500 text-white mx-auto mb-4">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Innovation</h3>
            <p className="text-gray-600">
              Technologies de pointe pour une expérience utilisateur optimale
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6 text-center">
            <div className="flex items-center justify-center h-12 w-12 rounded-md bg-purple-500 text-white mx-auto mb-4">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Collaboration</h3>
            <p className="text-gray-600">
              Travail en équipe avec les professionnels de santé pour des solutions adaptées
            </p>
          </div>
        </div>

        {/* Notre Équipe */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-8">Notre Équipe</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-32 h-32 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center">
                <span className="text-white text-2xl font-bold">LD</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Lamine Dianka</h3>
              <p className="text-blue-600 font-medium mb-2">Chef de projets</p>
              <p className="text-gray-600 text-sm">
                Spécialiste en informatique médicale avec plus de 15 ans d'expérience
              </p>
            </div>

            <div className="text-center">
              <div className="w-32 h-32 mx-auto mb-4 rounded-full bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center">
                <span className="text-white text-2xl font-bold">MD</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Moustapha Diao</h3>
              <p className="text-green-600 font-medium mb-2">Analyste de données</p>
              <p className="text-gray-600 text-sm">
                Experte en gestion de projets médicaux et coordination d'équipes
              </p>
            </div>

            <div className="text-center">
              <div className="w-32 h-32 mx-auto mb-4 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center">
                <span className="text-white text-2xl font-bold">MW</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Mamadou Wade</h3>
              <p className="text-purple-600 font-medium mb-2">Développeur Senior</p>
              <p className="text-gray-600 text-sm">
                Spécialiste en développement web et applications médicales sécurisées
              </p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-16 text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            Prêt à nous rejoindre ?
          </h3>
          <p className="text-lg text-gray-600 mb-8">
            Découvrez comment notre plateforme peut transformer votre pratique médicale
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/contact"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors duration-200"
            >
              Nous contacter
            </Link>
            <Link
              to="/login"
              className="inline-flex items-center px-6 py-3 border border-blue-600 text-base font-medium rounded-md text-blue-600 bg-white hover:bg-blue-50 transition-colors duration-200"
            >
              Essayer la plateforme
            </Link>
          </div>
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default AboutPage; 
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Header = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const handleLogout = () => {
    logout();
  };

  const isActive = (path) => {
    return location.pathname === path;
  };

  const isAdmin = user && (user.role === 'ADMIN' || user.is_superuser);

  return (
    <div className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white text-lg">🏥</span>
              </div>
              <h1 className="ml-3 text-2xl font-bold text-gray-900">Conformed</h1>
            </div>
            <nav className="flex space-x-8">
              <Link
                to="/admin/dashboard"
                className={`${isActive('/admin/dashboard') ? 'text-blue-600 font-medium' : 'text-gray-500 hover:text-gray-700'}`}
              >
                Accueil
              </Link>
              <Link
                to="/admin/statistiques"
                className={`${isActive('/admin/statistiques') ? 'text-blue-600 font-medium' : 'text-gray-500 hover:text-gray-700'}`}
              >
                Statistiques
              </Link>
              {isAdmin && (
                <Link
                  to="/admin/historique"
                  className={`${isActive('/admin/historique') ? 'text-blue-600 font-medium' : 'text-gray-500 hover:text-gray-700'}`}
                >
                  Historique
                </Link>
              )}
            </nav>
          </div>
          <div className="flex items-center space-x-4">
            <div className="relative">
              <input
                type="text"
                placeholder="Rechercher..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <svg className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <button className="p-2 text-gray-500 hover:text-gray-700">
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            </button>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-gray-700">👤</span>
              </div>
              <span className="text-gray-700 font-medium">{user?.username || 'admin'}</span>
              <div className="relative">
                <button className="flex items-center space-x-1 text-gray-500 hover:text-gray-700">
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {/* Dropdown menu pourrait être ajouté ici */}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Header; 
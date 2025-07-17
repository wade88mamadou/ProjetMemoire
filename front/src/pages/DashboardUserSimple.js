import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import useDarkMode from '../hooks/useDarkMode';
import MesDemandesExportation from './MesDemandesExportation';
import Plot from 'react-plotly.js';
import { getPatientsParMaladie } from '../services/api';
import LogoHeader from '../components/LogoHeader';

const DashboardUserSimple = () => {
  const { user, logout } = useAuth();
  const handleLogout = () => { logout(); };
  // Ajoute ce state pour le sélecteur de statistiques par groupe
  const [selectedChart, setSelectedChart] = useState('effectif');
  const [maladieStats, setMaladieStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [darkMode, setDarkMode] = useDarkMode();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const userMenuRef = useRef(null);

  // Charger les vraies statistiques depuis l'API
  useEffect(() => {
    const loadStats = async () => {
      try {
        setLoading(true);
        const stats = await getPatientsParMaladie();
        setMaladieStats(stats.data);
      } catch (error) {
        console.error('Erreur lors du chargement des statistiques:', error);
        // Fallback avec des données d'exemple
        setMaladieStats({
          infections: [
            { maladie: 'Grippe', nombre_patients: 10 },
            { maladie: 'COVID-19', nombre_patients: 5 },
            { maladie: 'Varicelle', nombre_patients: 3 }
          ],
          total_patients: 100,
          total_patients_avec_infections: 18
        });
      } finally {
        setLoading(false);
      }
    };

    loadStats();
  }, []);

  const sidebarItems = [
    {
      id: 'dashboard',
      label: 'Consulter tableau de bord',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      )
    },
    {
      id: 'export',
      label: 'Demande d\'exporter données',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      )
    },
  ];

  const renderContent = () => {
    if (activeTab === 'export') {
      return <MesDemandesExportation />;
    }

    // --- Bloc statistiques par maladie (avec vraies données) ---
    const infections = maladieStats?.infections || [];
    const labels = infections.map(item => item.maladie);
    const values = infections.map(item => item.nombre_patients);
    
    // Bar chart
    const barData = [
      {
        x: labels,
        y: values,
        type: 'bar',
        marker: {
          color: 'rgba(59, 130, 246, 0.8)',
          line: { color: 'rgba(59, 130, 246, 1)', width: 1 }
        },
        name: 'Nombre de patients'
      }
    ];
    const barLayout = {
      title: {
        text: "Répartition des patients par type d'infection",
        font: { size: 18, color: darkMode ? '#f3f4f6' : '#1f2937' }
      },
      xaxis: {
        title: "Type d'infection",
        tickangle: -45,
        font: { size: 12, color: darkMode ? '#d1d5db' : '#374151' }
      },
      yaxis: {
        title: 'Nombre de patients',
        font: { size: 12, color: darkMode ? '#d1d5db' : '#374151' }
      },
      margin: { l: 60, r: 30, t: 80, b: 100 },
      height: 400,
      showlegend: false,
      plot_bgcolor: 'rgba(0,0,0,0)',
      paper_bgcolor: 'rgba(0,0,0,0)',
      font: { color: darkMode ? '#f3f4f6' : '#1f2937' }
    };
    
    // Pie chart
    const pieData = [
      {
        values: values,
        labels: labels,
        type: 'pie',
        hole: 0.4,
        marker: {
          colors: [
            '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6',
            '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1'
          ]
        },
        textinfo: 'label+percent',
        textposition: 'outside'
      }
    ];
    const pieLayout = {
      title: {
        text: 'Répartition en pourcentage',
        font: { size: 18, color: darkMode ? '#f3f4f6' : '#1f2937' }
      },
      height: 400,
      showlegend: true,
      legend: {
        orientation: 'v',
        x: 1.1,
        y: 0.5,
        font: { color: darkMode ? '#f3f4f6' : '#1f2937' }
      },
      plot_bgcolor: 'rgba(0,0,0,0)',
      paper_bgcolor: 'rgba(0,0,0,0)',
      font: { color: darkMode ? '#f3f4f6' : '#1f2937' }
    };
    
    // Données d'exemple pour le sélecteur de groupe
    const groupes = ['Urbain', 'Semi-urbain', 'Europe'];
    const effectifs = [30, 20, 10];
    const sexRatios = [1.2, 0.8, 1.0];
    const agesMoyens = [35.5, 40.2, 29.8];
    const chartOptions = [
      { value: 'effectif', label: 'Effectif total par groupe' },
      { value: 'sexratio', label: 'Sex ratio (H/F) par groupe' },
      { value: 'agemoyen', label: 'Âge moyen par groupe' },
    ];
    
    let chartData, chartLayout, chartTitle;
    if (selectedChart === 'effectif') {
      chartData = [{ x: groupes, y: effectifs, type: 'bar', marker: { color: '#2563eb' } }];
      chartTitle = 'Effectif total par groupe';
      chartLayout = { 
        title: chartTitle, 
        xaxis: { title: 'Groupe' }, 
        yaxis: { title: 'Effectif' }, 
        height: 400,
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        font: { color: darkMode ? '#f3f4f6' : '#1f2937' }
      };
    } else if (selectedChart === 'sexratio') {
      chartData = [{ x: groupes, y: sexRatios, type: 'bar', marker: { color: '#059669' } }];
      chartTitle = 'Sex ratio (H/F) par groupe';
      chartLayout = { 
        title: chartTitle, 
        xaxis: { title: 'Groupe' }, 
        yaxis: { title: 'Sex ratio (H/F)' }, 
        height: 400,
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        font: { color: darkMode ? '#f3f4f6' : '#1f2937' }
      };
    } else {
      chartData = [{ x: groupes, y: agesMoyens, type: 'bar', marker: { color: '#f59e42' } }];
      chartTitle = 'Âge moyen par groupe';
      chartLayout = { 
        title: chartTitle, 
        xaxis: { title: 'Groupe' }, 
        yaxis: { title: 'Âge moyen' }, 
        height: 400,
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        font: { color: darkMode ? '#f3f4f6' : '#1f2937' }
      };
    }
    
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Tableau de bord</h2>
        
        {/* Statistiques générales */}
        {maladieStats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <div className="flex items-center">
                <div className="p-3 rounded-full bg-blue-100 dark:bg-blue-900">
                  <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Patients</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{maladieStats.total_patients || 0}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <div className="flex items-center">
                <div className="p-3 rounded-full bg-green-100 dark:bg-green-900">
                  <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Patients avec Infections</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{maladieStats.total_patients_avec_infections || 0}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <div className="flex items-center">
                <div className="p-3 rounded-full bg-yellow-100 dark:bg-yellow-900">
                  <svg className="w-6 h-6 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Types d'Infections</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{infections.length}</p>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Graphiques des statistiques par maladie */}
        {loading ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600 dark:text-gray-400">Chargement des statistiques par maladie...</p>
              </div>
            </div>
          </div>
        ) : maladieStats ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <Plot
                data={barData}
                layout={barLayout}
                config={{ responsive: true }}
                style={{ width: '100%' }}
              />
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <Plot
                data={pieData}
                layout={pieLayout}
                config={{ responsive: true }}
                style={{ width: '100%' }}
              />
            </div>
          </div>
        ) : (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <p className="text-gray-600 dark:text-gray-400">Aucune donnée disponible</p>
              </div>
            </div>
          </div>
        )}
        
        {/* Sélecteur de statistiques par groupe et graphique groupe EN BAS */}
        <div className="mt-8">
          <label className="mr-2 font-medium text-gray-700 dark:text-gray-300">Statistique à afficher :</label>
          <select
            className="p-2 border rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            value={selectedChart}
            onChange={e => setSelectedChart(e.target.value)}
          >
            {chartOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mt-4">
            <Plot data={chartData} layout={chartLayout} config={{ responsive: true }} style={{ width: '100%' }} />
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className={`min-h-screen ${darkMode ? 'dark' : ''}`}>
      <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
        {/* Sidebar */}
        <div className={`${sidebarOpen ? 'w-64' : 'w-16'} bg-white dark:bg-gray-800 shadow-lg transition-all duration-300 ease-in-out`}>
          <div className="flex flex-col h-full">
            {/* Logo */}
            <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200 dark:border-gray-700">
              {sidebarOpen && (
                <LogoHeader role="Utilisateur" />
              )}
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 rounded-md text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>

            {/* Sidebar Menu */}
            <nav className="flex-1 px-2 py-4 space-y-2">
              {sidebarItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200 ${
                    activeTab === item.id
                      ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                      : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                  }`}
                >
                  {item.icon}
                  {sidebarOpen && <span className="ml-3">{item.label}</span>}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Navbar */}
          <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between h-16 px-6">
              {/* Left side */}
              <div className="flex items-center space-x-4">
                {/* Logo */}
              <div className="flex items-center">
                  <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                </div>

                {/* Navigation Links */}
                <nav className="hidden md:flex space-x-4">
                  <button 
                    onClick={() => setActiveTab('dashboard')}
                    className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                  >
                    Accueil
                  </button>
                  <a href="#" className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white px-3 py-2 rounded-md text-sm font-medium">Statistiques</a>
                  <a href="#" className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white px-3 py-2 rounded-md text-sm font-medium">Historique</a>
                </nav>
          </div>

              {/* Right side */}
              <div className="flex items-center space-x-4">
                {/* Search Bar */}
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Rechercher..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-64 pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                </div>

                {/* Dark Mode Toggle */}
                <button
                  onClick={() => setDarkMode(!darkMode)}
                  className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700"
                  title={darkMode ? 'Mode clair' : 'Mode sombre'}
                >
                  {darkMode ? (
                    // Icône soleil SVG
                    <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
                  ) : (
                    // Icône lune SVG
                    <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12.79A9 9 0 1111.21 3a7 7 0 109.79 9.79z" /></svg>
                  )}
                </button>

                {/* User Menu */}
                <div className="relative" ref={userMenuRef}>
                  <button
                    className="flex items-center space-x-2 p-2 rounded-md text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                    onClick={() => setShowUserMenu((v) => !v)}
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    <span className="hidden md:block text-sm font-medium">{user?.username}</span>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  {showUserMenu && (
                    <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-md shadow-lg py-1 z-50">
                      <a
                        href="#"
                        className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                        onClick={() => setShowUserMenu(false)}
                      >
                        Paramètres
                      </a>
                      <button
                        onClick={() => {
                          setShowUserMenu(false);
                          setShowLogoutConfirm(true);
                        }}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                      >
                        Déconnexion
                      </button>
                  </div>
                  )}
                </div>
              </div>
            </div>
          </header>

          {/* Main Content Area */}
          <main className="flex-1 overflow-y-auto p-6">
            {renderContent()}
          </main>
        </div>
      </div>
      {showLogoutConfirm && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-40">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 max-w-sm w-full text-center">
            <h2 className="text-lg font-bold text-red-600 mb-4">Confirmer la déconnexion</h2>
            <p className="mb-6 text-gray-700 dark:text-gray-200">Voulez-vous vraiment vous déconnecter ?</p>
            <div className="flex justify-center gap-4">
              <button
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded"
                onClick={() => { setShowLogoutConfirm(false); handleLogout(); }}
              >
                Confirmer
              </button>
              <button
                className="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded"
                onClick={() => setShowLogoutConfirm(false)}
              >
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardUserSimple; 
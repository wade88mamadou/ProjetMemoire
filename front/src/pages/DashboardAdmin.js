import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { userService, patientService, alerteService, getPatientsParMaladie } from '../services/api';
import AdminUserManagement from './AdminUserManagement';
import StatisticsCharts from '../components/StatisticsCharts';
import useDarkMode from '../hooks/useDarkMode';
import { useNavigate } from 'react-router-dom';
import Plot from 'react-plotly.js';
import ConfigAlertesSecurite from './ConfigAlertesSecurite';
import AlertesCritiques from './AlertesCritiques';
import AuditAcces from './AuditAcces';
import RapportAudit from './RapportAudit';
import logo from '../conformed.png'; // adapte le chemin si besoin
import LogoHeader from '../components/LogoHeader';
import api from '../services/api';

const DashboardAdmin = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [darkMode, setDarkMode] = useDarkMode();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [searchQuery, setSearchQuery] = useState('');
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalPatients: 0,
    totalAlertes: 0
  });
  const [maladieStats, setMaladieStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const userMenuRef = useRef(null);
  const [selectedChart, setSelectedChart] = useState('effectif');
  const [accesData, setAccesData] = useState([]);
  const [accesLoading, setAccesLoading] = useState(false);
  const [accesError, setAccesError] = useState(null);
  const [accesPage, setAccesPage] = useState(1);
  const [accesTotalPages, setAccesTotalPages] = useState(1);
  const [accesSearch, setAccesSearch] = useState('');
  const [accesTypeFilter, setAccesTypeFilter] = useState('');
  const [accesDateFilter, setAccesDateFilter] = useState('');
  const [accesUserFilter, setAccesUserFilter] = useState('');
  const [userList, setUserList] = useState([]);

  // Fonction pour rafraîchir les statistiques
  const refreshStats = async () => {
    try {
      const [usersRes, patientsRes, alertesRes] = await Promise.all([
        userService.getUsers(),
        patientService.getPatients(),
        alerteService.getAlertes()
      ]);

      console.log('Réponse utilisateurs:', usersRes);
      console.log('Réponse patients:', patientsRes);
      console.log('Réponse alertes:', alertesRes);

      const newStats = {
        totalUsers: usersRes.data.count || usersRes.data.length,
        totalPatients: patientsRes.data.count || patientsRes.data.length,
        totalAlertes: alertesRes.data.count || alertesRes.data.length
      };

      console.log('Nouvelles statistiques:', newStats);
      setStats(newStats);
    } catch (error) {
      console.error('Erreur lors du rafraîchissement des statistiques:', error);
    }
  };

  // Fonction pour charger les statistiques par maladie
  const loadMaladieStats = async () => {
    try {
      console.log('Chargement des statistiques par maladie...');
      const response = await getPatientsParMaladie();
      console.log('Réponse API maladies:', response);
      setMaladieStats(response.data);
      console.log('Statistiques maladies mises à jour:', response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des statistiques par maladie:', error);
    }
  };

  // Charger la liste des utilisateurs pour le filtre
  useEffect(() => {
    if (activeTab !== 'historique') return;
    api.get('/utilisateurs/?page_size=1000')
      .then(res => {
        setUserList(res.data.results || res.data);
      })
      .catch(() => setUserList([]));
  }, [activeTab]);

  // Charger les accès à chaque changement de page, recherche ou filtre
  useEffect(() => {
    if (activeTab !== 'historique') return;
    setAccesLoading(true);
    let url = `/acces/?page=${accesPage}`;
    if (accesSearch) url += `&search=${encodeURIComponent(accesSearch)}`;
    if (accesTypeFilter) url += `&typeAcces=${encodeURIComponent(accesTypeFilter)}`;
    if (accesDateFilter) url += `&dateAcces=${encodeURIComponent(accesDateFilter)}`;
    if (accesUserFilter) url += `&utilisateur=${encodeURIComponent(accesUserFilter)}`;
    api.get(url)
      .then(res => {
        setAccesData(res.data.results || res.data);
        setAccesTotalPages(Math.ceil((res.data.count || res.data.length) / 10));
        setAccesLoading(false);
      })
      .catch(err => {
        setAccesError('Erreur lors du chargement de l\'historique');
        setAccesLoading(false);
      });
  }, [activeTab, accesPage, accesSearch, accesTypeFilter, accesDateFilter, accesUserFilter]);

  // Fermer le menu utilisateur si on clique en dehors
  useEffect(() => {
    function handleClickOutside(event) {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setShowUserMenu(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        console.log('Début du chargement des statistiques...');
        await Promise.all([refreshStats(), loadMaladieStats()]);
      } catch (error) {
        console.error('Erreur lors du chargement des statistiques:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const handleLogout = () => {
    logout();
  };

  // Sidebar menu items
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
      id: 'alerts',
      label: 'Configurer les alertes de sécurité',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      )
    },
    {
      id: 'roles',
      label: 'Gérer les rôles',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      )
    },
    {
      id: 'critical-alerts',
      label: 'Recevoir les alertes critiques',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5zM4.19 4.19A2 2 0 004 6v12a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-1.81 1.19zM12 9v2m0 4h.01" />
        </svg>
      )
    },
    {
      id: 'audit',
      label: 'Auditer les accès',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      )
    },
    {
      id: 'rapport-audit',
      label: 'Générer des rapports',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2a2 2 0 012-2h2a2 2 0 012 2v2m-6 4h6a2 2 0 002-2v-5a2 2 0 00-2-2H7a2 2 0 00-2 2v5a2 2 0 002 2z" />
        </svg>
      )
    }
  ];

  // Render content based on active tab
  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        console.log('Rendu du dashboard avec stats:', stats);
        console.log('maladieStats:', maladieStats);
        
        // Préparer les données pour les graphiques des maladies
        const infections = maladieStats?.infections || [];
        const labels = infections.map(item => item.maladie);
        const values = infections.map(item => item.nombre_patients);
        
        console.log('Infections:', infections);
        console.log('Labels:', labels);
        console.log('Values:', values);

        // Données pour le graphique en barres
        const barData = [
          {
            x: labels,
            y: values,
            type: 'bar',
            marker: {
              color: 'rgba(59, 130, 246, 0.8)',
              line: {
                color: 'rgba(59, 130, 246, 1)',
                width: 1
              }
            },
            name: 'Nombre de patients'
          }
        ];

        const barLayout = {
          title: {
            text: 'Répartition des patients par type d\'infection',
            font: { size: 18, color: darkMode ? '#f3f4f6' : '#1f2937' }
          },
          xaxis: {
            title: 'Type d\'infection',
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

        // Données pour le graphique circulaire
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

        // Données d'exemple à remplacer par tes vraies stats
        const groupes = ['Urbain', 'Semi-urbain', 'Europe'];
        const effectifs = [30, 20, 10];
        const sexRatios = [1.2, 0.8, 1.0]; // H/F
        const agesMoyens = [35.5, 40.2, 29.8];

        const chartOptions = [
          { value: 'effectif', label: 'Effectif total par groupe' },
          { value: 'sexratio', label: 'Sex ratio (H/F) par groupe' },
          { value: 'agemoyen', label: 'Âge moyen par groupe' },
        ];

        let chartData, chartLayout, chartTitle;
        if (selectedChart === 'effectif') {
          chartData = [{
            x: groupes,
            y: effectifs,
            type: 'bar',
            marker: { color: '#2563eb' }
          }];
          chartTitle = 'Effectif total par groupe';
          chartLayout = { title: chartTitle, xaxis: { title: 'Groupe' }, yaxis: { title: 'Effectif' }, height: 400 };
        } else if (selectedChart === 'sexratio') {
          chartData = [{
            x: groupes,
            y: sexRatios,
            type: 'bar',
            marker: { color: '#059669' }
          }];
          chartTitle = 'Sex ratio (H/F) par groupe';
          chartLayout = { title: chartTitle, xaxis: { title: 'Groupe' }, yaxis: { title: 'Sex ratio (H/F)' }, height: 400 };
        } else {
          chartData = [{
            x: groupes,
            y: agesMoyens,
            type: 'bar',
            marker: { color: '#f59e42' }
          }];
          chartTitle = 'Âge moyen par groupe';
          chartLayout = { title: chartTitle, xaxis: { title: 'Groupe' }, yaxis: { title: 'Âge moyen' }, height: 400 };
        }

        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Tableau de bord</h2>
            
            {/* Cartes statistiques principales */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                        </svg>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Total Utilisateurs</dt>
                        <dd className="text-lg font-medium text-gray-900 dark:text-white">{stats.totalUsers}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Total Patients</dt>
                        <dd className="text-lg font-medium text-gray-900 dark:text-white">{stats.totalPatients}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-red-500 rounded-md flex items-center justify-center">
                        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                        </svg>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Alertes Actives</dt>
                        <dd className="text-lg font-medium text-gray-900 dark:text-white">{stats.totalAlertes}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Graphiques des statistiques par maladie */}
            {maladieStats ? (
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
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600 dark:text-gray-400">Chargement des statistiques par maladie...</p>
                  </div>
                </div>
              </div>
            )}

            {/* Tableau détaillé des infections */}
            {maladieStats && maladieStats.infections && maladieStats.infections.length > 0 && (
              <div className="my-8">
                {/* GroupStatsCharts component was removed, so this block is now empty */}
              </div>
            )}

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 my-8">
              <h3 className="text-xl font-bold mb-4 text-center">Statistiques par groupe de résidence</h3>
              <div className="mb-4 flex justify-center">
                <label className="font-semibold mr-2">Choisir le graphique :</label>
                <select
                  className="border rounded px-2 py-1"
                  value={selectedChart}
                  onChange={e => setSelectedChart(e.target.value)}
                >
                  {chartOptions.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>
              <Plot
                data={chartData}
                layout={chartLayout}
                config={{ responsive: true }}
                style={{ width: '100%' }}
              />
            </div>
          </div>
        );
      
      case 'roles':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Gestion des rôles</h2>
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 space-y-4">
              <AdminUserManagement onUserChange={refreshStats} />
            </div>
          </div>
        );

      case 'alerts':
        return <ConfigAlertesSecurite />;
      case 'critical-alerts':
        return <AlertesCritiques />;
      case 'audit':
        return <AuditAcces />;
      case 'rapport-audit':
        return <RapportAudit />;

      case 'statistiques':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Statistiques Détaillées</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="bg-blue-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-blue-900">Total Patients</h3>
                <p className="text-3xl font-bold text-blue-600">{stats.totalPatients}</p>
              </div>
              <div className="bg-green-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-green-900">Nouveaux Aujourd'hui</h3>
                <p className="text-3xl font-bold text-green-600">0</p>
              </div>
              <div className="bg-red-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-red-900">Cas Critiques</h3>
                <p className="text-3xl font-bold text-red-600">0</p>
              </div>
              <div className="bg-orange-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-orange-900">Taux de Guérison</h3>
                <p className="text-3xl font-bold text-orange-600">0%</p>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Graphiques Statistiques</h3>
              <p className="text-gray-600 dark:text-gray-400">Les graphiques détaillés seront affichés ici...</p>
            </div>
          </div>
        );

      case 'historique':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Historique des Actions</h2>
            <div className="flex flex-col md:flex-row md:items-center gap-4 mb-4">
              <input
                type="text"
                placeholder="Rechercher (utilisateur, description...)"
                value={accesSearch}
                onChange={e => { setAccesSearch(e.target.value); setAccesPage(1); }}
                className="px-3 py-2 border rounded-md w-full md:w-64 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="date"
                value={accesDateFilter}
                onChange={e => { setAccesDateFilter(e.target.value); setAccesPage(1); }}
                className="px-3 py-2 border rounded-md w-full md:w-48 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <select
                value={accesTypeFilter}
                onChange={e => { setAccesTypeFilter(e.target.value); setAccesPage(1); }}
                className="px-3 py-2 border rounded-md w-full md:w-48 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Tous les types</option>
                <option value="CONSULTATION">Consultation</option>
                <option value="MODIFICATION">Modification</option>
                <option value="SUPPRESSION">Suppression</option>
                <option value="CONNEXION">Connexion</option>
              </select>
              <select
                value={accesUserFilter}
                onChange={e => { setAccesUserFilter(e.target.value); setAccesPage(1); }}
                className="px-3 py-2 border rounded-md w-full md:w-48 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Tous les utilisateurs</option>
                {userList.map(u => (
                  <option key={u.id} value={u.id}>{u.username} {u.first_name || ''} {u.last_name || ''}</option>
                ))}
              </select>
            </div>
            <div className="overflow-x-auto bg-white dark:bg-gray-800 rounded-lg shadow">
              {accesLoading ? (
                <div className="p-8 text-center text-gray-500">Chargement...</div>
              ) : accesError ? (
                <div className="p-8 text-center text-red-500">{accesError}</div>
              ) : (
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Date</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Type</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Utilisateur</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Données concernées</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {accesData.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="px-4 py-8 text-center text-gray-500">Aucune donnée</td>
                      </tr>
                    ) : (
                      accesData.map((acces, idx) => (
                        <tr key={acces.id || idx}>
                          <td className="px-4 py-2 whitespace-nowrap">{acces.dateAcces}</td>
                          <td className="px-4 py-2 whitespace-nowrap">{acces.typeAcces}</td>
                          <td className="px-4 py-2 whitespace-nowrap">{acces.utilisateur ? (acces.utilisateur.username || acces.utilisateur) : '—'}</td>
                          <td className="px-4 py-2">{acces.donnees_concernees || '—'}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              )}
            </div>
            {/* Pagination */}
            <div className="flex justify-center items-center gap-2 mt-4">
              <button
                onClick={() => setAccesPage(p => Math.max(1, p - 1))}
                disabled={accesPage === 1}
                className="px-3 py-1 rounded bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 disabled:opacity-50"
              >
                Précédent
              </button>
              <span className="text-gray-700 dark:text-gray-200">Page {accesPage} / {accesTotalPages}</span>
              <button
                onClick={() => setAccesPage(p => Math.min(accesTotalPages, p + 1))}
                disabled={accesPage === accesTotalPages}
                className="px-3 py-1 rounded bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 disabled:opacity-50"
              >
                Suivant
              </button>
            </div>
          </div>
        );

      default:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{sidebarItems.find(item => item.id === activeTab)?.label}</h2>
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
              <p className="text-gray-600 dark:text-gray-400">Fonctionnalité en cours de développement...</p>
            </div>
          </div>
        );
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${darkMode ? 'dark' : ''}`}>
      <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
        {/* Sidebar */}
        <div className={`${sidebarOpen ? 'w-64' : 'w-16'} bg-white dark:bg-gray-800 shadow-lg transition-all duration-300 ease-in-out`}>
          <div className="flex flex-col h-full">
            {/* Logo */}
            <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200 dark:border-gray-700">
              {sidebarOpen && (
                <div className="flex items-center gap-2 flex-shrink-0 pl-0">
                <LogoHeader />
                <span className="ml-2 text-2xl font-bold text-blue-700 tracking-wide animate-fade-in">Conformed</span>
              </div>
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
                  onClick={() => {
                    if (item.id === 'import') {
                      navigate('/import-data');
                    } else if (item.id === 'alerts') {
                      setActiveTab('alerts');
                    } else if (item.id === 'critical-alerts') {
                      setActiveTab('critical-alerts');
                    } else if (item.id === 'audit') {
                      setActiveTab('audit');
                    } else if (item.id === 'rapport-audit') {
                      setActiveTab('rapport-audit');
                    } else {
                      setActiveTab(item.id);
                    }
                  }}
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
            <div className="flex items-center justify-between h-16 px-6 w-full">
              {/* Bloc gauche : Logo + Conformed */}
              {/*<div className="flex items-center gap-2 flex-shrink-0">
                <LogoHeader />
                <span className="ml-2 text-2xl font-bold text-blue-700 tracking-wide animate-fade-in">Conformed</span>
              </div>*/}
              {/* Bloc centre : Liens de navigation */}
              <nav className="flex-1 flex justify-center space-x-8">
                <button 
                  onClick={() => setActiveTab('dashboard')} 
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                    activeTab === 'dashboard'
                      ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20'
                      : 'text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400'
                  }`}
                >
                  Accueil
                </button>
                <button 
                  onClick={() => setActiveTab('statistiques')} 
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                    activeTab === 'statistiques'
                      ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20'
                      : 'text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400'
                  }`}
                >
                  Statistiques
                </button>
                <button 
                  onClick={() => setActiveTab('historique')} 
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                    activeTab === 'historique'
                      ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20'
                      : 'text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400'
                  }`}
                >
                  Historique
                </button>
                </nav>
              {/* Bloc droit : Recherche, dark mode, user menu */}
              <div className="flex items-center gap-6 flex-shrink-0">
                {/* Barre de recherche */}
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
          <main className="flex-1 overflow-y-auto p-6 bg-gray-50 dark:bg-gray-900">
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

export default DashboardAdmin; 
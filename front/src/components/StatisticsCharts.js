import React, { useState, useEffect } from 'react';
import axios from 'axios';

const StatisticsCharts = ({ userRole }) => {
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStatistics = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('token');
        const response = await axios.get('http://localhost:8000/api/patient-statistics/', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setStatistics(response.data);
      } catch (err) {
        setError('Erreur lors du chargement des statistiques');
        console.error('Erreur statistiques:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStatistics();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  if (!statistics) {
    return <div>Aucune donnée disponible</div>;
  }

  // Fonction pour calculer le pourcentage
  const calculatePercentage = (value, total) => {
    if (total === 0) return 0;
    return Math.round((value / total) * 100);
  };

  // Fonction pour créer une barre de progression
  const ProgressBar = ({ value, total, color = "bg-blue-500" }) => {
    const percentage = calculatePercentage(value, total);
    return (
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div 
          className={`${color} h-2.5 rounded-full transition-all duration-300`} 
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    );
  };

  return (
    <div className="space-y-8">
      {/* Informations sur les champs disponibles */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">Champs Disponibles dans la Base</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          {Object.entries(statistics.available_fields || {}).map(([table, fields]) => (
            <div key={table} className="bg-white p-3 rounded border">
              <h4 className="font-medium text-blue-800 capitalize mb-2">{table}</h4>
              <ul className="space-y-1">
                {fields.map(field => (
                  <li key={field} className="text-gray-600">
                    <code className="bg-gray-100 px-1 rounded text-xs">{field}</code>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Statistiques globales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Patients</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{statistics.total_patients}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Hommes</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{statistics.sexe_distribution?.Homme || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-pink-100 rounded-lg">
              <svg className="w-6 h-6 text-pink-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Femmes</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{statistics.sexe_distribution?.Femme || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Types de Logement</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{Object.keys(statistics.logement_distribution || {}).length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Graphiques simplifiés */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Répartition par sexe */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Répartition par Sexe</h3>
          <div className="space-y-4">
            {Object.entries(statistics.sexe_distribution || {}).map(([sexe, count]) => (
              <div key={sexe} className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{sexe}</span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600 dark:text-gray-400">{count}</span>
                  <div className="w-32">
                    <ProgressBar 
                      value={count} 
                      total={statistics.total_patients} 
                      color={sexe === 'Homme' ? 'bg-blue-500' : 'bg-pink-500'} 
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Répartition par type de logement */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Répartition par Type de Logement</h3>
          <div className="space-y-4">
            {Object.entries(statistics.logement_distribution || {}).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{type}</span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600 dark:text-gray-400">{count}</span>
                  <div className="w-32">
                    <ProgressBar 
                      value={count} 
                      total={statistics.total_patients} 
                      color="bg-purple-500" 
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Répartition par lieu de naissance */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Répartition par Lieu de Naissance</h3>
          <div className="space-y-4 max-h-64 overflow-y-auto">
            {Object.entries(statistics.lieu_naissance_distribution || {}).map(([lieu, count]) => (
              <div key={lieu} className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{lieu}</span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600 dark:text-gray-400">{count}</span>
                  <div className="w-32">
                    <ProgressBar 
                      value={count} 
                      total={statistics.total_patients} 
                      color="bg-green-500" 
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Répartition par niveau d'étude */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Répartition par Niveau d'Étude</h3>
          <div className="space-y-4 max-h-64 overflow-y-auto">
            {Object.entries(statistics.niveau_etude_distribution || {}).map(([niveau, count]) => (
              <div key={niveau} className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{niveau}</span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600 dark:text-gray-400">{count}</span>
                  <div className="w-32">
                    <ProgressBar 
                      value={count} 
                      total={statistics.total_patients} 
                      color="bg-yellow-500" 
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Répartition par ville (plus large) */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Répartition par Ville de Résidence</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto">
          {Object.entries(statistics.ville_distribution || {}).map(([ville, count]) => (
            <div key={ville} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{ville}</span>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600 dark:text-gray-400">{count}</span>
                <div className="w-24">
                  <ProgressBar 
                    value={count} 
                    total={statistics.total_patients} 
                    color="bg-red-500" 
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default StatisticsCharts; 
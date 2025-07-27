import React, { useEffect, useState } from 'react';
import { 
  typeAlerteConformiteService, 
  regleAlerteConformiteService, 
  alerteConformiteService,
  conformiteService 
} from '../services/api';
import Plot from 'react-plotly.js';

const ConfigAlertesConformite = () => {
  const [typesAlertes, setTypesAlertes] = useState([]);
  const [reglesAlertes, setReglesAlertes] = useState([]);
  const [alertesActives, setAlertesActives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [configuration, setConfiguration] = useState({});
  const [statistiques, setStatistiques] = useState({});
  
  // États pour les modales
  const [showAddRegle, setShowAddRegle] = useState(false);
  const [showConfiguration, setShowConfiguration] = useState(false);
  const [editingRegle, setEditingRegle] = useState(null);
  
  // Formulaires
  const [regleForm, setRegleForm] = useState({
    nom: '',
    description: '',
    type_alerte: '',
    conditions: '',
    seuil: 1,
    periode_surveillance: 24,
    actions_automatiques: [],
    destinataires_notification: []
  });

  const [configForm, setConfigForm] = useState({
    activation_surveillance: true,
    delai_notification_defaut: 24,
    escalation_automatique: true,
    seuil_acces_non_autorise: 3,
    seuil_consultation_excessive: 50,
    notifier_admin_par_defaut: true,
    notifier_dpo_par_defaut: false,
    notifier_cdp_par_defaut: false
  });

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [typesRes, reglesRes, alertesRes, configRes, statsRes] = await Promise.all([
        typeAlerteConformiteService.getTypes(),
        regleAlerteConformiteService.getRegles(),
        alerteConformiteService.getAlertes(),
        conformiteService.getConfiguration(),
        conformiteService.getStatistiques()
      ]);

      setTypesAlertes(typesRes.data || []);
      setReglesAlertes(reglesRes.data || []);
      setAlertesActives(alertesRes.data || []);
      setConfiguration(configRes.data || {});
      setStatistiques(statsRes.data || {});
    } catch (err) {
      setError('Erreur lors du chargement des données.');
      console.error('Erreur:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAddRegle = async (e) => {
    e.preventDefault();
    try {
      await regleAlerteConformiteService.createRegle(regleForm);
      setShowAddRegle(false);
      setRegleForm({
        nom: '',
        description: '',
        type_alerte: '',
        conditions: '',
        seuil: 1,
        periode_surveillance: 24,
        actions_automatiques: [],
        destinataires_notification: []
      });
      fetchData();
    } catch (err) {
      setError('Erreur lors de la création de la règle.');
    }
  };

  const handleUpdateRegle = async (e) => {
    e.preventDefault();
    try {
      await regleAlerteConformiteService.updateRegle(editingRegle.id, regleForm);
      setEditingRegle(null);
      setShowAddRegle(false);
      fetchData();
    } catch (err) {
      setError('Erreur lors de la mise à jour de la règle.');
    }
  };

  const handleDeleteRegle = async (id) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette règle ?')) {
      try {
        await regleAlerteConformiteService.deleteRegle(id);
        fetchData();
      } catch (err) {
        setError('Erreur lors de la suppression de la règle.');
      }
    }
  };

  const handleSaveConfiguration = async (e) => {
    e.preventDefault();
    try {
      await conformiteService.configurerAlertes(configForm);
      setShowConfiguration(false);
      fetchData();
    } catch (err) {
      setError('Erreur lors de la sauvegarde de la configuration.');
    }
  };

  const executerSurveillance = async () => {
    try {
      await alerteConformiteService.executerSurveillance();
      fetchData();
      alert('Surveillance exécutée avec succès !');
    } catch (err) {
      setError('Erreur lors de l\'exécution de la surveillance.');
    }
  };

  const getNiveauCriticite = (niveau) => {
    const niveaux = {
      1: { nom: 'Faible', couleur: 'bg-green-100 text-green-800' },
      2: { nom: 'Moyen', couleur: 'bg-yellow-100 text-yellow-800' },
      3: { nom: 'Élevé', couleur: 'bg-orange-100 text-orange-800' },
      4: { nom: 'Critique', couleur: 'bg-red-100 text-red-800' },
      5: { nom: 'Urgent', couleur: 'bg-purple-100 text-purple-800' }
    };
    return niveaux[niveau] || { nom: 'Inconnu', couleur: 'bg-gray-100 text-gray-800' };
  };

  const getNormeConformite = (norme) => {
    const normes = {
      'RGPD': { nom: 'RGPD', couleur: 'bg-blue-100 text-blue-800' },
      'HIPAA': { nom: 'HIPAA', couleur: 'bg-green-100 text-green-800' },
      'CDP': { nom: 'CDP Sénégal', couleur: 'bg-yellow-100 text-yellow-800' },
      'GENERAL': { nom: 'Général', couleur: 'bg-gray-100 text-gray-800' }
    };
    return normes[norme] || { nom: norme, couleur: 'bg-gray-100 text-gray-800' };
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🔒 Configuration des Alertes de Conformité
        </h1>
        <p className="text-gray-600">
          Système moderne de surveillance RGPD, HIPAA et CDP Sénégal
        </p>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Statistiques générales */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <div className="p-2 rounded-full bg-blue-100">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Types d'Alertes</p>
              <p className="text-2xl font-semibold text-gray-900">{typesAlertes.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <div className="p-2 rounded-full bg-green-100">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Règles Actives</p>
              <p className="text-2xl font-semibold text-gray-900">{reglesAlertes.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <div className="p-2 rounded-full bg-red-100">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Alertes Actives</p>
              <p className="text-2xl font-semibold text-gray-900">{alertesActives.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <div className="p-2 rounded-full bg-purple-100">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Surveillance</p>
              <p className="text-2xl font-semibold text-gray-900">
                {configuration.activation_surveillance ? 'Active' : 'Inactive'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Actions principales */}
      <div className="flex flex-wrap gap-4 mb-8">
        <button
          onClick={() => setShowAddRegle(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Ajouter une Règle
        </button>

        <button
          onClick={() => setShowConfiguration(true)}
          className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Configuration
        </button>

        <button
          onClick={executerSurveillance}
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg flex items-center"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Exécuter Surveillance
        </button>
      </div>

      {/* Types d'Alertes */}
      <div className="bg-white rounded-lg shadow-md mb-8">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Types d'Alertes de Conformité</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Code</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nom</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Norme</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Niveau</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Délai</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {typesAlertes.map((type) => {
                const niveau = getNiveauCriticite(type.niveau_criticite);
                const norme = getNormeConformite(type.norme_conformite);
                return (
                  <tr key={type.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {type.code}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {type.nom}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${norme.couleur}`}>
                        {norme.nom}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${niveau.couleur}`}>
                        {niveau.nom}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {type.delai_notification}h
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Règles d'Alertes */}
      <div className="bg-white rounded-lg shadow-md mb-8">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Règles d'Alertes de Conformité</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nom</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Seuil</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Période</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {reglesAlertes.map((regle) => (
                <tr key={regle.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {regle.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {regle.nom}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {regle.type_alerte}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {regle.seuil}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {regle.periode_surveillance}h
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => {
                        setEditingRegle(regle);
                        setRegleForm(regle);
                        setShowAddRegle(true);
                      }}
                      className="text-blue-600 hover:text-blue-900 mr-4"
                    >
                      Éditer
                    </button>
                    <button
                      onClick={() => handleDeleteRegle(regle.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Supprimer
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Alertes Actives */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Alertes Actives</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Titre</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Statut</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {alertesActives.slice(0, 10).map((alerte) => {
                const niveau = getNiveauCriticite(alerte.niveau_criticite);
                return (
                  <tr key={alerte.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {alerte.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {alerte.titre}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {alerte.type_alerte?.nom || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${niveau.couleur}`}>
                        {niveau.nom}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(alerte.date_creation).toLocaleDateString()}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modale Ajout/Édition Règle */}
      {showAddRegle && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {editingRegle ? 'Modifier la Règle' : 'Ajouter une Règle'}
              </h3>
              <form onSubmit={editingRegle ? handleUpdateRegle : handleAddRegle}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Nom</label>
                  <input
                    type="text"
                    value={regleForm.nom}
                    onChange={(e) => setRegleForm({...regleForm, nom: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                  <textarea
                    value={regleForm.description}
                    onChange={(e) => setRegleForm({...regleForm, description: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows="3"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Type d'Alerte</label>
                  <select
                    value={regleForm.type_alerte}
                    onChange={(e) => setRegleForm({...regleForm, type_alerte: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="">Sélectionner un type</option>
                    {typesAlertes.map((type) => (
                      <option key={type.id} value={type.id}>{type.nom}</option>
                    ))}
                  </select>
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Seuil</label>
                  <input
                    type="number"
                    value={regleForm.seuil}
                    onChange={(e) => setRegleForm({...regleForm, seuil: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="1"
                    required
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Période de Surveillance (h)</label>
                  <input
                    type="number"
                    value={regleForm.periode_surveillance}
                    onChange={(e) => setRegleForm({...regleForm, periode_surveillance: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="1"
                    required
                  />
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => {
                      setShowAddRegle(false);
                      setEditingRegle(null);
                      setRegleForm({
                        nom: '',
                        description: '',
                        type_alerte: '',
                        conditions: '',
                        seuil: 1,
                        periode_surveillance: 24,
                        actions_automatiques: [],
                        destinataires_notification: []
                      });
                    }}
                    className="px-4 py-2 text-gray-600 bg-gray-200 rounded-md hover:bg-gray-300"
                  >
                    Annuler
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    {editingRegle ? 'Modifier' : 'Ajouter'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Modale Configuration */}
      {showConfiguration && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Configuration du Système</h3>
              <form onSubmit={handleSaveConfiguration}>
                <div className="mb-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={configForm.activation_surveillance}
                      onChange={(e) => setConfigForm({...configForm, activation_surveillance: e.target.checked})}
                      className="mr-2"
                    />
                    <span className="text-sm font-medium text-gray-700">Activer la surveillance</span>
                  </label>
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Délai de notification par défaut (h)</label>
                  <input
                    type="number"
                    value={configForm.delai_notification_defaut}
                    onChange={(e) => setConfigForm({...configForm, delai_notification_defaut: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="1"
                  />
                </div>
                <div className="mb-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={configForm.escalation_automatique}
                      onChange={(e) => setConfigForm({...configForm, escalation_automatique: e.target.checked})}
                      className="mr-2"
                    />
                    <span className="text-sm font-medium text-gray-700">Escalade automatique</span>
                  </label>
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Seuil accès non autorisé</label>
                  <input
                    type="number"
                    value={configForm.seuil_acces_non_autorise}
                    onChange={(e) => setConfigForm({...configForm, seuil_acces_non_autorise: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="1"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Seuil consultation excessive</label>
                  <input
                    type="number"
                    value={configForm.seuil_consultation_excessive}
                    onChange={(e) => setConfigForm({...configForm, seuil_consultation_excessive: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="1"
                  />
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowConfiguration(false)}
                    className="px-4 py-2 text-gray-600 bg-gray-200 rounded-md hover:bg-gray-300"
                  >
                    Annuler
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                  >
                    Sauvegarder
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConfigAlertesConformite; 
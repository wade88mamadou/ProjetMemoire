import React, { useEffect, useState } from 'react';
import { regleConformiteService, parametreConformiteService } from '../services/api';
import Plot from 'react-plotly.js';

const initialRegleForm = { nom: '', description: '', gravite: '', active: true };
const initialParamForm = { nom: '', valeur: '', unite: '', regle: '' };

// Paramètres médicaux courants avec leurs seuils par défaut
const parametresMedicauxCourants = [
  {
    nom: 'Glycémie',
    seuilMin: 70,
    seuilMax: 110,
    unite: 'mg/dL',
    description: 'Taux de glucose dans le sang'
  },
  {
    nom: 'Température',
    seuilMin: 36.0,
    seuilMax: 37.5,
    unite: '°C',
    description: 'Température corporelle'
  },
  {
    nom: 'Tension artérielle systolique',
    seuilMin: 90,
    seuilMax: 140,
    unite: 'mmHg',
    description: 'Pression artérielle systolique'
  },
  {
    nom: 'Tension artérielle diastolique',
    seuilMin: 60,
    seuilMax: 90,
    unite: 'mmHg',
    description: 'Pression artérielle diastolique'
  },
  {
    nom: 'Fréquence cardiaque',
    seuilMin: 60,
    seuilMax: 100,
    unite: 'bpm',
    description: 'Nombre de battements cardiaques par minute'
  },
  {
    nom: 'Saturation en oxygène',
    seuilMin: 95,
    seuilMax: 100,
    unite: '%',
    description: 'Taux d\'oxygène dans le sang'
  }
];

// Nouvelles alertes de sécurité avec leurs seuils par défaut
const alertesSecuriteCourantes = [
  {
    nom: 'Accès non autorisé',
    seuilMin: 1,
    seuilMax: null,
    unite: 'tentative',
    description: 'Nombre de tentatives d\'accès non autorisé',
    type: 'SECURITE_ACCES'
  },
  {
    nom: 'Fuite de données',
    seuilMin: 1,
    seuilMax: null,
    unite: 'incident',
    description: 'Détection de fuite de données médicales',
    type: 'SECURITE_DONNEES'
  },
  {
    nom: 'Tentative d\'intrusion',
    seuilMin: 3,
    seuilMax: null,
    unite: 'tentative',
    description: 'Nombre de tentatives d\'intrusion',
    type: 'SECURITE_INTRUSION'
  },
  {
    nom: 'Export non autorisé',
    seuilMin: 1,
    seuilMax: null,
    unite: 'tentative',
    description: 'Tentatives d\'export sans autorisation',
    type: 'SECURITE_EXPORT'
  },
  {
    nom: 'Modification critique',
    seuilMin: 1,
    seuilMax: null,
    unite: 'modification',
    description: 'Modifications de données critiques',
    type: 'SECURITE_MODIFICATION'
  },
  {
    nom: 'Suppression en masse',
    seuilMin: 5,
    seuilMax: null,
    unite: 'suppression',
    description: 'Suppressions de multiples dossiers',
    type: 'SECURITE_SUPPRESSION'
  },
  {
    nom: 'Connexion suspecte',
    seuilMin: 1,
    seuilMax: null,
    unite: 'connexion',
    description: 'Connexions depuis sources suspectes',
    type: 'SECURITE_CONNEXION'
  },
  {
    nom: 'Violation secret médical',
    seuilMin: 1,
    seuilMax: null,
    unite: 'violation',
    description: 'Violations du secret médical',
    type: 'SECURITE_SECRET'
  },
  {
    nom: 'Accès hors horaires',
    seuilMin: 1,
    seuilMax: null,
    unite: 'accès',
    description: 'Accès en dehors des horaires normaux',
    type: 'SECURITE_HORAIRE'
  },
  {
    nom: 'Échecs de connexion',
    seuilMin: 5,
    seuilMax: null,
    unite: 'échec',
    description: 'Multiples échecs de connexion',
    type: 'SECURITE_ECHEC'
  }
];

const ConfigAlertesSecurite = () => {
  const [regles, setRegles] = useState([]);
  const [parametres, setParametres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deletingId, setDeletingId] = useState(null);
  const [deleteType, setDeleteType] = useState(null); // 'regle' ou 'parametre'
  const [editRegle, setEditRegle] = useState(null); // objet à éditer ou null
  const [editParam, setEditParam] = useState(null); // objet à éditer ou null
  const [regleForm, setRegleForm] = useState(initialRegleForm);
  const [paramForm, setParamForm] = useState(initialParamForm);
  const [saving, setSaving] = useState(false);
  const [addRegleOpen, setAddRegleOpen] = useState(false);
  const [addParamOpen, setAddParamOpen] = useState(false);
  const [addRegleForm, setAddRegleForm] = useState(initialRegleForm);
  const [addParamForm, setAddParamForm] = useState(initialParamForm);
  // Ajout d'un état pour la liste des règles (pour le menu déroulant)
  const [reglesList, setReglesList] = useState([]);
  // État pour la modale de sélection des paramètres médicaux
  const [showParametresMedicaux, setShowParametresMedicaux] = useState(false);
  // État pour la modale de sélection des alertes de sécurité
  const [showAlertesSecurite, setShowAlertesSecurite] = useState(false);

  const reglesSansSeuil = [
    'Suppression en masse',
    'Export non autorisé',
    'Fuite de données',
    'Connexion suspecte',
    'Violation secret médical',
    'Accès hors horaires',
    'Échecs de connexion'
  ];
  
  const shouldDisplaySeuils = (selectedRuleId) => {
    const regle = reglesList.find(r => (r.idRegle || r.id) === selectedRuleId);
    const regleNom = regle ? (regle.nomRegle || regle.nom || regle.name) : '';
    return !reglesSansSeuil.includes(regleNom);
  };

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [reglesRes, parametresRes] = await Promise.all([
        regleConformiteService.getRegles(),
        parametreConformiteService.getParametres()
      ]);
      const reglesData = Array.isArray(reglesRes.data)
        ? reglesRes.data
        : (reglesRes.data.results || []);
      const parametresData = Array.isArray(parametresRes.data)
        ? parametresRes.data
        : (parametresRes.data.results || []);
      setRegles(reglesData);
      setParametres(parametresData);
    } catch (err) {
      setError('Erreur lors du chargement des données.');
      setRegles([]);
      setParametres([]);
    } finally {
      setLoading(false);
    }
  };

  // Charger la liste des règles pour le menu déroulant
  useEffect(() => {
    const fetchRegles = async () => {
      try {
        const res = await regleConformiteService.getRegles();
        const data = Array.isArray(res.data) ? res.data : (res.data.results || []);
        setReglesList(data);
      } catch (e) {
        setReglesList([]);
      }
    };
    fetchRegles();
  }, []);

  useEffect(() => {
    fetchData();
  }, []);

  // Suppression règle
  const handleDeleteRegle = async (id) => {
    if (!window.confirm('Confirmer la suppression de cette règle ?')) return;
    setDeletingId(id);
    setDeleteType('regle');
    try {
      await regleConformiteService.deleteRegle(id);
      await fetchData();
    } catch (err) {
      alert('Erreur lors de la suppression.');
    } finally {
      setDeletingId(null);
      setDeleteType(null);
    }
  };

  // Suppression paramètre
  const handleDeleteParametre = async (id) => {
    if (!window.confirm('Confirmer la suppression de ce paramètre/seuil ?')) return;
    setDeletingId(id);
    setDeleteType('parametre');
    try {
      await parametreConformiteService.deleteParametre(id);
      await fetchData();
    } catch (err) {
      alert('Erreur lors de la suppression.');
    } finally {
      setDeletingId(null);
      setDeleteType(null);
    }
  };

  // Ouvrir la modale d'édition règle (mapping correct)
  const openEditRegle = (regle) => {
    setEditRegle(regle);
    setRegleForm({
      nom: regle.nomRegle || regle.nom || regle.name || '',
      description: regle.description || '',
      gravite: regle.niveauCritique || regle.gravite || '',
      active: regle.is_active !== undefined ? regle.is_active : true
    });
  };

  // Ouvrir la modale d'édition paramètre
  const openEditParam = (param) => {
    setEditParam(param);
    setParamForm({
      nom: param.nom || '',
      seuilMin: param.seuilMin || '',
      seuilMax: param.seuilMax || '',
      unite: param.unite || '',
      regle: param.regle ? (param.regle.idRegle || param.regle.id || param.regle) : ''
    });
  };

  // Fermer les modales d'édition
  const closeEdit = () => {
    setEditRegle(null);
    setEditParam(null);
    setRegleForm(initialRegleForm);
    setParamForm(initialParamForm);
  };

  // Mise à jour règle
  const handleUpdateRegle = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const updateData = {
        nomRegle: regleForm.nom,
        description: regleForm.description,
        niveauCritique: parseInt(regleForm.gravite),
        is_active: regleForm.active
      };
      await regleConformiteService.updateRegle(editRegle.idRegle || editRegle.id, updateData);
      closeEdit();
      await fetchData();
    } catch (err) {
      alert('Erreur lors de la mise à jour.');
    } finally {
      setSaving(false);
    }
  };

  // Mise à jour paramètre
  const handleUpdateParam = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const updateData = {
        nom: paramForm.nom,
        seuilMin: parseInt(paramForm.seuilMin),
        seuilMax: parseInt(paramForm.seuilMax),
        unite: paramForm.unite,
        regle: paramForm.regle
      };
      await parametreConformiteService.updateParametre(editParam.idParametre || editParam.id, updateData);
      closeEdit();
      await fetchData();
    } catch (err) {
      alert('Erreur lors de la mise à jour.');
    } finally {
      setSaving(false);
    }
  };

  // Ajout règle
  const handleAddRegle = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const newRegle = {
        nomRegle: addRegleForm.nom,
        description: addRegleForm.description,
        typeRegle: 'SECURITE',
        niveauCritique: parseInt(addRegleForm.gravite),
        is_active: addRegleForm.active
      };
      await regleConformiteService.createRegle(newRegle);
      setAddRegleOpen(false);
      setAddRegleForm(initialRegleForm);
      await fetchData();
    } catch (err) {
      alert('Erreur lors de l\'ajout.');
    } finally {
      setSaving(false);
    }
  };

  // Initialiser la surveillance
  const handleInitialiserSurveillance = async () => {
    try {
      // Ici vous pouvez ajouter la logique pour initialiser la surveillance
      alert('Surveillance initialisée avec succès !');
    } catch (err) {
      alert('Erreur lors de l\'initialisation de la surveillance.');
    }
  };

  // Ajout paramètre
  const handleAddParam = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const newParam = {
        nom: addParamForm.nom,
        seuilMin: parseInt(addParamForm.seuilMin),
        seuilMax: parseInt(addParamForm.seuilMax),
        unite: addParamForm.unite,
        regle: addParamForm.regle
      };
      await parametreConformiteService.createParametre(newParam);
      setAddParamOpen(false);
      setAddParamForm(initialParamForm);
      await fetchData();
    } catch (err) {
      alert('Erreur lors de l\'ajout.');
    } finally {
      setSaving(false);
    }
  };

  // Pré-remplir avec un paramètre médical
  const preRemplirParametreMedical = (parametre) => {
    setAddParamForm({
      nom: parametre.nom,
      seuilMin: parametre.seuilMin,
      seuilMax: parametre.seuilMax,
      unite: parametre.unite,
      regle: ''
    });
    setShowParametresMedicaux(false);
    setAddParamOpen(true);
  };

  // Pré-remplir avec une alerte de sécurité
  const preRemplirAlerteSecurite = (alerte) => {
    setAddParamForm({
      nom: alerte.nom,
      seuilMin: alerte.seuilMin,
      seuilMax: alerte.seuilMax || '',
      unite: alerte.unite,
      regle: ''
    });
    setShowAlertesSecurite(false);
    setAddParamOpen(true);
  };

  // Toggle actif/inactif pour une règle
  const handleToggleActive = async (regle) => {
    try {
      const updateData = {
        nomRegle: regle.nomRegle || regle.nom || regle.name,
        description: regle.description,
        typeRegle: regle.typeRegle || 'SECURITE',
        niveauCritique: regle.niveauCritique || regle.gravite,
        is_active: !regle.is_active
      };
      await regleConformiteService.updateRegle(regle.idRegle || regle.id, updateData);
      await fetchData();
    } catch (err) {
      alert('Erreur lors de la modification du statut.');
    }
  };

  // Validation des formulaires
  const isEditParamValid = paramForm.seuilMin !== '' && paramForm.seuilMax !== '' && 
                          Number(paramForm.seuilMin) <= Number(paramForm.seuilMax);
  const isAddParamValid = addParamForm.seuilMin !== '' && addParamForm.seuilMax !== '' && 
                         Number(addParamForm.seuilMin) <= Number(addParamForm.seuilMax);

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
          🔒 Configuration des Alertes de Sécurité
        </h1>
        <p className="text-gray-600">
          Gestion des règles de conformité et des seuils d'alertes de sécurité
        </p>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Section Règles de conformité */}
      <div className="bg-white rounded-lg shadow-md mb-8">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">Règles de conformité</h2>
            <button 
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              onClick={() => setAddRegleOpen(true)}
            >
              + Ajouter une règle
            </button>
          </div>
        </div>
            <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nom</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Gravité</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Active</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
            <tbody className="bg-white divide-y divide-gray-200">
                  {regles.length === 0 ? (
                    <tr><td colSpan={6} className="text-center py-4 text-gray-500">Aucune règle trouvée.</td></tr>
                  ) : regles.map((regle) => (
                <tr key={regle.idRegle || regle.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {regle.idRegle || regle.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {regle.nomRegle || regle.nom || regle.name}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {regle.description}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {regle.niveauCritique || regle.gravite}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => handleToggleActive(regle)}
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        regle.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {regle.is_active ? 'Active' : 'Inactive'}
                    </button>
                      </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button
                      className="text-blue-600 hover:text-blue-900 mr-4"
                          onClick={() => openEditRegle(regle)}
                        >
                          Éditer
                        </button>
                        <button
                      className="text-red-600 hover:text-red-900"
                      onClick={() => handleDeleteRegle(regle.idRegle || regle.id)}
                          disabled={deletingId === (regle.idRegle || regle.id) && deleteType === 'regle'}
                        >
                          {deletingId === (regle.idRegle || regle.id) && deleteType === 'regle' ? 'Suppression...' : 'Supprimer'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

      {/* Section Paramètres / Seuils associés */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">Paramètres / Seuils associés</h2>
            <div className="flex gap-2">
              <button 
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
                onClick={() => setShowParametresMedicaux(true)}
              >
                + Paramètres médicaux courants
              </button>
              <button 
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
                onClick={() => setShowAlertesSecurite(true)}
              >
                + Alertes de sécurité
              </button>
              <button 
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                onClick={() => setAddParamOpen(true)}
              >
                + Ajouter un paramètre
              </button>
            </div>
          </div>
        </div>
            <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nom</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Seuil Min</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Seuil Max</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Unité</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Règle associée</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
            <tbody className="bg-white divide-y divide-gray-200">
                  {parametres.length === 0 ? (
                    <tr><td colSpan={7} className="text-center py-4 text-gray-500">Aucun paramètre trouvé.</td></tr>
                  ) : parametres.map((param) => {
                    // Chercher le nom de la règle associée
                    let regleNom = '';
                    if (param.regle && typeof param.regle === 'object') {
                      regleNom = param.regle.nomRegle || param.regle.nom || param.regle.name || '';
                    } else if (param.regle) {
                      // Si c'est juste un ID, essayer de le retrouver dans reglesList
                      const r = reglesList.find(r => (r.id || r.idRegle) == param.regle);
                      regleNom = r ? (r.nomRegle || r.nom || r.name) : param.regle;
                    }
                    return (
                  <tr key={param.idParametre || param.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {param.idParametre || param.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {param.nom}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {param.seuilMin}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {param.seuilMax || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {param.unite}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {regleNom}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button 
                        className="text-blue-600 hover:text-blue-900 mr-4"
                        onClick={() => openEditParam(param)}
                      >
                        Éditer
                      </button>
                      <button 
                        className="text-red-600 hover:text-red-900"
                        onClick={() => handleDeleteParametre(param.idParametre || param.id)}
                        disabled={deletingId === (param.idParametre || param.id) && deleteType === 'parametre'}
                      >
                        {deletingId === (param.idParametre || param.id) && deleteType === 'parametre' ? 'Suppression...' : 'Supprimer'}
                      </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

      {/* Modales d'édition et d'ajout */}
      {/* Modale édition règle */}
      {editRegle && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-40">
          <form onSubmit={handleUpdateRegle} className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 max-w-md w-full">
            <h3 className="text-lg font-bold mb-4">Modifier la règle</h3>
            <label className="block mb-2">Nom
              <input className="w-full p-2 border rounded" value={regleForm.nom} onChange={e => setRegleForm(f => ({...f, nom: e.target.value}))} required />
            </label>
            <label className="block mb-2">Description
              <textarea className="w-full p-2 border rounded" value={regleForm.description} onChange={e => setRegleForm(f => ({...f, description: e.target.value}))} required />
            </label>
            <label className="block mb-2">Gravité
              <input className="w-full p-2 border rounded" value={regleForm.gravite} onChange={e => setRegleForm(f => ({...f, gravite: e.target.value}))} required />
            </label>
            <label className="block mb-2">Active
              <select className="w-full p-2 border rounded" value={regleForm.active} onChange={e => setRegleForm(f => ({...f, active: e.target.value === 'true'}))}>
                <option value="true">Oui</option>
                <option value="false">Non</option>
              </select>
            </label>
            <div className="flex justify-end gap-2 mt-4">
              <button type="button" className="px-4 py-2 bg-gray-300 rounded" onClick={closeEdit}>Annuler</button>
              <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded" disabled={saving}>{saving ? 'Enregistrement...' : 'Enregistrer'}</button>
            </div>
          </form>
        </div>
      )}
      {/* Modale édition paramètre */}
      {editParam && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-40">
          <form onSubmit={handleUpdateParam} className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 max-w-md w-full">
            <h3 className="text-lg font-bold mb-4">Modifier le paramètre/seuil</h3>
            <label className="block mb-2">Nom
              <input className="w-full p-2 border rounded" value={paramForm.nom} onChange={e => setParamForm(f => ({...f, nom: e.target.value}))} required />
            </label>
            <label className="block mb-2">Seuil minimum
              <input type="number" className="w-full p-2 border rounded" value={paramForm.seuilMin} onChange={e => setParamForm(f => ({...f, seuilMin: e.target.value}))} required />
            </label>
            <label className="block mb-2">Seuil maximum
              <input type="number" className="w-full p-2 border rounded" value={paramForm.seuilMax} onChange={e => setParamForm(f => ({...f, seuilMax: e.target.value}))} required />
            </label>
            <label className="block mb-2">Unité
              <input className="w-full p-2 border rounded" value={paramForm.unite} onChange={e => setParamForm(f => ({...f, unite: e.target.value}))} required />
            </label>
            <label className="block mb-2">Règle associée
              <select className="w-full p-2 border rounded" value={paramForm.regle} onChange={e => setParamForm(f => ({...f, regle: e.target.value}))} required>
                <option value="">-- Choisir une règle --</option>
                    {reglesList.filter(r => r.is_active).map(r => <option key={r.idRegle || r.id} value={r.idRegle || r.id}>{r.nomRegle || r.nom || r.name}</option>)}
              </select>
            </label>
            {paramForm.seuilMin !== '' && paramForm.seuilMax !== '' && Number(paramForm.seuilMin) > Number(paramForm.seuilMax) && (
              <div className="text-red-600 text-sm mb-2">Le seuil minimum doit être inférieur ou égal au seuil maximum.</div>
            )}
            <div className="flex justify-end gap-2 mt-4">
              <button type="button" className="px-4 py-2 bg-gray-300 rounded" onClick={closeEdit}>Annuler</button>
              <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded" disabled={saving || !isEditParamValid}>{saving ? 'Enregistrement...' : 'Enregistrer'}</button>
            </div>
          </form>
        </div>
      )}
      {/* Modale ajout règle */}
      {addRegleOpen && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-40">
          <form onSubmit={handleAddRegle} className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 max-w-md w-full">
            <h3 className="text-lg font-bold mb-4">Ajouter une règle de conformité</h3>
            <label className="block mb-2">Nom
              <input className="w-full p-2 border rounded" value={addRegleForm.nom} onChange={e => setAddRegleForm(f => ({...f, nom: e.target.value}))} required />
            </label>
            <label className="block mb-2">Description
              <textarea className="w-full p-2 border rounded" value={addRegleForm.description} onChange={e => setAddRegleForm(f => ({...f, description: e.target.value}))} required />
            </label>
            <label className="block mb-2">Gravité
              <input className="w-full p-2 border rounded" value={addRegleForm.gravite} onChange={e => setAddRegleForm(f => ({...f, gravite: e.target.value}))} required />
            </label>
            <label className="block mb-2">Active
              <select className="w-full p-2 border rounded" value={addRegleForm.active} onChange={e => setAddRegleForm(f => ({...f, active: e.target.value === 'true'}))}>
                <option value="true">Oui</option>
                <option value="false">Non</option>
              </select>
            </label>
            <div className="flex justify-end gap-2 mt-4">
              <button type="button" className="px-4 py-2 bg-gray-300 rounded" onClick={() => setAddRegleOpen(false)}>Annuler</button>
              <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded" disabled={saving}>{saving ? 'Ajout...' : 'Ajouter'}</button>
            </div>
          </form>
        </div>
      )}

      {/* Modale ajout règle */}
      {/* Modale ajout paramètre */}
      {addParamOpen && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-40">
          <form onSubmit={handleAddParam} className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 max-w-md w-full">
            <h3 className="text-lg font-bold mb-4">Ajouter un paramètre/seuil</h3>
            <label className="block mb-2">Nom
              <input className="w-full p-2 border rounded" value={addParamForm.nom} onChange={e => setAddParamForm(f => ({...f, nom: e.target.value}))} required />
            </label>
      <label className="block mb-2">Règle associée
        <select className="w-full p-2 border rounded" value={addParamForm.regle} onChange={e => setAddParamForm(f => ({...f, regle: e.target.value}))} required>
          <option value="">-- Choisir une règle --</option>
          {reglesList.filter(r => r.is_active).map(r => <option key={r.idRegle || r.id} value={r.idRegle || r.id}>{r.nomRegle || r.nom || r.name}</option>)}
        </select>
      </label>

      {shouldDisplaySeuils(addParamForm.regle) ? (
        <>
            <label className="block mb-2">Seuil minimum
              <input type="number" className="w-full p-2 border rounded" value={addParamForm.seuilMin} onChange={e => setAddParamForm(f => ({...f, seuilMin: e.target.value}))}  />
            </label>
            <label className="block mb-2">Seuil maximum
              <input type="number" className="w-full p-2 border rounded" value={addParamForm.seuilMax} onChange={e => setAddParamForm(f => ({...f, seuilMax: e.target.value}))}  />
            </label>
            <label className="block mb-2">Unité
              <input className="w-full p-2 border rounded" value={addParamForm.unite} onChange={e => setAddParamForm(f => ({...f, unite: e.target.value}))}  />
            </label>
        </>
      ) : (
        <div className="text-sm text-blue-600 mb-4">Aucun seuil requis pour cette règle.</div>
      )}

            <div className="flex justify-end gap-2 mt-4">
              <button type="button" className="px-4 py-2 bg-gray-300 rounded" onClick={() => setAddParamOpen(false)}>Annuler</button>
        <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded" disabled={saving || (!shouldDisplaySeuils(addParamForm.regle) ? false : !isAddParamValid)}>{saving ? 'Ajout...' : 'Ajouter'}</button>
            </div>
          </form>
        </div>
      )}

      {/* Modale de sélection des paramètres médicaux courants */}
      {showParametresMedicaux && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-40">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">Paramètres médicaux courants</h3>
              <button 
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                onClick={() => setShowParametresMedicaux(false)}
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Sélectionnez un paramètre médical pour pré-remplir automatiquement le formulaire d'ajout avec les seuils recommandés.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {parametresMedicauxCourants.map((parametre, index) => (
                <div 
                  key={index}
                  className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                  onClick={() => preRemplirParametreMedical(parametre)}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-semibold text-gray-900 dark:text-white">{parametre.nom}</h4>
                    <span className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded">
                      {parametre.unite}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    {parametre.description}
                  </p>
                  <div className="text-sm text-gray-700 dark:text-gray-300">
                    <span className="font-medium">Seuils :</span> {parametre.seuilMin} - {parametre.seuilMax} {parametre.unite}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 flex justify-end">
              <button 
                className="px-4 py-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-400 dark:hover:bg-gray-500"
                onClick={() => setShowParametresMedicaux(false)}
              >
                Annuler
              </button>
            </div>
          </div>
        </div>
          )}

      {/* Modale de sélection des alertes de sécurité */}
      {showAlertesSecurite && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-40">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">Alertes de sécurité</h3>
              <button 
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                onClick={() => setShowAlertesSecurite(false)}
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Sélectionnez une alerte de sécurité pour pré-remplir automatiquement le formulaire d'ajout avec les seuils recommandés.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {alertesSecuriteCourantes.map((alerte, index) => (
                <div 
                  key={index}
                  className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                  onClick={() => preRemplirAlerteSecurite(alerte)}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-semibold text-gray-900 dark:text-white">{alerte.nom}</h4>
                    <span className="text-xs bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 px-2 py-1 rounded">
                      {alerte.unite}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    {alerte.description}
                  </p>
                  <div className="text-sm text-gray-700 dark:text-gray-300">
                    <span className="font-medium">Seuil :</span> {alerte.seuilMin} {alerte.unite}
                    {alerte.seuilMax && ` - ${alerte.seuilMax}`}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 flex justify-end">
              <button 
                className="px-4 py-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-400 dark:hover:bg-gray-500"
                onClick={() => setShowAlertesSecurite(false)}
              >
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
    //   </div>
    // </>
  );
};

export default ConfigAlertesSecurite; 
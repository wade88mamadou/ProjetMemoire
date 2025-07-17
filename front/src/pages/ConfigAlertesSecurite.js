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
      nom: regle.nomRegle || regle.nom || '',
      description: regle.description || '',
      gravite: regle.niveauCritique !== undefined ? regle.niveauCritique : (regle.gravite || ''),
      active: regle.active !== undefined ? regle.active : true,
      typeRegle: regle.typeRegle || 'RGPD',
    });
  };
  // Ouvrir la modale d'édition paramètre
  const openEditParam = (param) => {
    setEditParam(param);
    setParamForm({
      nom: param.nom || '',
      valeur: param.valeur || '',
      unite: param.unite || '',
      regle: param.regle || param.regle_conformite || '',
    });
  };
  // Fermer les modales
  const closeEdit = () => {
    setEditRegle(null);
    setEditParam(null);
    setRegleForm(initialRegleForm);
    setParamForm(initialParamForm);
  };
  // Soumettre la modification règle (mapping corrigé)
  const handleUpdateRegle = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const data = {
        nomRegle: regleForm.nom,
        description: regleForm.description,
        typeRegle: regleForm.typeRegle || 'RGPD',
        niveauCritique: parseInt(regleForm.gravite, 10) || 3,
        active: regleForm.active === true || regleForm.active === 'true',
      };
      await regleConformiteService.updateRegle(editRegle.idRegle || editRegle.id, data);
      await fetchData(); // Rafraîchir la liste après édition
      closeEdit();
    } catch (err) {
      alert('Erreur lors de la modification.');
    } finally {
      setSaving(false);
    }
  };
  // Soumettre la modification paramètre
  const handleUpdateParam = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await parametreConformiteService.updateParametre(editParam.idParametre || editParam.id, paramForm);
      await fetchData();
      closeEdit();
    } catch (err) {
      alert('Erreur lors de la modification.');
    } finally {
      setSaving(false);
    }
  };

  // Ajout règle (mapping corrigé et typage)
  const handleAddRegle = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      // Correction du mapping des champs pour l'API Django
      const data = {
        nomRegle: addRegleForm.nom,
        description: addRegleForm.description,
        typeRegle: addRegleForm.typeRegle || 'RGPD',
        niveauCritique: 3, // Critique = 3, Warning = 2, Info = 1 (exemple)
        active: addRegleForm.active === true || addRegleForm.active === 'true',
      };
      await regleConformiteService.createRegle(data);
      await fetchData();
      setAddRegleOpen(false);
      setAddRegleForm(initialRegleForm);
    } catch (err) {
      alert('Erreur lors de l\'ajout.');
    } finally {
      setSaving(false);
    }
  };

  // Ajout du bouton d'initialisation (mapping corrigé)
  const handleInitialiserSurveillance = async () => {
    setSaving(true);
    try {
      // 1. Créer la règle RGPD si elle n'existe pas
      let regle = regles.find(r => (r.nomRegle || r.nom) === 'Surveillance paramètres vitaux');
      if (!regle) {
        const regleData = {
          nomRegle: 'Surveillance paramètres vitaux',
          description: 'Règle RGPD pour la surveillance des paramètres vitaux',
          typeRegle: 'RGPD',
          niveauCritique: 3,
          active: true,
        };
        const res = await regleConformiteService.createRegle(regleData);
        regle = res.data;
      }
      // 2. Créer les paramètres médicaux courants associés à cette règle
      for (const param of parametresMedicauxCourants) {
        // Vérifier si le paramètre existe déjà
        const existe = parametres.some(p => p.nom === param.nom && (p.regle === regle.idRegle || p.regle === regle.id));
        if (!existe) {
          await parametreConformiteService.createParametre({
            nom: param.nom,
            seuilMin: param.seuilMin,
            seuilMax: param.seuilMax,
            unite: param.unite,
            regle: regle.idRegle || regle.id
          });
        }
      }
      await fetchData();
      alert('Surveillance médicale initialisée avec succès !');
    } catch (err) {
      alert('Erreur lors de l\'initialisation.');
    } finally {
      setSaving(false);
    }
  };
  // Ajout paramètre
  const handleAddParam = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await parametreConformiteService.createParametre(addParamForm);
      await fetchData();
      setAddParamOpen(false);
      setAddParamForm(initialParamForm);
    } catch (err) {
      alert('Erreur lors de l\'ajout.');
    } finally {
      setSaving(false);
    }
  };

  // Validation ajout paramètre
  const isAddParamValid = addParamForm.nom && addParamForm.seuilMin !== '' && addParamForm.seuilMax !== '' && addParamForm.unite && addParamForm.regle && Number(addParamForm.seuilMin) <= Number(addParamForm.seuilMax);
  // Validation édition paramètre
  const isEditParamValid = paramForm.nom && paramForm.seuilMin !== '' && paramForm.seuilMax !== '' && paramForm.unite && paramForm.regle && Number(paramForm.seuilMin) <= Number(paramForm.seuilMax);

  // Fonction pour pré-remplir le formulaire avec un paramètre médical
  const preRemplirParametreMedical = (parametre) => {
    setAddParamForm({
      nom: parametre.nom,
      seuilMin: parametre.seuilMin.toString(),
      seuilMax: parametre.seuilMax.toString(),
      unite: parametre.unite,
      regle: ''
    });
    setShowParametresMedicaux(false);
    setAddParamOpen(true);
  };

  // Dans le composant principal :
  const handleToggleActive = async (regle) => {
    try {
      const regleId = regle.idRegle || regle.id;
      // Préparer le payload complet attendu par le backend
      const payload = {
        nomRegle: regle.nomRegle || regle.nom || '',
        description: regle.description || '',
        typeRegle: regle.typeRegle || 'RGPD',
        niveauCritique: regle.niveauCritique !== undefined ? regle.niveauCritique : (regle.gravite || 3),
        is_active: !regle.is_active
      };
      await regleConformiteService.updateRegle(regleId, payload);
      setRegles(regles =>
        regles.map(r =>
          (r.idRegle || r.id) === regleId ? { ...r, is_active: !regle.is_active } : r
        )
      );
      // Rafraîchir la liste déroulante des règles
      const res = await regleConformiteService.getRegles();
      const data = Array.isArray(res.data) ? res.data : (res.data.results || []);
      setReglesList(data);
    } catch (error) {
      alert("Erreur lors de l'activation/désactivation !");
    }
  };

  return (
    <div className="p-6 space-y-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Configuration des alertes de sécurité</h2>
        {/* Bouton supprimé : Initialiser la surveillance médicale */}
      </div>
      {loading ? (
        <div className="text-center text-gray-600 dark:text-gray-300">Chargement...</div>
      ) : error ? (
        <div className="text-center text-red-600">{error}</div>
      ) : (
        <>
          {/* Boutons d'ajout au-dessus de chaque tableau */}
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-xl font-semibold text-blue-700 dark:text-blue-300">Règles de conformité</h3>
            <button className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700" onClick={() => setAddRegleOpen(true)}>+ Ajouter une règle</button>
          </div>
          {/* Tableau des règles de conformité */}
          <div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700 bg-white dark:bg-gray-800 rounded shadow">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">ID</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Nom</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Description</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Gravité</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Active</th>
                    <th className="px-4 py-2"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {regles.length === 0 ? (
                    <tr><td colSpan={6} className="text-center py-4 text-gray-500">Aucune règle trouvée.</td></tr>
                  ) : regles.map((regle) => (
                    <tr key={regle.idRegle || regle.id} className="hover:bg-gray-100 dark:hover:bg-gray-700">
                      <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">{regle.idRegle || regle.id}</td>
                      <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">{regle.nomRegle || regle.nom || regle.name}</td>
                      <td className="px-4 py-2 text-sm text-gray-700 dark:text-gray-200">{regle.description}</td>
                      <td className="px-4 py-2 text-sm text-gray-700 dark:text-gray-200">{regle.gravite || regle.niveauCritique || regle.severite}</td>
                      <td className="px-4 py-2 text-sm text-gray-700 dark:text-gray-200">
                        <input
                          type="checkbox"
                          checked={regle.is_active}
                          onChange={() => handleToggleActive(regle)}
                          className="form-checkbox h-5 w-5 text-blue-600"
                        />
                      </td>
                      <td className="px-4 py-2 text-right">
                        {/* Actions à venir : éditer, supprimer, activer/désactiver */}
                        <button
                          className="text-blue-600 hover:underline mr-2"
                          onClick={() => openEditRegle(regle)}
                        >
                          Éditer
                        </button>
                        <button
                          className="text-red-600 hover:underline"
                          disabled={deletingId === (regle.idRegle || regle.id) && deleteType === 'regle'}
                          onClick={() => handleDeleteRegle(regle.idRegle || regle.id)}
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

          {/* Boutons d'ajout au-dessus de chaque tableau */}
          <div className="flex justify-between items-center mt-8 mb-2">
            <h3 className="text-xl font-semibold text-blue-700 dark:text-blue-300">Paramètres / Seuils associés</h3>
            <div className="flex gap-2">
              <button 
                className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
                onClick={() => setShowParametresMedicaux(true)}
              >
                + Paramètres médicaux courants
              </button>
              <button 
                className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700" 
                onClick={() => setAddParamOpen(true)}
              >
                + Ajouter un paramètre
              </button>
            </div>
          </div>
          {/* Tableau des paramètres/seuils */}
          <div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700 bg-white dark:bg-gray-800 rounded shadow">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">ID</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Nom</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Seuil Min</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Seuil Max</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Unité</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Règle associée</th>
                    <th className="px-4 py-2"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
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
                      <tr key={param.idParametre || param.id} className="hover:bg-gray-100 dark:hover:bg-gray-700">
                        <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">{param.idParametre || param.id}</td>
                        <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">{param.nom}</td>
                        <td className="px-4 py-2 text-sm text-gray-700 dark:text-gray-200">{param.seuilMin}</td>
                        <td className="px-4 py-2 text-sm text-gray-700 dark:text-gray-200">{param.seuilMax}</td>
                        <td className="px-4 py-2 text-sm text-gray-700 dark:text-gray-200">{param.unite}</td>
                        <td className="px-4 py-2 text-sm text-gray-700 dark:text-gray-200">{regleNom}</td>
                        <td className="px-4 py-2 text-right">
                          <button className="text-blue-600 hover:underline mr-2" onClick={() => openEditParam(param)}>Éditer</button>
                          <button className="text-red-600 hover:underline" disabled={deletingId === (param.idParametre || param.id) && deleteType === 'parametre'} onClick={() => handleDeleteParametre(param.idParametre || param.id)}>{deletingId === (param.idParametre || param.id) && deleteType === 'parametre' ? 'Suppression...' : 'Supprimer'}</button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

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
      {/* Modale ajout paramètre */}
      {addParamOpen && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-40">
          <form onSubmit={handleAddParam} className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 max-w-md w-full">
            <h3 className="text-lg font-bold mb-4">Ajouter un paramètre/seuil</h3>
            <label className="block mb-2">Nom
              <input className="w-full p-2 border rounded" value={addParamForm.nom} onChange={e => setAddParamForm(f => ({...f, nom: e.target.value}))} required />
            </label>
            <label className="block mb-2">Seuil minimum
              <input type="number" className="w-full p-2 border rounded" value={addParamForm.seuilMin} onChange={e => setAddParamForm(f => ({...f, seuilMin: e.target.value}))} required />
            </label>
            <label className="block mb-2">Seuil maximum
              <input type="number" className="w-full p-2 border rounded" value={addParamForm.seuilMax} onChange={e => setAddParamForm(f => ({...f, seuilMax: e.target.value}))} required />
            </label>
            <label className="block mb-2">Unité
              <input className="w-full p-2 border rounded" value={addParamForm.unite} onChange={e => setAddParamForm(f => ({...f, unite: e.target.value}))} required />
            </label>
            <label className="block mb-2">Règle associée
              <select className="w-full p-2 border rounded" value={addParamForm.regle} onChange={e => setAddParamForm(f => ({...f, regle: e.target.value}))} required>
                <option value="">-- Choisir une règle --</option>
                    {reglesList.filter(r => r.is_active).map(r => <option key={r.idRegle || r.id} value={r.idRegle || r.id}>{r.nomRegle || r.nom || r.name}</option>)}
              </select>
            </label>
            {addParamForm.seuilMin !== '' && addParamForm.seuilMax !== '' && Number(addParamForm.seuilMin) > Number(addParamForm.seuilMax) && (
              <div className="text-red-600 text-sm mb-2">Le seuil minimum doit être inférieur ou égal au seuil maximum.</div>
            )}
            <div className="flex justify-end gap-2 mt-4">
              <button type="button" className="px-4 py-2 bg-gray-300 rounded" onClick={() => setAddParamOpen(false)}>Annuler</button>
              <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded" disabled={saving || !isAddParamValid}>{saving ? 'Ajout...' : 'Ajouter'}</button>
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
        </>
      )}
    </div>
  );
};

export default ConfigAlertesSecurite; 
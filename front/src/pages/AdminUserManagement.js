import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/admin/users/';
const MEDECINS_API_URL = 'http://localhost:8000/api/medecins/';

const roleLabels = {
  'ADMIN': 'Administrateur',
  'MEDECIN': 'Médecin',
  'user_simple': 'Utilisateur simple',
};

const emptyForm = {
  username: '',
  email: '',
  password: '',
  password_confirm: '',
  first_name: '',
  last_name: '',
  role: 'MEDECIN',
  specialite: '',
  is_active: true,
};

// Modal de confirmation stylisée
const ConfirmModal = ({ open, onClose, onConfirm, message }) => {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-sm w-full text-center border-t-4 border-red-500">
        <h2 className="text-xl font-bold text-red-600 mb-4">Confirmation</h2>
        <p className="mb-6 text-gray-700">{message}</p>
        <div className="flex justify-center gap-4">
          <button
            className="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded"
            onClick={onClose}
          >
            Annuler
          </button>
          <button
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded"
            onClick={onConfirm}
          >
            Confirmer
          </button>
        </div>
      </div>
    </div>
  );
};

const AdminUserManagement = ({ onUserChange, onlyForMedecinId }) => {
  const { user, isAdmin } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updatingId, setUpdatingId] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [editUserId, setEditUserId] = useState(null);
  const [formError, setFormError] = useState(null);
  const [addRoleSelect, setAddRoleSelect] = useState('');
  const [medecins, setMedecins] = useState([]);
  const [showSuccessCard, setShowSuccessCard] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [userToDelete, setUserToDelete] = useState(null);

  // Fetch médecins si besoin
  useEffect(() => {
    if ((showAddForm && form.role === 'user_simple') || (showEditForm && form.role === 'user_simple')) {
      const fetchMedecins = async () => {
        try {
          const token = localStorage.getItem('token');
          const res = await axios.get(MEDECINS_API_URL, {
            headers: { Authorization: `Bearer ${token}` }
          });
          setMedecins(res.data);
        } catch (err) {
          setMedecins([]);
        }
      };
      fetchMedecins();
    }
  }, [showAddForm, showEditForm, form.role]);

  useEffect(() => {
    if (isAdmin()) {
      fetchUsers();
    }
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(API_URL, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      let userList = [];
      if (Array.isArray(res.data)) {
        userList = res.data;
      } else if (Array.isArray(res.data.results)) {
        userList = res.data.results;
      }
      
      // Filtrer pour exclure les admins de la liste
      const filteredUsers = userList.filter(u => u.role !== 'ADMIN');
      setUsers(filteredUsers);
    } catch (err) {
      setError("Erreur lors du chargement des utilisateurs");
    } finally {
      setLoading(false);
    }
  };



  const handleDelete = (id) => {
    setUserToDelete(id);
    setShowConfirmModal(true);
  };

  const confirmDelete = async () => {
    setUpdatingId(userToDelete);
    setShowConfirmModal(false);
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`http://localhost:8000/api/utilisateurs/${userToDelete}/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUsers(users => users.filter(u => u.id !== userToDelete));
    } catch (err) {
      alert("Erreur lors de la suppression");
    } finally {
      setUpdatingId(null);
      setUserToDelete(null);
    }
  };

  // Ajout d'un utilisateur
  const handleAddUser = async (e) => {
    e.preventDefault();
    setFormError(null);
    
    // Validation personnalisée pour le médecin
    if (form.role === 'user_simple' && !form.medecin) {
      setFormError('Veuillez choisir le médecin.');
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      const payload = { ...form };
      if (!payload.password || !payload.password_confirm) {
        setFormError('Le mot de passe est requis.');
        return;
      }
      await axios.post(API_URL, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setShowAddForm(false);
      setForm(emptyForm);
      fetchUsers();
      
      // Afficher la carte de succès
      setSuccessMessage(`✅ L'utilisateur "${form.username}" a été créé avec succès !`);
      setShowSuccessCard(true);
      
      // Rafraîchir les statistiques du dashboard
      if (onUserChange) {
        onUserChange();
      }
      
      // Masquer la carte après 3 secondes
      setTimeout(() => {
        setShowSuccessCard(false);
        setSuccessMessage('');
      }, 3000);
    } catch (err) {
      // Ajoute ce log :
      console.log("Erreur API création utilisateur:", err.response?.data || err.message);
      
      // Gestion des erreurs spécifiques
      if (err.response?.data?.medecin) {
        setFormError('Veuillez choisir le médecin.');
      } else {
      setFormError(
        err.response?.data?.detail ||
        JSON.stringify(err.response?.data) ||
        "Erreur lors de l'ajout de l'utilisateur"
      );
      }
    }
  };

  // Préparer le formulaire d'édition
  const openEditForm = (u) => {
    setEditUserId(u.id);
    setForm({
      username: u.username,
      email: u.email,
      password: '',
      password_confirm: '',
      first_name: u.first_name || '',
      last_name: u.last_name || '',
      role: u.role,
      specialite: u.specialite || '',
      is_active: u.is_active,
    });
    setShowEditForm(true);
    setFormError(null);
  };

  // Modifier un utilisateur
  const handleEditUser = async (e) => {
    e.preventDefault();
    setFormError(null);
    
    // Validation personnalisée pour le médecin
    if (form.role === 'user_simple' && !form.medecin) {
      setFormError('Veuillez choisir le médecin.');
      return;
    }
    
    // Empêcher l'admin de se désactiver lui-même
    if (editUserId === user.id && !form.is_active) {
      setFormError("Vous ne pouvez pas vous désactiver vous-même.");
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      const payload = { ...form };
      
      // Si mot de passe vide, ne pas l'envoyer
      if (!payload.password) {
        delete payload.password;
        delete payload.password_confirm;
      }
      
      // S'assurer que is_active est bien un booléen
      payload.is_active = Boolean(payload.is_active);
      
      console.log('Payload envoyé:', payload); // Debug
      
      await axios.patch(`${API_URL}${editUserId}/`, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log('Modification réussie'); // Debug
      
      // Afficher la carte de succès
      if (!payload.is_active) {
        setSuccessMessage(`✅ L'utilisateur "${form.username}" a été désactivé avec succès.\n\nIl ne pourra plus se connecter jusqu'à ce que vous le réactiviez.`);
      } else {
        setSuccessMessage(`✅ L'utilisateur "${form.username}" a été activé avec succès.\n\nIl peut maintenant se connecter à l'application.`);
      }
      setShowSuccessCard(true);
      
      setShowEditForm(false);
      setEditUserId(null);
      setForm(emptyForm);
      fetchUsers();
      
      // Rafraîchir les statistiques du dashboard
      if (onUserChange) {
        onUserChange();
      }
      
      // Masquer la carte après 3 secondes
      setTimeout(() => {
        setShowSuccessCard(false);
        setSuccessMessage('');
      }, 3000);
    } catch (err) {
      console.error('Erreur modification:', err.response?.data || err.message); // Debug
      
      // Gestion des erreurs spécifiques
      if (err.response?.data?.medecin) {
        setFormError('Veuillez choisir le médecin.');
      } else {
      setFormError("Erreur lors de la modification de l'utilisateur");
      }
    }
  };

  if (!isAdmin() && !onlyForMedecinId) {
    return <div className="p-8 text-center text-red-600 font-bold">Accès réservé à l'administrateur.</div>;
  }

  // Filtrage pour médecin : n'afficher que les users simples rattachés
  const filteredUsers = onlyForMedecinId
    ? users.filter(u => u.role === 'user_simple' && String(u.medecin) === String(onlyForMedecinId))
    : users;

  return (
    <div className="p-4 bg-gray-50 dark:bg-gray-900 min-h-screen">
      {/* Carte de confirmation de succès */}
      {showSuccessCard && (
        <div className="fixed top-4 right-4 z-50 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded shadow-lg max-w-md">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <div className="whitespace-pre-line">{successMessage}</div>
            </div>
            <button
              onClick={() => setShowSuccessCard(false)}
              className="ml-4 text-green-500 hover:text-green-700"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      )}

      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">Gestion des utilisateurs</h1>
        {/* Bouton vert classique pour ajouter un utilisateur - réservé à l'admin */}
        {!showAddForm && !showEditForm && !onlyForMedecinId && (
          <button
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded shadow font-bold"
            onClick={() => {
              setForm({ ...emptyForm });
              setShowAddForm(true);
              setShowEditForm(false);
            }}
          >
            Ajouter un utilisateur
          </button>
        )}
        {/* Bouton Annuler si le formulaire est ouvert */}
        {(showAddForm || showEditForm) && !onlyForMedecinId && (
        <button
          className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded shadow"
            onClick={() => { setShowAddForm(false); setShowEditForm(false); setForm(emptyForm); }}
        >
            Annuler
        </button>
        )}
      </div>

      {/* Formulaire d'ajout - réservé à l'admin */}
      {showAddForm && !onlyForMedecinId && (
        <form className="bg-gray-100 dark:bg-gray-800 p-4 rounded mb-6" onSubmit={handleAddUser}>
          <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-100">Ajouter un nouvel utilisateur</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Nom d'utilisateur *</label>
              <input type="text" className="border rounded px-2 py-1 w-full bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100" required value={form.username} onChange={e => setForm(f => ({ ...f, username: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Email *</label>
              <input type="email" className="border rounded px-2 py-1 w-full bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100" required value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Prénom</label>
              <input type="text" className="border rounded px-2 py-1 w-full bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100" value={form.first_name} onChange={e => setForm(f => ({ ...f, first_name: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Nom</label>
              <input type="text" className="border rounded px-2 py-1 w-full bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100" value={form.last_name} onChange={e => setForm(f => ({ ...f, last_name: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Mot de passe *</label>
              <input type="password" className="border rounded px-2 py-1 w-full bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100" required value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Confirmer le mot de passe *</label>
              <input type="password" className="border rounded px-2 py-1 w-full bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100" required value={form.password_confirm} onChange={e => setForm(f => ({ ...f, password_confirm: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Rôle *</label>
              <select className="border rounded px-2 py-1 w-full bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100" value={form.role} onChange={e => setForm(f => ({ ...f, role: e.target.value }))}>
              <option value="MEDECIN">Médecin</option>
              <option value="user_simple">Utilisateur simple</option>
            </select>
          </div>
            {/* Section Spécialiste - visible uniquement pour les médecins */}
            {form.role === 'MEDECIN' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Spécialiste</label>
                <select 
                  className="border rounded px-2 py-1 w-full bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100" 
                  value={form.specialite} 
                  onChange={e => setForm(f => ({ ...f, specialite: e.target.value }))}
                >
                  <option value="">Sélectionner une spécialité</option>
                  <option value="endocrinologue">Endocrinologue</option>
                  <option value="pneumologue">Pneumologue</option>
                  <option value="allergologue">Allergologue</option>
                  <option value="rhumatologue">Rhumatologue</option>
                  <option value="cardiologue">Cardiologue</option>
                  <option value="immunologue">Immunologue</option>
                  <option value="infectiologue">Infectiologue</option>
                  <option value="urologue">Urologue</option>
                  <option value="dermatologue">Dermatologue</option>
                  <option value="neurologue">Neurologue</option>
                  <option value="gastro_enterologue">Gastro-entérologue</option>
                  <option value="medecin_generaliste">Médecin généraliste</option>
                  <option value="orl">ORL</option>
                  <option value="autre">Autre spécialité</option>
                </select>
              </div>
            )}
            {/* Si user_simple, afficher le select médecin */}
            {form.role === 'user_simple' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Médecin référent *</label>
                <select
                  className="border rounded px-2 py-1 w-full bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
                  value={form.medecin || ''}
                  onChange={e => setForm(f => ({ ...f, medecin: e.target.value }))}
                  required
                >
                  <option value="">Sélectionner un médecin</option>
                  {medecins.map(m => (
                    <option key={m.id} value={m.id}>{m.first_name || ''} {m.last_name || ''} ({m.username})</option>
                  ))}
                </select>
              </div>
            )}
          </div>
          {formError && <div className="text-red-600 dark:text-red-400 mt-2 font-medium">{formError}</div>}
          <div className="mt-4 flex gap-2">
            <button type="submit" className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded font-medium">
              ➕ Créer l'utilisateur
            </button>
            <button type="button" className="bg-gray-400 hover:bg-gray-500 text-white px-4 py-2 rounded font-medium" onClick={() => { setShowAddForm(false); setForm(emptyForm); }}>
              ❌ Annuler
            </button>
          </div>
        </form>
      )}

      {/* Formulaire de modification - réservé à l'admin */}
      {showEditForm && !onlyForMedecinId && (
        <form className="bg-gray-100 dark:bg-gray-800 p-4 rounded mb-6" onSubmit={handleEditUser}>
          <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-100">Modifier l'utilisateur</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Nom d'utilisateur</label>
              <input type="text" className="border rounded px-2 py-1 w-full bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100" required value={form.username} onChange={e => setForm(f => ({ ...f, username: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Email</label>
              <input type="email" className="border rounded px-2 py-1 w-full bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100" required value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Prénom</label>
              <input type="text" className="border rounded px-2 py-1 w-full bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100" value={form.first_name} onChange={e => setForm(f => ({ ...f, first_name: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Nom</label>
              <input type="text" className="border rounded px-2 py-1 w-full bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100" value={form.last_name} onChange={e => setForm(f => ({ ...f, last_name: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Nouveau mot de passe (optionnel)</label>
              <input type="password" placeholder="Laisser vide pour ne pas changer" className="border rounded px-2 py-1 w-full bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100" value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Confirmer le mot de passe</label>
              <input type="password" className="border rounded px-2 py-1 w-full bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100" value={form.password_confirm} onChange={e => setForm(f => ({ ...f, password_confirm: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Rôle</label>
              <select className="border rounded px-2 py-1 w-full bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100" value={form.role} onChange={e => setForm(f => ({ ...f, role: e.target.value }))}>
              <option value="MEDECIN">Médecin</option>
              <option value="user_simple">Utilisateur simple</option>
            </select>
            </div>
            {/* Section Spécialiste - visible uniquement pour les médecins */}
            {form.role === 'MEDECIN' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Spécialiste</label>
                <select 
                  className="border rounded px-2 py-1 w-full bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100" 
                  value={form.specialite || ''} 
                  onChange={e => setForm(f => ({ ...f, specialite: e.target.value }))}
                >
                  <option value="">Sélectionner une spécialité</option>
                  <option value="endocrinologue">Endocrinologue</option>
                  <option value="pneumologue">Pneumologue</option>
                  <option value="allergologue">Allergologue</option>
                  <option value="rhumatologue">Rhumatologue</option>
                  <option value="cardiologue">Cardiologue</option>
                  <option value="immunologue">Immunologue</option>
                  <option value="infectiologue">Infectiologue</option>
                  <option value="urologue">Urologue</option>
                  <option value="dermatologue">Dermatologue</option>
                  <option value="neurologue">Neurologue</option>
                  <option value="gastro_enterologue">Gastro-entérologue</option>
                  <option value="medecin_generaliste">Médecin généraliste</option>
                  <option value="orl">ORL</option>
                  <option value="autre">Autre spécialité</option>
                </select>
              </div>
            )}
            {/* Si user_simple, afficher le select médecin */}
            {form.role === 'user_simple' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Médecin référent *</label>
                <select
                  className="border rounded px-2 py-1 w-full bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
                  value={form.medecin || ''}
                  onChange={e => setForm(f => ({ ...f, medecin: e.target.value }))}
                  required
                >
                  <option value="">Sélectionner un médecin</option>
                  {medecins.map(m => (
                    <option key={m.id} value={m.id}>{m.first_name || ''} {m.last_name || ''} ({m.username})</option>
                  ))}
                </select>
              </div>
            )}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Statut</label>
              <select className="border rounded px-2 py-1 w-full bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100" value={form.is_active} onChange={e => setForm(f => ({ ...f, is_active: e.target.value === 'true' }))}>
                <option value="true">🟢 Actif</option>
                <option value="false">🔴 Inactif</option>
            </select>
            </div>
          </div>
          {formError && <div className="text-red-600 dark:text-red-400 mt-2 font-medium">{formError}</div>}
          <div className="mt-4 flex gap-2">
            <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-medium">
               Enregistrer les modifications
            </button>
            <button type="button" className="bg-gray-400 hover:bg-gray-500 text-white px-4 py-2 rounded font-medium" onClick={() => { setShowEditForm(false); setEditUserId(null); setForm(emptyForm); }}>
              ❌ Annuler
            </button>
          </div>
        </form>
      )}

      {loading ? (
        <div className="text-gray-900 dark:text-gray-100">Chargement...</div>
      ) : error ? (
        <div className="text-red-600 dark:text-red-400">{error}</div>
      ) : (
        <table className="min-w-full bg-white dark:bg-gray-800 border rounded-lg shadow">
          <thead>
            <tr>
              <th className="py-2 px-4 border-b text-gray-900 dark:text-gray-100">Nom d'utilisateur</th>
              <th className="py-2 px-4 border-b text-gray-900 dark:text-gray-100">Email</th>
              <th className="py-2 px-4 border-b text-gray-900 dark:text-gray-100">Rôle</th>
              <th className="py-2 px-4 border-b text-gray-900 dark:text-gray-100">Spécialiste</th>
              <th className="py-2 px-4 border-b text-gray-900 dark:text-gray-100">Statut</th>
              <th className="py-2 px-4 border-b text-gray-900 dark:text-gray-100">Actions</th>
            </tr>
          </thead>
          <tbody>
            {Array.isArray(filteredUsers) && filteredUsers.map(u => (
              <tr key={u.id} className={`text-center ${u.id === user.id ? 'bg-blue-50 dark:bg-blue-900' : 'bg-white dark:bg-gray-800'}`}>
                <td className="py-2 px-4 border-b text-gray-900 dark:text-gray-100">
                  {u.username} {u.id === user.id && <span className="text-blue-600 dark:text-blue-300 text-xs">(Vous)</span>}
                </td>
                <td className="py-2 px-4 border-b text-gray-900 dark:text-gray-100">{u.email}</td>
                <td className="py-2 px-4 border-b">
                  <span className={`px-2 py-1 rounded text-sm font-medium ${
                    u.role === 'MEDECIN'
                      ? 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
                  }`}>
                    {u.role === 'MEDECIN' ? ' Médecin' : 'Utilisateur simple'}
                  </span>
                </td>
                <td className="py-2 px-4 border-b text-gray-900 dark:text-gray-100">
                  {u.role === 'MEDECIN' ? (
                    u.specialite ? (
                      <span className="px-2 py-1 rounded text-sm font-medium bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200">
                        {u.specialite}
                      </span>
                    ) : (
                      <span className="text-gray-500 dark:text-gray-400 text-sm">Non spécifiée</span>
                    )
                  ) : (
                    <span className="text-gray-400 dark:text-gray-500 text-sm">-</span>
                  )}
                </td>
                <td className="py-2 px-4 border-b">
                  <span className={`px-2 py-1 rounded text-sm font-medium ${
                    u.is_active
                      ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                      : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                  }`}>
                    {u.is_active ? '🟢 Actif' : '🔴 Inactif'}
                  </span>
                </td>
                <td className="py-2 px-4 border-b flex flex-col md:flex-row gap-2 items-center justify-center">
                  <button
                    onClick={() => openEditForm(u)}
                    className="bg-yellow-500 dark:bg-yellow-600 hover:bg-yellow-600 dark:hover:bg-yellow-700 text-white px-3 py-1 rounded"
                  >
                    Modifier
                  </button>
                  <button
                    onClick={() => handleDelete(u.id)}
                    disabled={updatingId === u.id || u.id === user.id}
                    className="bg-red-500 dark:bg-red-700 hover:bg-red-700 dark:hover:bg-red-800 text-white px-3 py-1 rounded disabled:opacity-50"
                  >
                    Supprimer
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <ConfirmModal
        open={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        onConfirm={confirmDelete}
        message="Voulez-vous vraiment supprimer cet utilisateur ? Cette action est irréversible."
      />
    </div>
  );
};

export default AdminUserManagement; 
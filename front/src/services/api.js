import axios from 'axios';

// Configuration de base pour axios
const API_BASE_URL = 'http://localhost:8000/api';

// Créer une instance axios avec la configuration de base
const api = axios.create({
  baseURL: API_BASE_URL,
});

// Intercepteur pour ajouter le token d'authentification aux requêtes
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Ajouter le Content-Type approprié si pas déjà défini
    if (!config.headers['Content-Type']) {
      if (config.data instanceof FormData) {
        // Pour FormData, ne pas définir Content-Type (axios le fera automatiquement)
        delete config.headers['Content-Type'];
      } else {
        config.headers['Content-Type'] = 'application/json';
      }
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les erreurs de réponse
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expiré ou invalide
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('role');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Service d'authentification
export const authService = {
  // Test de connexion
  testConnection: () => api.get('/test-connexion/'),
  
  // Connexion utilisateur
  login: (credentials) => api.post('/auth/login/', credentials),
  
  // Déconnexion utilisateur
  logout: (refreshToken) => api.post('/auth/logout/', { refresh_token: refreshToken }),
  
  // Obtenir les détails de l'utilisateur connecté
  getUserDetails: () => api.get('/auth/user/'),
  
  // Changer le mot de passe
  changePassword: (passwords) => api.post('/auth/change-password/', passwords),
  
  // Réinitialisation simple de mot de passe (ancienne méthode, à garder pour compatibilité)
  simplePasswordReset: (data) => api.post('/auth/admin-reset-password/', data),

  // Nouvelle méthode : étape 1 - vérification username + email
  verifyUsername: (data) => api.post('/auth/verify-username/', data).then(res => res.data),
  // Nouvelle méthode : étape 2 - reset avec token
  simplePasswordResetWithToken: (data) => api.post('/auth/reset-password-token/', data).then(res => res.data),
};

// Service pour les utilisateurs (admin seulement)
export const userService = {
  // Liste des utilisateurs (admin)
  getUsers: () => api.get('/admin/users/'),
  
  // Détails d'un utilisateur (admin)
  getUser: (id) => api.get(`/admin/users/${id}/`),
  
  // Créer un utilisateur (admin)
  createUser: (userData) => api.post('/admin/users/', userData),
  
  // Mettre à jour un utilisateur (admin)
  updateUser: (id, userData) => api.put(`/admin/users/${id}/`, userData),
  
  // Supprimer un utilisateur (admin)
  deleteUser: (id) => api.delete(`/admin/users/${id}/`),
};

// Service pour les patients
export const patientService = {
  getPatients: () => api.get('/patients/'),
  getPatient: (id) => api.get(`/patients/${id}/`),
  createPatient: (patientData) => api.post('/patients/', patientData),
  updatePatient: (id, patientData) => api.put(`/patients/${id}/`, patientData),
  deletePatient: (id) => api.delete(`/patients/${id}/`),
  // Statistiques spécifiques au médecin
  getMesPatients: () => api.get('/mes-patients/'),
};

// Service pour les dossiers médicaux
export const dossierMedicalService = {
  getDossiers: () => api.get('/dossiers-medicaux/'),
  getDossier: (id) => api.get(`/dossiers-medicaux/${id}/`),
  createDossier: (dossierData) => api.post('/dossiers-medicaux/', dossierData),
  updateDossier: (id, dossierData) => api.put(`/dossiers-medicaux/${id}/`, dossierData),
  deleteDossier: (id) => api.delete(`/dossiers-medicaux/${id}/`),
  // Statistiques spécifiques au médecin
  getMesDossiers: () => api.get('/mes-dossiers-medicaux/'),
};

// Service pour les rapports
export const rapportService = {
  getRapports: () => api.get('/rapports/'),
  getRapport: (id) => api.get(`/rapports/${id}/`),
  createRapport: (rapportData) => api.post('/rapports/', rapportData),
  updateRapport: (id, rapportData) => api.put(`/rapports/${id}/`, rapportData),
  deleteRapport: (id) => api.delete(`/rapports/${id}/`),
  // Statistiques spécifiques au médecin
  getMesRapports: () => api.get('/mes-rapports/'),
};

// Service pour les alertes
export const alerteService = {
  getAlertes: () => api.get('/alertes/'),
  getAlerte: (id) => api.get(`/alertes/${id}/`),
  createAlerte: (alerteData) => api.post('/alertes/', alerteData),
  updateAlerte: (id, alerteData) => api.put(`/alertes/${id}/`, alerteData),
  deleteAlerte: (id) => api.delete(`/alertes/${id}/`),
};

// Service pour l'importation CSV
export const importCSV = (formData) => {
  return api.post('/import-csv/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }).then(response => response.data);
};

// === DEMANDES D'EXPORTATION ===

export const exportationService = {
  // User simple : créer une demande
  creerDemande: (data, token) =>
    api.post('/demandes-exportation/', data, {
      headers: { Authorization: `Bearer ${token}` },
    }),

  // User simple : lister ses demandes
  mesDemandes: (token) =>
    api.get('/mes-demandes-exportation/', {
      headers: { Authorization: `Bearer ${token}` },
    }),

  // Médecin : lister les demandes à traiter
  demandesATraiter: (token) =>
    api.get('/demandes-a-traiter/', {
      headers: { Authorization: `Bearer ${token}` },
    }),

  // Médecin : traiter une demande (approuver/refuser)
  traiterDemande: (demandeId, data, token) =>
    api.put(`/traiter-demande-exportation/${demandeId}/`, data, {
      headers: { Authorization: `Bearer ${token}` },
    }),
};

// Statistiques des patients par maladie
export const getPatientsParMaladie = async () => {
  try {
    const response = await api.get('/stats/patients-par-maladie/');
    return response.data;
  } catch (error) {
    console.error('Erreur lors de la récupération des statistiques par maladie:', error);
    throw error;
  }
};

// Récupérer les alertes critiques
export const getAlertesCritiques = async () => {
  try {
    const response = await api.get('/alertes-critiques/');
    return response.data;
  } catch (error) {
    console.error('Erreur lors de la récupération des alertes critiques:', error);
    throw error;
  }
};

// Service pour les règles de conformité
export const regleConformiteService = {
  getRegles: () => api.get('/regles-conformite/'),
  getRegle: (id) => api.get(`/regles-conformite/${id}/`),
  createRegle: (data) => api.post('/regles-conformite/', data),
  updateRegle: (id, data) => api.put(`/regles-conformite/${id}/`, data),
  deleteRegle: (id) => api.delete(`/regles-conformite/${id}/`),
};

// Service pour les paramètres/seuils de conformité
export const parametreConformiteService = {
  getParametres: () => api.get('/parametres-conformite/'),
  getParametre: (id) => api.get(`/parametres-conformite/${id}/`),
  createParametre: (data) => api.post('/parametres-conformite/', data),
  updateParametre: (id, data) => api.put(`/parametres-conformite/${id}/`, data),
  deleteParametre: (id) => api.delete(`/parametres-conformite/${id}/`),
};

// === NOUVEAU SYSTÈME D'ALERTES DE CONFORMITÉ ===

// Service pour les types d'alertes de conformité
export const typeAlerteConformiteService = {
  getTypes: () => api.get('/types-alertes-conformite/'),
  getType: (id) => api.get(`/types-alertes-conformite/${id}/`),
  createType: (data) => api.post('/types-alertes-conformite/', data),
  updateType: (id, data) => api.put(`/types-alertes-conformite/${id}/`, data),
  deleteType: (id) => api.delete(`/types-alertes-conformite/${id}/`),
};

// Service pour les alertes de conformité
export const alerteConformiteService = {
  getAlertes: () => api.get('/alertes-conformite/'),
  getAlerte: (id) => api.get(`/alertes-conformite/${id}/`),
  createAlerte: (data) => api.post('/alertes-conformite/', data),
  updateAlerte: (id, data) => api.put(`/alertes-conformite/${id}/`, data),
  deleteAlerte: (id) => api.delete(`/alertes-conformite/${id}/`),
  getAlertesCritiques: () => api.get('/conformite/alertes-critiques/'),
  executerSurveillance: () => api.post('/conformite/surveillance/'),
};

// Service pour les règles d'alertes de conformité
export const regleAlerteConformiteService = {
  getRegles: () => api.get('/regles-alertes-conformite/'),
  getRegle: (id) => api.get(`/regles-alertes-conformite/${id}/`),
  createRegle: (data) => api.post('/regles-alertes-conformite/', data),
  updateRegle: (id, data) => api.put(`/regles-alertes-conformite/${id}/`, data),
  deleteRegle: (id) => api.delete(`/regles-alertes-conformite/${id}/`),
};

// Service pour les notifications de conformité
export const notificationConformiteService = {
  getNotifications: () => api.get('/notifications-conformite/'),
  getNotification: (id) => api.get(`/notifications-conformite/${id}/`),
  createNotification: (data) => api.post('/notifications-conformite/', data),
  updateNotification: (id, data) => api.put(`/notifications-conformite/${id}/`, data),
  deleteNotification: (id) => api.delete(`/notifications-conformite/${id}/`),
};

// Service pour l'audit de conformité
export const auditConformiteService = {
  getAudits: () => api.get('/audit-conformite/'),
  getAudit: (id) => api.get(`/audit-conformite/${id}/`),
  createAudit: (data) => api.post('/audit-conformite/', data),
  updateAudit: (id, data) => api.put(`/audit-conformite/${id}/`, data),
  deleteAudit: (id) => api.delete(`/audit-conformite/${id}/`),
};

// Service pour les statistiques et configuration de conformité
export const conformiteService = {
  getStatistiques: () => api.get('/conformite/statistiques-detaillees/'),
  getConfiguration: () => api.get('/conformite/configuration/'),
  configurerAlertes: (data) => api.post('/conformite/configurer/', data),
  genererRapport: () => api.get('/conformite/rapport/'),
  initialiserTypes: () => api.post('/conformite/initialiser-types-alertes/'),
};

// Service pour l'audit des accès
export const accesService = {
  getAcces: async () => {
    const response = await api.get('/acces/');
    // Django REST Framework renvoie souvent les données dans response.data.results
    // ou directement dans response.data selon la configuration
    return {
      data: Array.isArray(response.data) ? response.data : (response.data.results || response.data || [])
    };
  },
  getAccesById: (id) => api.get(`/acces/${id}/`),
  // Ajoute d'autres méthodes si besoin (filtrage, suppression, etc.)
};

export const resultatAnalyseService = {
  getResultats: () => api.get('/resultats-analyse/'),
  getResultat: (id) => api.get(`/resultats-analyse/${id}/`)
};

export default api; 
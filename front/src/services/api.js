import axios from 'axios';

// Configuration de base pour axios
const API_BASE_URL = 'http://localhost:8000/api';

// Créer une instance axios avec la configuration de base
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token d'authentification aux requêtes
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
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
  
  // Déconnexion
  logout: (refreshToken) => api.post('/auth/logout/', { refresh_token: refreshToken }),
  
  // Récupérer les détails de l'utilisateur connecté
  getUserDetails: () => api.get('/auth/user/'),
  
  // Changer le mot de passe
  changePassword: (passwords) => api.post('/auth/change-password/', passwords),
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
};

// Service pour les dossiers médicaux
export const dossierMedicalService = {
  getDossiers: () => api.get('/dossiers-medicaux/'),
  getDossier: (id) => api.get(`/dossiers-medicaux/${id}/`),
  createDossier: (dossierData) => api.post('/dossiers-medicaux/', dossierData),
  updateDossier: (id, dossierData) => api.put(`/dossiers-medicaux/${id}/`, dossierData),
  deleteDossier: (id) => api.delete(`/dossiers-medicaux/${id}/`),
};

// Service pour les rapports
export const rapportService = {
  getRapports: () => api.get('/rapports/'),
  getRapport: (id) => api.get(`/rapports/${id}/`),
  createRapport: (rapportData) => api.post('/rapports/', rapportData),
  updateRapport: (id, rapportData) => api.put(`/rapports/${id}/`, rapportData),
  deleteRapport: (id) => api.delete(`/rapports/${id}/`),
};

// Service pour les alertes
export const alerteService = {
  getAlertes: () => api.get('/alertes/'),
  getAlerte: (id) => api.get(`/alertes/${id}/`),
  createAlerte: (alerteData) => api.post('/alertes/', alerteData),
  updateAlerte: (id, alerteData) => api.put(`/alertes/${id}/`, alerteData),
  deleteAlerte: (id) => api.delete(`/alertes/${id}/`),
};

export default api; 
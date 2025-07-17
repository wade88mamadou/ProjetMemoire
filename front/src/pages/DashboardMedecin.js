import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { patientService, dossierMedicalService, rapportService, exportationService, getPatientsParMaladie } from '../services/api';
import useDarkMode from '../hooks/useDarkMode';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Plot from 'react-plotly.js';
import { resultatAnalyseService } from '../services/api';
import GroupStatsCharts from '../components/GroupStatsCharts';
import DemandesExportationMedecin from './DemandesExportationMedecin';
import AdminUserManagement from './AdminUserManagement';
import StatCard from '../components/StatCard';
import LogoHeader from '../components/LogoHeader';

function UsersSimplesMedecin() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true);
      const token = localStorage.getItem('token');
      const res = await fetch('http://localhost:8000/api/mes-users-simples/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      setUsers(data);
      setLoading(false);
    };
    fetchUsers();
  }, []);

  if (loading) return (
    <div className="flex justify-center items-center h-40">
      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
      <span className="ml-4 text-gray-600">Chargement...</span>
    </div>
  );

  if (!users.length) return (
    <div className="flex flex-col items-center justify-center h-40">
      <span className="text-gray-500 text-lg">Aucun utilisateur simple rattaché à vous.</span>
    </div>
  );

  return (
    <div className="max-w-3xl mx-auto mt-8 p-6 bg-white dark:bg-gray-800 rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-6 text-blue-700 dark:text-blue-200 text-center">
        Mes utilisateurs simples rattachés
      </h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700 rounded-lg overflow-hidden shadow">
          <thead className="bg-blue-100 dark:bg-blue-900">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-semibold text-blue-700 dark:text-blue-200 uppercase tracking-wider">
                Nom d'utilisateur
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-blue-700 dark:text-blue-200 uppercase tracking-wider">
                Email
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {users.map((u, idx) => (
              <tr key={u.id} className={idx % 2 === 0 ? "bg-gray-50 dark:bg-gray-900" : ""}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">{u.username}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">{u.email}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function PatientsCard() {
  const [nbPatients, setNbPatients] = useState(0);
  useEffect(() => {
    const token = localStorage.getItem('token');
    fetch('http://localhost:8000/api/mes-patients/', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setNbPatients(data.length));
  }, []);
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 text-center mb-6">
      <div className="text-lg font-bold text-gray-700 dark:text-gray-200">Nombre de patients</div>
      <div className="text-3xl text-blue-600 dark:text-blue-400 font-extrabold">{nbPatients}</div>
    </div>
  );
}

function ExportPatientsMedecin() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dossiers, setDossiers] = useState({}); // { patientId: dossier }

  useEffect(() => {
    const fetchPatients = async () => {
      setLoading(true);
      const token = localStorage.getItem('token');
      const res = await fetch('http://localhost:8000/api/mes-patients/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      setPatients(data);
      setLoading(false);
    };
    fetchPatients();
  }, []);

  useEffect(() => {
    // Pour chaque patient, on charge le dossier principal
    const fetchDossiers = async () => {
      const token = localStorage.getItem('token');
      const res = await fetch('http://localhost:8000/api/mes-dossiers-medicaux/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      const dossiersByPatient = {};
      for (const patient of patients) {
        const pid = patient.idPatient || patient.id;
        const dossiersPatient = (data.dossiers || []).filter(d => d.patient === pid);
        const dossier = dossiersPatient.sort((a, b) => new Date(b.dateCreation) - new Date(a.dateCreation))[0];
        if (dossier) {
          dossiersByPatient[pid] = dossier;
        }
      }
      setDossiers(dossiersByPatient);
    };
    if (patients.length > 0) {
      fetchDossiers();
    }
  }, [patients]);

  const handleExportPatient = (patient, type) => {
    const pid = patient.idPatient || patient.id;
    const url = type === 'pdf'
      ? `http://localhost:8000/api/export-patient-pdf/${pid}/`
      : `http://localhost:8000/api/export-patient-csv/${pid}/`;
    const token = localStorage.getItem('token');
    
    // Debug: afficher le token pour vérification
    console.log('Token:', token ? token.substring(0, 20) + '...' : 'Aucun token');
    
    fetch(url, { 
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      } 
    })
      .then(res => {
        console.log('Response status:', res.status);
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.blob();
      })
      .then(blob => {
        const fileType = type === 'pdf' ? 'pdf' : 'csv';
        const fileName = `patient_${pid}.${fileType}`;
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        a.click();
        window.URL.revokeObjectURL(url);
      })
      .catch(error => {
        console.error('Erreur lors de l\'export:', error);
        alert(`Erreur lors de l'export: ${error.message}`);
      });
  };

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Exporter les données de mes patients</h2>
      <div className="mt-8">
        <h3 className="text-lg font-semibold mb-2">Dossiers médicaux</h3>
        {loading ? (
          <div className="flex justify-center items-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-4 text-gray-600">Chargement...</span>
          </div>
        ) : patients.length === 0 ? (
          <div className="text-gray-500">Aucun patient trouvé.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700 rounded-lg overflow-hidden shadow">
              <thead className="bg-blue-100 dark:bg-blue-900">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-blue-700 dark:text-blue-200 uppercase tracking-wider">ID</th>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-blue-700 dark:text-blue-200 uppercase tracking-wider">Patient</th>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-blue-700 dark:text-blue-200 uppercase tracking-wider">Date création</th>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-blue-700 dark:text-blue-200 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {patients.map((p, idx) => {
                  const pid = p.idPatient || p.id;
                  const dossier = dossiers[pid];
                  return (
                    <tr key={pid} className={idx % 2 === 0 ? "bg-gray-50 dark:bg-gray-900" : ""}>
                      <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900 dark:text-white">{dossier ? dossier.id : ''}</td>
                      <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900 dark:text-white">{pid}</td>
                      <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900 dark:text-white">{dossier ? dossier.dateCreation : ''}</td>
                      <td className="px-4 py-2 whitespace-nowrap text-sm flex gap-2">
                        <button
                          className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-xs"
                          onClick={() => handleExportPatient(p, 'pdf')}
                        >
                          Exporter PDF
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function ModifierPatientsMedecin() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [editingPatient, setEditingPatient] = useState(null);

  useEffect(() => {
    const fetchPatients = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('token');
        const response = await fetch('http://localhost:8000/api/mes-patients/', {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await response.json();
        setPatients(data);
      } catch (error) {
        console.error('Erreur lors du chargement des patients:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchPatients();
  }, []);

  const handleEditPatient = (patient) => {
    setSelectedPatient(patient);
    setEditingPatient({ ...patient });
  };

  const handleSavePatient = async () => {
    if (!editingPatient) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/patients/${editingPatient.id}/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(editingPatient)
      });
      
      if (response.ok) {
        // Mettre à jour la liste des patients
        setPatients(patients.map(p => p.id === editingPatient.id ? editingPatient : p));
        setSelectedPatient(null);
        setEditingPatient(null);
        alert('Patient modifié avec succès !');
      } else {
        alert('Erreur lors de la modification du patient');
      }
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error);
      alert('Erreur lors de la sauvegarde');
    }
  };

  const handleCancelEdit = () => {
    setSelectedPatient(null);
    setEditingPatient(null);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-4 text-gray-600">Chargement...</span>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Modifier les données des patients</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700 rounded-lg overflow-hidden shadow">
          <thead className="bg-blue-100 dark:bg-blue-900">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-semibold text-blue-700 dark:text-blue-200 uppercase tracking-wider">ID</th>
              <th className="px-4 py-2 text-left text-xs font-semibold text-blue-700 dark:text-blue-200 uppercase tracking-wider">Nom</th>
              <th className="px-4 py-2 text-left text-xs font-semibold text-blue-700 dark:text-blue-200 uppercase tracking-wider">Prénom</th>
              <th className="px-4 py-2 text-left text-xs font-semibold text-blue-700 dark:text-blue-200 uppercase tracking-wider">Date de naissance</th>
              <th className="px-4 py-2 text-left text-xs font-semibold text-blue-700 dark:text-blue-200 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {patients.map((patient, idx) => (
              <tr key={patient.id} className={idx % 2 === 0 ? "bg-gray-50 dark:bg-gray-900" : ""}>
                <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900 dark:text-white">{patient.idPatient || patient.id}</td>
                <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {selectedPatient?.id === patient.id ? (
                    <input
                      type="text"
                      value={editingPatient?.nom || ''}
                      onChange={(e) => setEditingPatient({...editingPatient, nom: e.target.value})}
                      className="border rounded px-2 py-1 text-sm w-full"
                    />
                  ) : (
                    patient.nom || 'N/A'
                  )}
                </td>
                <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {selectedPatient?.id === patient.id ? (
                    <input
                      type="text"
                      value={editingPatient?.prenom || ''}
                      onChange={(e) => setEditingPatient({...editingPatient, prenom: e.target.value})}
                      className="border rounded px-2 py-1 text-sm w-full"
                    />
                  ) : (
                    patient.prenom || 'N/A'
                  )}
                </td>
                <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {selectedPatient?.id === patient.id ? (
                    <input
                      type="date"
                      value={editingPatient?.dateNaissance || ''}
                      onChange={(e) => setEditingPatient({...editingPatient, dateNaissance: e.target.value})}
                      className="border rounded px-2 py-1 text-sm w-full"
                    />
                  ) : (
                    patient.dateNaissance || 'N/A'
                  )}
                </td>
                <td className="px-4 py-2 whitespace-nowrap text-sm flex gap-2">
                  {selectedPatient?.id === patient.id ? (
                    <>
                      <button
                        className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-xs"
                        onClick={handleSavePatient}
                      >
                        Sauvegarder
                      </button>
                      <button
                        className="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-xs"
                        onClick={handleCancelEdit}
                      >
                        Annuler
                      </button>
                    </>
                  ) : (
                    <button
                      className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-xs"
                      onClick={() => handleEditPatient(patient)}
                    >
                      Modifier
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function DashboardCards() {
  const [patients, setPatients] = useState([]);
  const [usersSimples, setUsersSimples] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    // Patients du médecin
    fetch('http://localhost:8000/api/mes-patients/', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        setPatients(data);
        setLoading(false);
      });
    // Users simples du médecin
    fetch('http://localhost:8000/api/mes-users-simples/', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setUsersSimples(data));
  }, []);

  // Card 1 : Nombre de patients
  const nbPatients = patients.length;

  // Card 2 : Nombre de décès users_simple (supposons champ 'etat' ou 'deces')
  const nbDeces = usersSimples.filter(u => u.etat === 'décédé' || u.deces === true).length;

  // Card 3 : Nombre de dossiers médicaux (supposons chaque patient a un champ 'dossier_medical' ou sinon = nbPatients)
  const nbDossiers = patients.filter(p => p.dossier_medical !== undefined && p.dossier_medical !== null).length || nbPatients;

  if (loading) return <div>Chargement...</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
      <StatCard title="Nombre de patients" value={nbPatients} color="border-blue-600" />
      <StatCard title="Décès (users simples)" value={nbDeces} color="border-red-600" />
      <StatCard title="Dossiers médicaux" value={nbDossiers} color="border-green-600" />
    </div>
  );
}

const API_BASE_URL = "http://localhost:8000";

const DashboardMedecin = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [darkMode, setDarkMode] = useDarkMode();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState({
    totalPatients: 0,
    totalDossiers: 0,
    totalRapports: 0
  });
  const [maladieStats, setMaladieStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const userMenuRef = useRef(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [usersSimples, setUsersSimples] = useState([]);
  const [pendingExports, setPendingExports] = useState(0);

  // State pour la liste des résultats d'analyse
  const [resultats, setResultats] = useState([]);
  const [loadingResultats, setLoadingResultats] = useState(true);

  // Ajoute ce state pour le sélecteur de statistiques par groupe
  const [selectedChart, setSelectedChart] = useState('effectif');

  // Ajoute ces hooks en haut du composant DashboardMedecin (après les autres useState)
  const [dossiers, setDossiers] = useState([]);
  const [loadingExport, setLoadingExport] = useState(true);

  // Charger les dossiers médicaux
  useEffect(() => {
    const fetchDossiers = async () => {
      setLoadingExport(true);
      try {
        const res = await dossierMedicalService.getMesDossiers();
        setDossiers(res.data.dossiers || res.data || []);
      } catch (e) {
        setDossiers([]);
      } finally {
        setLoadingExport(false);
      }
    };
    fetchDossiers();
  }, []);

  // Charger les résultats d'analyse
  useEffect(() => {
    const fetchResultats = async () => {
      setLoadingResultats(true);
      try {
        const res = await resultatAnalyseService.getResultats();
        setResultats(res.data.results || res.data || []);
      } catch (e) {
        setResultats([]);
      } finally {
        setLoadingResultats(false);
      }
    };
    fetchResultats();
  }, []);

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

  // Fonction pour charger les statistiques par maladie
  const loadMaladieStats = async () => {
    try {
      console.log('Chargement des statistiques par maladie (médecin)...');
      const response = await getPatientsParMaladie();
      console.log('Réponse API maladies (médecin):', response);
      setMaladieStats(response.data);
      console.log('Statistiques maladies mises à jour (médecin):', response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des statistiques par maladie (médecin):', error);
    }
  };

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [patientsRes, dossiersRes, rapportsRes] = await Promise.all([
          patientService.getMesPatients(),
          dossierMedicalService.getMesDossiers(),
          rapportService.getMesRapports()
        ]);
        setStats({
          totalPatients: patientsRes.data.total_patients || 0,
          totalDossiers: dossiersRes.data.total_dossiers || 0,
          totalRapports: rapportsRes.data.total_rapports || 0
        });
      } catch (error) {
        console.error('Erreur lors du chargement des statistiques:', error);
        // En cas d'erreur, on met des valeurs par défaut
        setStats({
          totalPatients: 0,
          totalDossiers: 0,
          totalRapports: 0
        });
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
    loadMaladieStats();
  }, []);

  // Charger le nombre de demandes d'exportation en attente
  useEffect(() => {
    const fetchPendingExports = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await exportationService.demandesATraiter(token);
        setPendingExports(res.data ? res.data.length : (res.length || 0));
      } catch (e) {
        setPendingExports(0);
      }
    };
    fetchPendingExports();
  }, []);

  // Fetch users_simple rattachés à ce médecin
  useEffect(() => {
    if (activeTab === 'users_simples') {
      const fetchUsersSimples = async () => {
        try {
          const token = localStorage.getItem('token');
          const res = await axios.get('http://localhost:8000/api/mes-users-simples/', {
            headers: { Authorization: `Bearer ${token}` }
          });
          setUsersSimples(res.data);
        } catch (err) {
          setUsersSimples([]);
        }
      };
      fetchUsersSimples();
    }
  }, [activeTab]);

  // Effect pour charger les résultats d'analyse
  useEffect(() => {
    const fetchResultats = async () => {
      setLoadingResultats(true);
      try {
        const res = await resultatAnalyseService.getResultats();
        setResultats(res.data.results || res.data || []);
      } catch (e) {
        setResultats([]);
      } finally {
        setLoadingResultats(false);
      }
    };
    fetchResultats();
  }, []);

  const handleLogout = () => {
    logout();
  };

  // Fonction utilitaire pour télécharger un fichier avec gestion d'erreur
  const downloadFile = async (url, filename) => {
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer ' + localStorage.getItem('token')
        }
      });
      const contentType = response.headers.get('content-type');
      if (!response.ok || (contentType && contentType.includes('application/json'))) {
        let errorMsg = 'Erreur lors du téléchargement';
        try {
          const errorData = await response.json();
          errorMsg = errorData.error || errorData.detail || errorMsg;
        } catch {}
        alert(errorMsg);
        return;
      }
      const blob = await response.blob();
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(link.href);
    } catch (err) {
      alert('Erreur réseau ou serveur lors du téléchargement');
    }
  };

  // Remplacer les fonctions d'export par des appels à downloadFile
  const downloadDossierCSV = (dossierId) => downloadFile(`${API_BASE_URL}/api/export/dossier-medical/${dossierId}/`, `dossier_${dossierId}.csv`);
  const downloadDossierPDF = (dossierId) => downloadFile(`${API_BASE_URL}/api/export/dossier-medical-pdf/${dossierId}/`, `dossier_${dossierId}.pdf`);
  const downloadAnalyseCSV = (analyseId) => downloadFile(`${API_BASE_URL}/api/export/resultats-analyse/${analyseId}/`, `resultats_analyse_${analyseId}.csv`);
  const downloadAnalysePDF = (analyseId) => downloadFile(`${API_BASE_URL}/api/export/resultats-analyse-pdf/${analyseId}/`, `resultats_analyse_${analyseId}.pdf`);

  // Sidebar menu items pour le médecin
  const sidebarItems = [
    {
      id: 'dashboard',
      label: 'Tableau de bord',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      )
    },
    {
      id: 'export',
      label: 'Exporter les données',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      )
    },
    {
      id: 'modifier_patients',
      label: 'Modifier données patient',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
      )
    },
    {
      id: 'users_simples',
      label: 'Mes utilisateurs',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      )
    },
    {
      id: 'repondre-demandes',
      label: "Répondre demandes d'exportation",
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V4a2 2 0 10-4 0v1.341C7.67 7.165 6 9.388 6 12v2.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
      )
    }
  ];

  // Render content based on active tab
  const renderContent = () => {
    if (activeTab === 'export') {
      return <ExportPatientsMedecin />;
    }
    if (activeTab === 'modifier_patients') {
      return <ModifierPatientsMedecin />;
    }
    if (activeTab === 'users_simples') {
      return <UsersSimplesMedecin />;
    }
    if (activeTab === 'repondre-demandes') {
      return <DemandesExportationMedecin />;
    }
    // Bloc statistiques par groupe et graphiques : UNIQUEMENT pour le dashboard
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
      chartLayout = { title: chartTitle, xaxis: { title: 'Groupe' }, yaxis: { title: 'Effectif' }, height: 400 };
    } else if (selectedChart === 'sexratio') {
      chartData = [{ x: groupes, y: sexRatios, type: 'bar', marker: { color: '#059669' } }];
      chartTitle = 'Sex ratio (H/F) par groupe';
      chartLayout = { title: chartTitle, xaxis: { title: 'Groupe' }, yaxis: { title: 'Sex ratio (H/F)' }, height: 400 };
    } else {
      chartData = [{ x: groupes, y: agesMoyens, type: 'bar', marker: { color: '#f59e42' } }];
      chartTitle = 'Âge moyen par groupe';
      chartLayout = { title: chartTitle, xaxis: { title: 'Groupe' }, yaxis: { title: 'Âge moyen' }, height: 400 };
    }
    // --- FIN bloc statistiques par maladie ---
        return (
          <div className="space-y-6">
        <DashboardCards />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Tableau de bord</h2>
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
        {/* Sélecteur de statistiques par groupe */}
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

            {/* Tableau détaillé des infections */}
        {/* {maladieStats && maladieStats.infections && maladieStats.infections.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md">
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Détail par Type d'Infection</h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead className="bg-gray-50 dark:bg-gray-700">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          Type d'Infection
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          Nombre de Patients
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          Pourcentage
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                      {maladieStats.infections.map((infection, index) => {
                        const percentage = ((infection.nombre_patients / maladieStats.total_patients) * 100).toFixed(1);
                        return (
                          <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                              {infection.maladie}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                              {infection.nombre_patients}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                              {percentage}%
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
        )} */}
          </div>
        );
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
                <LogoHeader role="Médecin" />
              )}
              <button
                className="md:hidden text-gray-500 dark:text-gray-300 focus:outline-none"
                onClick={() => setSidebarOpen(!sidebarOpen)}
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              </button>
            </div>
            {/* Menu */}
            <nav className="flex-1 px-2 py-4 space-y-2">
              {sidebarItems.map(item => (
                <button
                  key={item.id}
                  className={`flex items-center w-full px-3 py-2 rounded-lg transition-colors duration-200 focus:outline-none text-left font-medium text-gray-700 dark:text-gray-200 hover:bg-blue-100 dark:hover:bg-blue-900 ${activeTab === item.id ? 'bg-blue-100 dark:bg-blue-900 font-bold' : ''}`}
                  onClick={() => {
                    if (item.id === 'import') {
                      navigate('/import-data');
                    } else {
                      setActiveTab(item.id);
                    }
                  }}
                >
                  <span className="mr-3">{item.icon}</span>
                  {sidebarOpen && item.label}
                </button>
              ))}
              {/* Lien conditionnel pour demandes d'exportation */}
              {pendingExports > 0 && (
                <button
                  onClick={() => navigate('/medecin/demandes-exportation')}
                  className="flex items-center w-full px-3 py-2 rounded-lg transition-colors duration-200 focus:outline-none text-left font-medium text-blue-700 dark:text-blue-200 bg-yellow-100 dark:bg-yellow-900 mt-2"
                >
                  <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V4a2 2 0 10-4 0v1.341C7.67 7.165 6 9.388 6 12v2.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                  {sidebarOpen && (
                    <span>
                      Répondre aux demandes d'exportation
                      <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-red-600 text-white">{pendingExports}</span>
                    </span>
                  )}
                </button>
              )}
            </nav>
          </div>
        </div>
        {/* Main content */}
        <div className="flex-1 flex flex-col">
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
          {/* Confirmation logout */}
          {showLogoutConfirm && (
            <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
              <div className="bg-white dark:bg-gray-800 p-6 rounded shadow-lg max-w-sm w-full">
                <h2 className="text-lg font-bold mb-4 text-gray-900 dark:text-white">Confirmer la déconnexion</h2>
                <p className="mb-4 text-gray-700 dark:text-gray-300">Voulez-vous vraiment vous déconnecter ?</p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setShowLogoutConfirm(false)}
                    className="bg-gray-400 hover:bg-gray-500 text-white px-4 py-2 rounded font-medium"
                  >
                    Annuler
                  </button>
                  <button
                    onClick={handleLogout}
                    className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded font-medium"
                  >
                    Se déconnecter
                  </button>
              </div>
              </div>
            </div>
          )}
          {/* Contenu principal dynamique */}
          <main className="flex-1 p-6 overflow-y-auto">
            {renderContent()}
          </main>
        </div>
      </div>
    </div>
  );
};

export default DashboardMedecin; 
import React, { useEffect, useState } from 'react';
import { exportationService, dossierMedicalService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import useDarkMode from '../hooks/useDarkMode';

const API_BASE_URL = "http://localhost:8000";

const MesDemandesExportation = () => {
  const { user } = useAuth();
  const [darkMode] = useDarkMode();
  const [demandes, setDemandes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [exportDone, setExportDone] = useState(false);
  const [dossiers, setDossiers] = useState([]);
  const [loadingDossiers, setLoadingDossiers] = useState(false);

  // Vérifier s'il y a une demande en attente ou approuvée (déclaré AVANT tout usage)
  const demandeEnAttente = demandes.find(d => d.statut === 'EN_ATTENTE');
  const demandeApprouvee = demandes.find(d => d.statut === 'APPROUVEE');

  // Charger les demandes de l'utilisateur
  const fetchDemandes = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const res = await exportationService.mesDemandes(token);
      setDemandes(res.data || res);
    } catch (err) {
      setError("Erreur lors du chargement des demandes.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDemandes();
    // eslint-disable-next-line
  }, []);

  // Charger les dossiers médicaux si demande approuvée
  useEffect(() => {
    if (demandeApprouvee) {
      setLoadingDossiers(true);
      dossierMedicalService.getMesDossiers()
        .then(res => setDossiers(res.data.dossiers || res.data || []))
        .catch(() => setDossiers([]))
        .finally(() => setLoadingDossiers(false));
    }
  }, [demandeApprouvee]);

  // Créer une nouvelle demande
  const handleDemanderExport = async () => {
    setIsSubmitting(true);
    setError(null);
    setSuccess(null);
    try {
      const token = localStorage.getItem('token');
      const data = {
        medecin: user.medecin,
        donnees_autorisees: {}, // à remplir si besoin
      };
      await exportationService.creerDemande(data, token);
      setSuccess('Demande envoyée avec succès.');
      fetchDemandes();
    } catch (err) {
      setError(err?.response?.data?.detail || err?.response?.data || "Erreur lors de la demande.");
    } finally {
      setIsSubmitting(false);
    }
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

  const handleExportAndLock = async (exportFunc) => {
    await exportFunc();
    setExportDone(true);
  };

  // Vérifier s'il y a une demande en attente
  // const demandeEnAttente = demandes.find(d => d.statut === 'EN_ATTENTE');
  // Vérifier s'il y a une demande approuvée non exportée
  // const demandeApprouvee = demandes.find(d => d.statut === 'APPROUVEE');

  // Fonctions d'export par dossier
  const handleExportDossierCSV = (dossierId) => {
    downloadFile(
      `${API_BASE_URL}/api/export/dossier-medical/${dossierId}/`,
      `dossier_${dossierId}.csv`
    );
  };
  const handleExportDossierPDF = (dossierId) => {
    downloadFile(
      `${API_BASE_URL}/api/export/dossier-medical-pdf/${dossierId}/`,
      `dossier_${dossierId}.pdf`
    );
  };

  const handleExporterAnalyseCSV = () => {
    if (demandeApprouvee && demandeApprouvee.resultat_analyse_id) {
      handleExportAndLock(() => downloadFile(
        `${API_BASE_URL}/api/export/resultats-analyse/${demandeApprouvee.resultat_analyse_id}/`,
        `resultats_analyse_${demandeApprouvee.resultat_analyse_id}.csv`
      ));
    } else {
      alert('Aucun résultat d\'analyse à exporter.');
    }
  };

  const handleExporterAnalysePDF = () => {
    if (demandeApprouvee && demandeApprouvee.resultat_analyse_id) {
      handleExportAndLock(() => downloadFile(
        `${API_BASE_URL}/api/export/resultats-analyse-pdf/${demandeApprouvee.resultat_analyse_id}/`,
        `resultats_analyse_${demandeApprouvee.resultat_analyse_id}.pdf`
      ));
    } else {
      alert('Aucun résultat d\'analyse à exporter.');
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-8 p-6 bg-white dark:bg-gray-800 rounded shadow">
      <h2 className="text-2xl font-bold mb-4 text-blue-700 dark:text-blue-200">Mes demandes d'exportation</h2>
      {loading ? (
        <div className="text-center py-8">Chargement...</div>
      ) : (
        <>
          {error && <div className="mb-4 text-red-600">{error}</div>}
          {success && <div className="mb-4 text-green-600">{success}</div>}

          {/* Bouton demander exportation */}
          {!demandeEnAttente && !demandeApprouvee && (
            <button
              onClick={handleDemanderExport}
              disabled={isSubmitting}
              className="mb-6 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition disabled:opacity-50"
            >
              Demander l'exportation de mes données
            </button>
          )}

          {/* Liste des demandes */}
          <div className="space-y-4">
            {demandes.length === 0 ? (
              <div className="text-gray-500">Aucune demande d'exportation.</div>
            ) : (
              demandes.map((demande) => (
                <div key={demande.id} className="border rounded p-4 flex flex-col md:flex-row md:items-center md:justify-between bg-gray-50 dark:bg-gray-900">
                  <div>
                    <div className="font-semibold text-gray-800 dark:text-gray-200">Demande #{demande.id}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Médecin : {demande.medecin_nom}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Date : {new Date(demande.date_demande).toLocaleString()}</div>
                  </div>
                  <div className="mt-2 md:mt-0 flex flex-col items-end">
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                      demande.statut === 'EN_ATTENTE' ? 'bg-yellow-100 text-yellow-800' :
                      demande.statut === 'APPROUVEE' ? 'bg-green-100 text-green-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {demande.statut === 'EN_ATTENTE' && 'En attente'}
                      {demande.statut === 'APPROUVEE' && 'Approuvée'}
                      {demande.statut === 'REFUSEE' && 'Refusée'}
                    </span>
                    {demande.statut === 'REFUSEE' && demande.commentaire_medecin && (
                      <span className="text-xs text-gray-500 mt-1">Motif : {demande.commentaire_medecin}</span>
                    )}
                    {/* Bouton exporter si approuvé */}
                    {demande.statut === 'APPROUVEE' && !exportDone && (
                      <div className="flex flex-col items-center justify-center min-h-[40vh]">
                        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 w-full max-w-2xl border border-blue-100 dark:border-gray-700">
                          <div className="flex items-center justify-between mb-6">
                            <h3 className="text-xl font-extrabold text-blue-700 dark:text-blue-200 flex items-center gap-2">
                              <svg className="w-7 h-7 text-blue-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M12 4v16m8-8H4"/></svg>
                              Exporter les données
                            </h3>
                            <span className="bg-green-100 text-green-700 px-4 py-1 rounded-full font-semibold text-sm shadow">Approuvée</span>
                          </div>
                          <div className="overflow-x-auto rounded-lg border border-blue-50 dark:border-gray-700">
                            <table className="min-w-full divide-y divide-blue-200 dark:divide-gray-700">
                              <thead className="bg-blue-50 dark:bg-blue-900">
                                <tr>
                                  <th className="px-6 py-3 text-left text-xs font-bold text-blue-700 dark:text-blue-200 uppercase tracking-wider">ID</th>
                                  <th className="px-6 py-3 text-left text-xs font-bold text-blue-700 dark:text-blue-200 uppercase tracking-wider">Date création</th>
                                  <th className="px-6 py-3 text-center text-xs font-bold text-blue-700 dark:text-blue-200 uppercase tracking-wider">Actions</th>
                                </tr>
                              </thead>
                              <tbody className="bg-white dark:bg-gray-800 divide-y divide-blue-100 dark:divide-gray-700">
                                {dossiers.map((dossier, idx) => (
                                  <tr key={dossier.idDossier} className="hover:bg-blue-50 dark:hover:bg-blue-900 transition">
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white font-semibold">{dossier.idDossier}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">{dossier.dateCreation}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-center">
                                      <button
                                        className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white px-5 py-2 rounded-lg shadow font-bold transition transform hover:scale-105"
                                        onClick={() => handleExportDossierPDF(dossier.idDossier)}
                                      >
                                        <svg className="inline w-5 h-5 mr-2 -mt-1" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M12 4v16m8-8H4"/></svg>
                                        Exporter PDF
                                      </button>
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      </div>
                    )}
                    {demande.statut === 'APPROUVEE' && exportDone && (
                      <div className="mt-6 text-green-700 font-bold">Exportation effectuée. Vous n'avez plus accès à l'export tant qu'une nouvelle demande n'est pas approuvée.</div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default MesDemandesExportation; 
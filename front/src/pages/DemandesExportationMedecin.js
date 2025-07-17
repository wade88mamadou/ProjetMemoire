import React, { useEffect, useState } from 'react';
import { exportationService } from '../services/api';

const DemandesExportationMedecin = () => {
  const [demandes, setDemandes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [motifsRefus, setMotifsRefus] = useState({});

  // Charger les demandes à traiter
  const fetchDemandes = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const res = await exportationService.demandesATraiter(token);
      setDemandes(res.data || res);
    } catch (err) {
      setError("Erreur lors du chargement des demandes.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDemandes();
  }, []);

  // Valider une demande
  const handleValider = async (demandeId) => {
    setIsSubmitting(true);
    setError(null);
    setSuccess(null);
    try {
      const token = localStorage.getItem('token');
      await exportationService.traiterDemande(demandeId, { statut: 'APPROUVEE' }, token);
      setSuccess('Demande approuvée !');
      fetchDemandes();
    } catch (err) {
      setError("Erreur lors de la validation.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Refuser une demande
  const handleRefuser = async (demandeId) => {
    setIsSubmitting(true);
    setError(null);
    setSuccess(null);
    try {
      const token = localStorage.getItem('token');
      await exportationService.traiterDemande(demandeId, { statut: 'REFUSEE', commentaire_medecin: motifsRefus[demandeId] || '' }, token);
      setSuccess('Demande refusée.');
      fetchDemandes();
    } catch (err) {
      setError("Erreur lors du refus.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto mt-8 p-6 bg-white dark:bg-gray-800 rounded shadow">
      <h2 className="text-2xl font-bold mb-4 text-blue-700 dark:text-blue-200">Demandes d'exportation à traiter</h2>
      {loading ? (
        <div className="text-center py-8">Chargement...</div>
      ) : (
        <>
          {error && <div className="mb-4 text-red-600">{error}</div>}
          {success && <div className="mb-4 text-green-600">{success}</div>}
          <div className="space-y-4">
            {demandes.length === 0 ? (
              <div className="text-gray-500">Aucune demande en attente.</div>
            ) : (
              demandes.map((demande) => (
                <div key={demande.id} className="border rounded p-4 bg-gray-50 dark:bg-gray-900 flex flex-col md:flex-row md:items-center md:justify-between">
                  <div>
                    <div className="font-semibold text-gray-800 dark:text-gray-200">Demande #{demande.id}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Demandeur : {demande.demandeur_nom}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Date : {new Date(demande.date_demande).toLocaleString()}</div>
                  </div>
                  <div className="mt-2 md:mt-0 flex flex-col items-end gap-2">
                    <button
                      onClick={() => handleValider(demande.id)}
                      disabled={isSubmitting}
                      className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition disabled:opacity-50"
                    >
                      Valider
                    </button>
                    <button
                      onClick={() => handleRefuser(demande.id)}
                      disabled={isSubmitting}
                      className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition disabled:opacity-50"
                    >
                      Refuser
                    </button>
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

export default DemandesExportationMedecin; 
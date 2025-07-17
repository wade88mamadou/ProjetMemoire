import React, { useEffect, useState } from 'react';
import { accesService } from '../services/api';

const AuditAcces = () => {
  const [acces, setAcces] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAcces = async () => {
      try {
        setLoading(true);
        const res = await accesService.getAcces();
        console.log('Réponse API accès:', res); // Debug
        console.log('Type de res.data:', typeof res.data); // Debug
        console.log('Est un tableau?', Array.isArray(res.data)); // Debug
        
        // S'assurer que acces est toujours un tableau
        const accesData = Array.isArray(res.data) ? res.data : [];
        setAcces(accesData);
      } catch (e) {
        console.error('Erreur lors de la récupération des accès:', e);
        setAcces([]);
      } finally {
        setLoading(false);
      }
    };
    fetchAcces();
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Audit des accès (traçabilité)</h2>
      {loading ? (
        <div className="text-center text-gray-500">Chargement...</div>
      ) : acces.length === 0 ? (
        <div className="text-center text-gray-500">Aucun accès enregistré.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-4 py-2 text-left">Date</th>
                <th className="px-4 py-2 text-left">Utilisateur</th>
                <th className="px-4 py-2 text-left">Type d'accès</th>
                <th className="px-4 py-2 text-left">Règle associée</th>
                <th className="px-4 py-2 text-left">Données concernées</th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {acces.map((a) => (
                <tr key={a.id || a.idAcces}>
                  <td className="px-4 py-2">{a.dateAcces}</td>
                  <td className="px-4 py-2">{a.utilisateur || '-'}</td>
                  <td className="px-4 py-2">{a.typeAcces}</td>
                  <td className="px-4 py-2">{a.regle ? (a.regle.nomRegle || a.regle) : '-'}</td>
                  <td className="px-4 py-2">{a.donnees_concernees || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default AuditAcces; 
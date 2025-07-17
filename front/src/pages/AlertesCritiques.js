import React, { useEffect, useState } from 'react';
import { getAlertesCritiques } from '../services/api';

const graviteColors = {
  critique: 'bg-red-100 text-red-800',
  warning: 'bg-yellow-100 text-yellow-800',
  info: 'bg-blue-100 text-blue-800',
};

const AlertesCritiques = () => {
  const [alertes, setAlertes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAlertes = async () => {
      try {
        setLoading(true);
        const data = await getAlertesCritiques();
        setAlertes(data);
      } catch (e) {
        setAlertes([]);
      } finally {
        setLoading(false);
      }
    };
    fetchAlertes();
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Alertes critiques de sécurité & conformité</h2>
      {loading ? (
        <div className="text-center text-gray-500">Chargement...</div>
      ) : alertes.length === 0 ? (
        <div className="text-center text-gray-500">Aucune alerte critique détectée.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-4 py-2 text-left">Type</th>
                <th className="px-4 py-2 text-left">Gravité</th>
                <th className="px-4 py-2 text-left">Message</th>
                <th className="px-4 py-2 text-left">Date</th>
                <th className="px-4 py-2 text-left">Utilisateur</th>
                <th className="px-4 py-2 text-left">Données concernées</th>
                <th className="px-4 py-2 text-left">Notifiée CDP</th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {alertes.map((a) => (
                <tr key={a.idAlerte}>
                  <td className="px-4 py-2 font-semibold">{a.typeAlerte}</td>
                  <td className="px-4 py-2">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${graviteColors[a.gravite] || 'bg-gray-100 text-gray-800'}`}>
                      {a.gravite}
                    </span>
                  </td>
                  <td className="px-4 py-2">{a.message}</td>
                  <td className="px-4 py-2">{a.dateAlerte}</td>
                  <td className="px-4 py-2">{a.utilisateur || '-'}</td>
                  <td className="px-4 py-2">{a.donnees_concernees || '-'}</td>
                  <td className="px-4 py-2">{a.notifie_cdp ? 'Oui' : 'Non'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default AlertesCritiques; 
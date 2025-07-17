import React, { useEffect, useState } from 'react';

const API_BASE_URL = "http://localhost:8000";

const RapportAudit = () => {
  const [acces, setAcces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [downloadMessage, setDownloadMessage] = useState("");

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/rapport-audit/`, {
      headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
    })
      .then(res => res.json())
      .then(data => setAcces(data))
      .finally(() => setLoading(false));
  }, []);

  const handleExportCSV = async () => {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/api/rapport-audit/?format=csv`, {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    if (!response.ok) {
      alert("Erreur lors de l'export CSV");
      return;
    }
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'rapport_audit.csv';
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
    setDownloadMessage('Fichier téléchargé !');
    setTimeout(() => setDownloadMessage(''), 3000);
  };
  const handleExportPDF = async () => {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/api/rapport-audit/?format=pdf`, {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    if (!response.ok) {
      alert("Erreur lors de l'export PDF");
      return;
    }
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'rapport_audit.pdf';
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
    setDownloadMessage('Fichier téléchargé !');
    setTimeout(() => setDownloadMessage(''), 3000);
  };

  return (
    <div className="max-w-4xl mx-auto mt-8 p-6 bg-white rounded shadow">
      <h2 className="text-2xl font-bold mb-4">Rapport d'audit des accès</h2>
      {downloadMessage && (
        <div className="mb-4 px-4 py-2 bg-green-100 text-green-800 rounded">
          {downloadMessage}
        </div>
      )}
      <button
        onClick={handleExportCSV}
        className="mb-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
      >
        Exporter en CSV
      </button>
      <button
        onClick={handleExportPDF}
        className="mb-4 ml-2 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition"
      >
        Exporter en PDF
      </button>
      {loading ? (
        <div>Chargement...</div>
      ) : Array.isArray(acces) ? (
        <table className="min-w-full border">
          <thead>
            <tr>
              <th className="border px-2 py-1">Date</th>
              <th className="border px-2 py-1">Utilisateur</th>
              <th className="border px-2 py-1">Type d'accès</th>
              <th className="border px-2 py-1">Données concernées</th>
            </tr>
          </thead>
          <tbody>
            {acces.map(a => (
              <tr key={a.id}>
                <td className="border px-2 py-1">{a.dateAcces}</td>
                <td className="border px-2 py-1">{a.utilisateur}</td>
                <td className="border px-2 py-1">{a.typeAcces}</td>
                <td className="border px-2 py-1">{a.donnees_concernees}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div className="text-red-600">Erreur lors du chargement des données d'audit.</div>
      )}
    </div>
  );
};

export default RapportAudit; 
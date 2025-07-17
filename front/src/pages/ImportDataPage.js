import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { importCSV } from '../services/api';

const ImportDataPage = () => {
  const { user } = useAuth();
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'text/csv') {
      setFile(selectedFile);
      setError('');
    } else {
      setError('Veuillez sélectionner un fichier CSV valide');
      setFile(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Veuillez sélectionner un fichier');
      return;
    }

    setIsLoading(true);
    setMessage('');
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await importCSV(formData);
      
      if (response.success) {
        setMessage(`Importation réussie ! ${response.patients_created} patients créés, ${response.dossiers_created} dossiers médicaux créés.`);
        setFile(null);
        // Reset file input
        e.target.reset();
      } else {
        setError(response.error || 'Erreur lors de l\'importation');
      }
    } catch (err) {
      setError('Erreur de connexion au serveur');
      console.error('Import error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Vérifier si l'utilisateur a les permissions (admin ou médecin)
  if (user?.role !== 'ADMIN' && user?.role !== 'MEDECIN') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-lg shadow-md p-6">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Accès refusé</h2>
            <p className="text-gray-600">Vous n'avez pas les permissions nécessaires pour importer des données.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Importation de données</h1>
            <p className="text-gray-600">
              Importez des données médicales depuis un fichier CSV. 
              Seuls les administrateurs et médecins peuvent effectuer cette opération.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="csv_file" className="block text-sm font-medium text-gray-700 mb-2">
                Fichier CSV
              </label>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md hover:border-gray-400 transition-colors">
                <div className="space-y-1 text-center">
                  <svg
                    className="mx-auto h-12 w-12 text-gray-400"
                    stroke="currentColor"
                    fill="none"
                    viewBox="0 0 48 48"
                    aria-hidden="true"
                  >
                    <path
                      d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                      strokeWidth={2}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  <div className="flex text-sm text-gray-600">
                    <label
                      htmlFor="csv_file"
                      className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500"
                    >
                      <span>Télécharger un fichier</span>
                      <input
                        id="csv_file"
                        name="csv_file"
                        type="file"
                        accept=".csv"
                        className="sr-only"
                        onChange={handleFileChange}
                        required
                      />
                    </label>
                    <p className="pl-1">ou glisser-déposer</p>
                  </div>
                  <p className="text-xs text-gray-500">CSV jusqu'à 10MB</p>
                </div>
              </div>
              {file && (
                <p className="mt-2 text-sm text-green-600">
                  ✓ Fichier sélectionné : {file.name}
                </p>
              )}
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-red-800">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {message && (
              <div className="bg-green-50 border border-green-200 rounded-md p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-green-800">{message}</p>
                  </div>
                </div>
              </div>
            )}

            <div className="flex justify-end">
              <button
                type="submit"
                disabled={isLoading || !file}
                className={`px-6 py-2 border border-transparent text-sm font-medium rounded-md text-white ${
                  isLoading || !file
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
                }`}
              >
                {isLoading ? (
                  <div className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Importation en cours...
                  </div>
                ) : (
                  'Importer les données'
                )}
              </button>
            </div>
          </form>

          <div className="mt-8 bg-gray-50 rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Instructions d'importation</h3>
            <div className="space-y-3 text-sm text-gray-600">
              <p>• Le fichier CSV doit contenir les colonnes suivantes :</p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li>Informations patient (nom, prénom, date de naissance, etc.)</li>
                <li>Données médicales (dossier médical, analyses, etc.)</li>
                <li>Informations de résidence et logement</li>
                <li>Données de comportement et alimentation</li>
              </ul>
              <p>• L'importation peut prendre plusieurs minutes selon la taille du fichier</p>
              <p>• Les données existantes ne seront pas dupliquées</p>
              <p>• Seuls les administrateurs et médecins peuvent importer des données</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImportDataPage; 
// Script pour mettre à jour la navigation avec la nouvelle page d'alertes de conformité
const fs = require('fs');
const path = require('path');

// Chemin vers App.js
const appJsPath = path.join(__dirname, 'src', 'App.js');

// Lire le contenu actuel
let content = fs.readFileSync(appJsPath, 'utf8');

// Ajouter l'import pour la nouvelle page
if (!content.includes('ConfigAlertesConformite')) {
  // Ajouter l'import
  const importStatement = "import ConfigAlertesConformite from './pages/ConfigAlertesConformite';";
  const importIndex = content.indexOf('import ConfigAlertesSecurite');
  if (importIndex !== -1) {
    content = content.slice(0, importIndex) + importStatement + '\n' + content.slice(importIndex);
  }
}

// Ajouter la route
if (!content.includes('/config-alertes-conformite')) {
  const routePattern = /path="\/config-alertes-securite"/;
  const newRoute = '        <Route path="/config-alertes-conformite" element={<ConfigAlertesConformite />} />\n        <Route path="/config-alertes-securite"';
  content = content.replace(routePattern, newRoute);
}

// Sauvegarder les modifications
fs.writeFileSync(appJsPath, content, 'utf8');

console.log('✅ Navigation mise à jour avec la nouvelle page ConfigAlertesConformite');
console.log('📝 Ajoutez manuellement le lien dans votre menu de navigation :');
console.log('   <Link to="/config-alertes-conformite">Nouveau Système d\'Alertes</Link>'); 
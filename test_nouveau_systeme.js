// Script de test pour le nouveau système d'alertes de conformité
const axios = require('axios');

const API_BASE_URL = 'http://localhost:8000/api';

// Configuration axios
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  }
});

async function testNouveauSysteme() {
  console.log('🧪 TEST DU NOUVEAU SYSTÈME D\'ALERTES DE CONFORMITÉ\n');

  try {
    // Test 1: Configuration
    console.log('1️⃣ Test de la configuration...');
    const configResponse = await api.get('/conformite/configuration/');
    console.log('   ✅ Configuration accessible');
    console.log('   📊 Données:', configResponse.data);

    // Test 2: Types d'alertes
    console.log('\n2️⃣ Test des types d\'alertes...');
    const typesResponse = await api.get('/types-alertes-conformite/');
    console.log('   ✅ Types d\'alertes accessibles');
    console.log(`   📊 ${typesResponse.data.length} types trouvés`);

    // Test 3: Règles d'alertes
    console.log('\n3️⃣ Test des règles d\'alertes...');
    const reglesResponse = await api.get('/regles-alertes-conformite/');
    console.log('   ✅ Règles d\'alertes accessibles');
    console.log(`   📊 ${reglesResponse.data.length} règles trouvées`);

    // Test 4: Alertes actives
    console.log('\n4️⃣ Test des alertes actives...');
    const alertesResponse = await api.get('/alertes-conformite/');
    console.log('   ✅ Alertes actives accessibles');
    console.log(`   📊 ${alertesResponse.data.length} alertes trouvées`);

    // Test 5: Statistiques
    console.log('\n5️⃣ Test des statistiques...');
    const statsResponse = await api.get('/conformite/statistiques-detaillees/');
    console.log('   ✅ Statistiques accessibles');
    console.log('   📊 Données:', statsResponse.data);

    // Test 6: Exécution de surveillance
    console.log('\n6️⃣ Test de la surveillance...');
    const surveillanceResponse = await api.post('/conformite/surveillance/');
    console.log('   ✅ Surveillance exécutée');
    console.log('   📊 Résultat:', surveillanceResponse.data);

    console.log('\n🎉 TOUS LES TESTS SONT RÉUSSIS !');
    console.log('\n📋 RÉSUMÉ:');
    console.log(`   • Types d'alertes: ${typesResponse.data.length}`);
    console.log(`   • Règles configurées: ${reglesResponse.data.length}`);
    console.log(`   • Alertes actives: ${alertesResponse.data.length}`);
    console.log(`   • Surveillance: Fonctionnelle`);

    console.log('\n🚀 LE NOUVEAU SYSTÈME EST OPÉRATIONNEL !');
    console.log('\n📝 PROCHAINES ÉTAPES:');
    console.log('   1. Accéder à http://localhost:3000/config-alertes-conformite');
    console.log('   2. Configurer vos règles spécifiques');
    console.log('   3. Tester les notifications');
    console.log('   4. Former les utilisateurs');

  } catch (error) {
    console.error('❌ ERREUR LORS DU TEST:', error.message);
    
    if (error.response) {
      console.error('   📊 Status:', error.response.status);
      console.error('   📊 Données:', error.response.data);
    }
    
    console.log('\n🔧 SOLUTIONS:');
    console.log('   1. Vérifiez que le serveur backend fonctionne: python manage.py runserver');
    console.log('   2. Vérifiez que les migrations sont appliquées: python manage.py migrate');
    console.log('   3. Vérifiez que l\'initialisation est faite: python initialiser_alertes_conformite.py');
  }
}

// Exécuter le test
testNouveauSysteme(); 
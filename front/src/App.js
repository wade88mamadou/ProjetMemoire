import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import SecureNavigation from './components/SecureNavigation';

// Pages
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import SimpleResetPage from './pages/SimpleResetPage';
import DashboardAdmin from './pages/DashboardAdmin';
import DashboardMedecin from './pages/DashboardMedecin';
import DashboardUserSimple from './pages/DashboardUserSimple';
import DashboardRedirect from './pages/DashboardRedirect';
import UnauthorizedPage from './pages/UnauthorizedPage';
import AdminUserManagement from './pages/AdminUserManagement';
import ImportDataPage from './pages/ImportDataPage';
import MesDemandesExportation from './pages/MesDemandesExportation';
import DemandesExportationMedecin from './pages/DemandesExportationMedecin';
import AlertesCritiques from './pages/AlertesCritiques';
import ConfigAlertesSecurite from './pages/ConfigAlertesSecurite';
import RapportAudit from './pages/RapportAudit';
import ContactPage from './pages/ContactPage';
import AboutPage from './pages/AboutPage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <SecureNavigation />
          <Routes>
            {/* Routes publiques */}
            <Route path="/" element={<HomePage />} />
            <Route path="/contact" element={<ContactPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/simple-reset" element={<SimpleResetPage />} />
            <Route path="/unauthorized" element={<UnauthorizedPage />} />
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <DashboardRedirect />
                </ProtectedRoute>
              } 
            />
            
            {/* Routes protégées par rôle */}
            <Route 
              path="/admin/dashboard" 
              element={
                <ProtectedRoute requiredRole="ADMIN">
                  <DashboardAdmin />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/medecin/dashboard" 
              element={
                <ProtectedRoute requiredRole="MEDECIN">
                  <DashboardMedecin />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/user/dashboard" 
              element={
                <ProtectedRoute requiredRole="user_simple">
                  <DashboardUserSimple />
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/admin/users" 
              element={
                <ProtectedRoute requiredRole="ADMIN">
                  <AdminUserManagement />
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/import-data" 
              element={
                <ProtectedRoute requiredRole={["ADMIN", "MEDECIN"]}>
                  <ImportDataPage />
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/user/mes-demandes-exportation" 
              element={
                <ProtectedRoute requiredRole="user_simple">
                  <MesDemandesExportation />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/medecin/demandes-exportation" 
              element={
                <ProtectedRoute requiredRole="MEDECIN">
                  <DemandesExportationMedecin />
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/alertes-critiques" 
              element={
                <ProtectedRoute requiredRole="ADMIN">
                  <AlertesCritiques />
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/config-alertes-securite" 
              element={
                <ProtectedRoute requiredRole="ADMIN">
                  <ConfigAlertesSecurite />
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/admin/rapport-audit" 
              element={
                <ProtectedRoute requiredRole="ADMIN">
                  <RapportAudit />
                </ProtectedRoute>
              } 
            />

            
            {/* Route par défaut - redirige vers l'accueil */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;

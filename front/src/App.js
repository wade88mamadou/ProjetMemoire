import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import DashboardAdmin from './pages/DashboardAdmin';
import DashboardMedecin from './pages/DashboardMedecin';
import DashboardUserSimple from './pages/DashboardUserSimple';
import UnauthorizedPage from './pages/UnauthorizedPage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Routes publiques */}
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/unauthorized" element={<UnauthorizedPage />} />
            
            {/* Routes protégées par rôle */}
            <Route 
              path="/admin/dashboard" 
              element={
                <ProtectedRoute requiredRole="administrateur">
                  <DashboardAdmin />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/medecin/dashboard" 
              element={
                <ProtectedRoute requiredRole="medecin">
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
            
            {/* Route par défaut - redirige vers l'accueil */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;

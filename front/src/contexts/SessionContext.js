import React, { createContext, useContext, useEffect, useRef, useState } from 'react';
import { useAuth } from './AuthContext';
import api from '../services/api';

const SessionContext = createContext();

export const useSession = () => {
    const context = useContext(SessionContext);
    if (!context) {
        throw new Error('useSession must be used within a SessionProvider');
    }
    return context;
};

export const SessionProvider = ({ children }) => {
    const { user, logout } = useAuth();
    const [sessionActive, setSessionActive] = useState(true);
    const [timeRemaining, setTimeRemaining] = useState(60);
    const [showWarning, setShowWarning] = useState(false);
    const [showExpired, setShowExpired] = useState(false);
    
    const activityTimer = useRef(null);
    const warningTimer = useRef(null);
    const expirationTimer = useRef(null);
    const refreshTimer = useRef(null);
    
    const SESSION_TIMEOUT = 60; // 1 minute en secondes
    const WARNING_TIME = 30;    // 30 secondes avant avertissement
    const REFRESH_INTERVAL = 45; // Refresh toutes les 45 secondes
    
    // Fonction pour réinitialiser l'activité
    const resetActivity = () => {
        if (activityTimer.current) {
            clearTimeout(activityTimer.current);
        }
        if (warningTimer.current) {
            clearTimeout(warningTimer.current);
        }
        if (expirationTimer.current) {
            clearTimeout(expirationTimer.current);
        }
        
        setShowWarning(false);
        setShowExpired(false);
        setSessionActive(true);
        setTimeRemaining(SESSION_TIMEOUT);
        
        // Programmer les timers
        warningTimer.current = setTimeout(() => {
            setShowWarning(true);
        }, (SESSION_TIMEOUT - WARNING_TIME) * 1000);
        
        expirationTimer.current = setTimeout(() => {
            setShowExpired(true);
            setSessionActive(false);
            handleSessionExpired();
        }, SESSION_TIMEOUT * 1000);
    };
    
    // Fonction pour gérer l'expiration de session
    const handleSessionExpired = () => {
        logout();
        // Redirection vers la page de login avec message d'expiration
        window.location.href = '/login?expired=true';
    };
    
    // Fonction pour refresh la session
    const refreshSession = async () => {
        try {
            const response = await api.post('/auth/refresh-session/');
            if (response.data.success) {
                // Mettre à jour le token dans le contexte d'authentification
                localStorage.setItem('accessToken', response.data.access_token);
                localStorage.setItem('refreshToken', response.data.refresh_token);
                
                resetActivity();
                console.log('Session refreshée avec succès');
            }
        } catch (error) {
            console.error('Erreur lors du refresh de session:', error);
            handleSessionExpired();
        }
    };
    
    // Fonction pour étendre la session
    const extendSession = async () => {
        await refreshSession();
        setShowWarning(false);
    };
    
    // Fonction pour déconnexion sécurisée
    const secureLogout = async () => {
        try {
            await api.post('/auth/logout-secure/');
        } catch (error) {
            console.error('Erreur lors de la déconnexion sécurisée:', error);
        } finally {
            logout();
        }
    };
    
    // Écouter les événements d'activité utilisateur
    useEffect(() => {
        if (!user) return;
        
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
        
        const handleUserActivity = () => {
            resetActivity();
        };
        
        // Ajouter les listeners d'événements
        events.forEach(event => {
            document.addEventListener(event, handleUserActivity, true);
        });
        
        // Timer pour le refresh automatique
        refreshTimer.current = setInterval(() => {
            if (sessionActive && user) {
                refreshSession();
            }
        }, REFRESH_INTERVAL * 1000);
        
        // Timer pour mettre à jour le temps restant
        const updateTimeRemaining = () => {
            setTimeRemaining(prev => {
                const newTime = Math.max(0, prev - 1);
                return newTime;
            });
        };
        
        const timeInterval = setInterval(updateTimeRemaining, 1000);
        
        // Initialiser l'activité
        resetActivity();
        
        return () => {
            // Nettoyer les listeners
            events.forEach(event => {
                document.removeEventListener(event, handleUserActivity, true);
            });
            
            // Nettoyer les timers
            if (activityTimer.current) clearTimeout(activityTimer.current);
            if (warningTimer.current) clearTimeout(warningTimer.current);
            if (expirationTimer.current) clearTimeout(expirationTimer.current);
            if (refreshTimer.current) clearInterval(refreshTimer.current);
            clearInterval(timeInterval);
        };
    }, [user, sessionActive]);
    
    // Effet pour nettoyer quand l'utilisateur se déconnecte
    useEffect(() => {
        if (!user) {
            setSessionActive(false);
            setShowWarning(false);
            setShowExpired(false);
            setTimeRemaining(0);
        }
    }, [user]);
    
    const value = {
        sessionActive,
        timeRemaining,
        showWarning,
        showExpired,
        extendSession,
        secureLogout,
        refreshSession
    };
    
    return (
        <SessionContext.Provider value={value}>
            {children}
            
            {/* Modal d'avertissement */}
            {showWarning && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full mx-4">
                        <h3 className="text-lg font-semibold text-red-600 mb-4">
                            ⚠️ Session sur le point d'expirer
                        </h3>
                        <p className="text-gray-700 mb-4">
                            Votre session expirera dans {timeRemaining} secondes en raison d'inactivité.
                            Cliquez sur "Continuer" pour rester connecté.
                        </p>
                        <div className="flex justify-end space-x-3">
                            <button
                                onClick={secureLogout}
                                className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
                            >
                                Se déconnecter
                            </button>
                            <button
                                onClick={extendSession}
                                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                            >
                                Continuer
                            </button>
                        </div>
                    </div>
                </div>
            )}
            
            {/* Modal d'expiration */}
            {showExpired && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full mx-4">
                        <h3 className="text-lg font-semibold text-red-600 mb-4">
                            🔒 Session expirée
                        </h3>
                        <p className="text-gray-700 mb-4">
                            Votre session a expiré en raison d'inactivité.
                            Vous allez être redirigé vers la page de connexion.
                        </p>
                        <div className="flex justify-center">
                            <button
                                onClick={() => window.location.href = '/login'}
                                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                            >
                                Se reconnecter
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </SessionContext.Provider>
    );
}; 
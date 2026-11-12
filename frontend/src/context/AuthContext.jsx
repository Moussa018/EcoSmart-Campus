import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

const DEMO_ACCOUNTS = {
  gestionnaire: {
    email: 'admin@campus.fr',
    nom: 'Moussa Mohammed (Gestionnaire)',
    role: 'gestionnaire',
    batiment_id: 'bat-a',
    token: 'mock-jwt-token-gestionnaire-sprint1',
  },
  technicien: {
    email: 'tech@campus.fr',
    nom: 'Reghioui Mohamed (Technicien)',
    role: 'technicien',
    batiment_id: 'bat-a',
    token: 'mock-jwt-token-technicien-sprint1',
  },
  etudiant: {
    email: 'etudiant@campus.fr',
    nom: 'Benomar Youssef (Étudiant)',
    role: 'etudiant',
    batiment_id: 'bat-b',
    token: 'mock-jwt-token-etudiant-sprint1',
  },
  direction: {
    email: 'direction@campus.fr',
    nom: 'Najib Ibrahim (Direction)',
    role: 'direction',
    batiment_id: 'bat-d',
    token: 'mock-jwt-token-direction-sprint1',
  },
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('ecosmart_token') || null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Vérification de la session stockée
    const savedUser = localStorage.getItem('ecosmart_user');
    const savedToken = localStorage.getItem('ecosmart_token');
    if (savedUser && savedToken) {
      try {
        setUser(JSON.parse(savedUser));
        setToken(savedToken);
      } catch (e) {
        localStorage.removeItem('ecosmart_user');
        localStorage.removeItem('ecosmart_token');
      }
    } else {
      // Connexion par défaut en tant que Gestionnaire pour une démo immédiate
      const defaultAccount = DEMO_ACCOUNTS.gestionnaire;
      setUser(defaultAccount);
      setToken(defaultAccount.token);
      localStorage.setItem('ecosmart_user', JSON.stringify(defaultAccount));
      localStorage.setItem('ecosmart_token', defaultAccount.token);
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (res.ok) {
        const data = await res.json();
        setUser(data.user);
        setToken(data.access_token);
        localStorage.setItem('ecosmart_user', JSON.stringify(data.user));
        localStorage.setItem('ecosmart_token', data.access_token);
        return { success: true };
      }
    } catch (err) {
      console.warn('API indisponible, tentative de fallback sur compte de démo...');
    }

    // Fallback sur comptes de démo locaux
    const foundRole = Object.keys(DEMO_ACCOUNTS).find(
      (r) => DEMO_ACCOUNTS[r].email === email
    );
    if (foundRole) {
      const acc = DEMO_ACCOUNTS[foundRole];
      setUser(acc);
      setToken(acc.token);
      localStorage.setItem('ecosmart_user', JSON.stringify(acc));
      localStorage.setItem('ecosmart_token', acc.token);
      return { success: true };
    }

    return { success: false, error: 'Identifiants invalides' };
  };

  const loginAsRole = (role) => {
    const acc = DEMO_ACCOUNTS[role] || DEMO_ACCOUNTS.gestionnaire;
    setUser(acc);
    setToken(acc.token);
    localStorage.setItem('ecosmart_user', JSON.stringify(acc));
    localStorage.setItem('ecosmart_token', acc.token);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('ecosmart_user');
    localStorage.removeItem('ecosmart_token');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        loading,
        login,
        loginAsRole,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

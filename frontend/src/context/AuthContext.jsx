import React, { createContext, useContext, useState, useEffect } from 'react';
import { api, getToken, setToken, removeToken } from '../api';
import { supabase, isSupabaseConfigured } from '../supabaseClient';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [checkingAuth, setCheckingAuth] = useState(true);

  const hydrateProfile = async () => {
    try {
      const data = await api.me();
      if (data && data.user) {
        setCurrentUser(data.user);
        return data.user;
      }
      return null;
    } catch (err) {
      console.warn('Session verification note:', err);
      // Only purge token if server explicitly confirms the session is invalid (HTTP 401)
      if (err.status === 401) {
        removeToken();
        setCurrentUser(null);
      }
      return null;
    }
  };

  const initAuth = async () => {
    // 1. Check if token was provided in URL query parameters (e.g. from GitHub OAuth or redirect)
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const urlToken = urlParams.get('token');
      if (urlToken) {
        setToken(urlToken);
        const newPath = window.location.pathname === '/login' ? '/dashboard' : window.location.pathname;
        window.history.replaceState({}, document.title, newPath);
      }
    } catch (e) {
      console.warn('Could not parse OAuth query params:', e);
    }

    // 2. If Supabase is configured, check for existing Supabase session
    if (isSupabaseConfigured && supabase) {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (session && session.access_token) {
          setToken(session.access_token);
          if (session.user) {
            setCurrentUser({
              id: session.user.id,
              username: session.user.user_metadata?.username || session.user.email?.split('@')[0] || 'Learner',
              email: session.user.email,
              target_role: session.user.user_metadata?.target_role || 'ML Engineer'
            });
          }
        }
      } catch (e) {
        console.warn('Supabase getSession error:', e);
      }
    }

    // 3. Check stored token (either from Supabase or direct API)
    const token = getToken();
    if (!token) {
      setCurrentUser(null);
      setCheckingAuth(false);
      return;
    }

    // 4. Hydrate profile from backend API
    await hydrateProfile();
    setCheckingAuth(false);
  };

  useEffect(() => {
    initAuth();

    // Set up Supabase auth listener if configured
    let authListener = null;
    if (isSupabaseConfigured && supabase) {
      const { data } = supabase.auth.onAuthStateChange(async (event, session) => {
        if (session && session.access_token) {
          setToken(session.access_token);
          await hydrateProfile();
        } else if (event === 'SIGNED_OUT') {
          removeToken();
          setCurrentUser(null);
        }
      });
      authListener = data?.subscription;
    }

    return () => {
      if (authListener) authListener.unsubscribe();
    };
  }, []);

  const login = async (identifier, password) => {
    // If Supabase is configured and identifier is an email (or standard), authenticate via Supabase
    if (isSupabaseConfigured && supabase) {
      const email = identifier.includes('@') ? identifier : `${identifier}@skillpath.local`;
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        // Fallback to backend local-login if Supabase fails (e.g. legacy local account)
        try {
          const res = await api.login(identifier, password);
          if (res && res.token) {
            setToken(res.token);
            if (res.user) setCurrentUser(res.user);
            hydrateProfile().catch(() => {});
            return res.user || { username: identifier };
          }
        } catch {
          throw new Error(error.message || 'Authentication failed');
        }
      }

      if (data?.session?.access_token) {
        setToken(data.session.access_token);
        const supaUser = data.session.user;
        const initialUser = {
          id: supaUser?.id,
          username: supaUser?.user_metadata?.username || supaUser?.email?.split('@')[0] || identifier,
          email: supaUser?.email,
          target_role: supaUser?.user_metadata?.target_role || 'ML Engineer'
        };
        setCurrentUser(initialUser);
        hydrateProfile().catch(() => {});
        return initialUser;
      }
    }

    // Direct backend authentication fallback
    const res = await api.login(identifier, password);
    if (res && res.token) {
      setToken(res.token);
      if (res.user) setCurrentUser(res.user);
    }
    return await hydrateProfile();
  };

  const register = async (username, email, password, target_role) => {
    // If Supabase is configured, create user via Supabase Auth
    if (isSupabaseConfigured && supabase) {
      const userEmail = email || `${username}@skillpath.local`;
      const { data, error } = await supabase.auth.signUp({
        email: userEmail,
        password,
        options: {
          data: {
            username,
            target_role: target_role || 'ML Engineer'
          }
        }
      });

      if (error) {
        throw new Error(error.message);
      }

      if (data?.session?.access_token) {
        setToken(data.session.access_token);
        const supaUser = data.session.user;
        const initialUser = {
          id: supaUser?.id,
          username: supaUser?.user_metadata?.username || username,
          email: userEmail,
          target_role: target_role || 'ML Engineer'
        };
        setCurrentUser(initialUser);
        hydrateProfile().catch(() => {});
        return initialUser;
      } else if (data?.user) {
        // Try immediate sign-in in case session was not returned in signup response
        try {
          const { data: loginData } = await supabase.auth.signInWithPassword({
            email: userEmail,
            password,
          });
          if (loginData?.session?.access_token) {
            setToken(loginData.session.access_token);
            const supaUser = loginData.session.user;
            const initialUser = {
              id: supaUser?.id,
              username: supaUser?.user_metadata?.username || username,
              email: userEmail,
              target_role: target_role || 'ML Engineer'
            };
            setCurrentUser(initialUser);
            hydrateProfile().catch(() => {});
            return initialUser;
          }
        } catch {
          // Ignore and continue
        }
        
        // If email confirmation is enabled on Supabase, notify clearly
        if (!data.session) {
          throw new Error('Account created! Supabase email confirmation is enabled: please confirm your email or turn off "Confirm email" in Supabase Dashboard > Authentication > Providers > Email.');
        }
      }
    }

    // Direct backend register
    const res = await api.register(username, email, password, target_role);
    if (res && res.token) {
      setToken(res.token);
      if (res.user) setCurrentUser(res.user);
    }
    return await hydrateProfile();
  };

  const logout = async () => {
    try {
      if (isSupabaseConfigured && supabase) {
        await supabase.auth.signOut();
      }
      await api.logout();
    } catch (e) {
      console.warn('Logout API error:', e);
    } finally {
      removeToken();
      setCurrentUser(null);
    }
  };

  const updateUser = (updatedUser) => {
    setCurrentUser((prev) => (prev ? { ...prev, ...updatedUser } : updatedUser));
  };

  const value = {
    currentUser,
    isAuthenticated: !!currentUser,
    checkingAuth,
    isSupabaseConfigured,
    login,
    register,
    logout,
    updateUser,
    refreshUser: hydrateProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

import React from 'react';
import { Routes, Route, Navigate, Outlet, useNavigate } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './queryClient';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LearningProvider } from './context/LearningContext';

import Sidebar from './components/Sidebar';
import ErrorBoundary from './components/ErrorBoundary';

import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import ResumeUpload from './pages/ResumeUpload';
import SkillGap from './pages/SkillGap';
import LearningCatalog from './pages/LearningCatalog';
import LearningView from './pages/LearningView';
import QuizView from './pages/QuizView';
import QuizResults from './pages/QuizResults';
import Profile from './pages/Profile';

function ProtectedLayout() {
  const { currentUser, isAuthenticated, checkingAuth, logout } = useAuth();
  const navigate = useNavigate();

  if (checkingAuth) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'var(--bg-main)' }}>
        <div style={{ color: '#818cf8', fontSize: '1.05rem', fontWeight: '600' }}>Starting SkillPath AI...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="app-container">
      <Sidebar user={currentUser} onLogout={logout} />
      <main className="main-content">
        <ErrorBoundary navigate={navigate}>
          <Outlet />
        </ErrorBoundary>
      </main>
    </div>
  );
}

function PublicAuthRoute({ children }) {
  const { isAuthenticated, checkingAuth } = useAuth();

  if (checkingAuth) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'var(--bg-main)' }}>
        <div style={{ color: '#818cf8', fontSize: '1rem', fontWeight: '600' }}>Loading...</div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

function AppRoutes() {
  const { refreshUser } = useAuth();

  return (
    <Routes>
      {/* Public Auth Routes */}
      <Route
        path="/login"
        element={
          <PublicAuthRoute>
            <Login onAuthSuccess={refreshUser} />
          </PublicAuthRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicAuthRoute>
            <Register onAuthSuccess={refreshUser} />
          </PublicAuthRoute>
        }
      />
      <Route
        path="/signup"
        element={<Navigate to="/register" replace />}
      />

      {/* Protected Routes (Single mounted shell with persistent Sidebar) */}
      <Route element={<ProtectedLayout />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        
        {/* Learning Catalog & Path Aliases */}
        <Route path="/learning" element={<LearningCatalog />} />
        <Route path="/learning-path" element={<LearningCatalog />} />
        <Route path="/learning-centre" element={<LearningCatalog />} />
        <Route path="/learning-center" element={<LearningCatalog />} />
        
        {/* Course & Learning Video View */}
        <Route path="/learning/:topicId" element={<LearningView />} />
        <Route path="/learning/:topicId/module/:moduleId" element={<LearningView />} />
        <Route path="/course/:topicId" element={<LearningView />} />
        <Route path="/video/:videoId" element={<LearningView />} />
        
        {/* Quiz & Assessment */}
        <Route path="/quiz/:topicId" element={<QuizView />} />
        <Route path="/quiz/:quizId/results" element={<QuizResults />} />
        
        {/* User Profile & Skills */}
        <Route path="/profile" element={<Profile />} />
        <Route path="/resume" element={<ResumeUpload />} />
        <Route path="/skill-gap" element={<SkillGap />} />
        
        {/* Catch-all redirect */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <LearningProvider>
          <AppRoutes />
        </LearningProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

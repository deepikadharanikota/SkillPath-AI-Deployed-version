import React from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  BookOpen, 
  FileText, 
  GitPullRequest, 
  User, 
  LogOut, 
  Flame, 
  Clock,
  Sparkles
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Sidebar({ user: propUser, onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { currentUser, logout } = useAuth();
  const user = propUser || currentUser;

  const handleLogout = async () => {
    if (onLogout) {
      await onLogout();
    } else {
      await logout();
    }
    navigate('/login');
  };

  const navItems = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { 
      to: '/learning', 
      label: 'Learning Center', 
      icon: BookOpen,
      matchPrefixes: ['/learning', '/course', '/learning-path', '/learning-centre', '/learning-center']
    },
    { to: '/resume', label: 'Resume & Skills', icon: FileText },
    { to: '/skill-gap', label: 'Skill Gap Analysis', icon: GitPullRequest },
    { to: '/profile', label: 'Profile', icon: User },
  ];

  return (
    <aside style={{
      width: '260px',
      backgroundColor: 'rgba(15, 20, 35, 0.95)',
      backdropFilter: 'blur(20px)',
      borderRight: '1px solid rgba(255, 255, 255, 0.08)',
      display: 'flex',
      flexDirection: 'column',
      padding: '1.5rem 1rem',
      flexShrink: 0
    }}>
      {/* Brand Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '0 0.75rem', marginBottom: '2rem' }}>
        <div style={{
          width: '38px',
          height: '38px',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 12px rgba(99, 102, 241, 0.4)'
        }}>
          <Sparkles size={22} color="#fff" />
        </div>
        <div>
          <h1 style={{ fontSize: '1.2rem', fontWeight: '800', lineHeight: 1.1 }}>SkillPath <span style={{ color: '#a855f7' }}>AI</span></h1>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Adaptive Learning</span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '6px', flex: 1 }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isCustomActive = item.matchPrefixes 
            ? item.matchPrefixes.some(prefix => location.pathname.startsWith(prefix))
            : location.pathname === item.to;

          return (
            <NavLink
              key={item.to}
              to={item.to}
              style={({ isActive }) => {
                const active = isActive || isCustomActive;
                return {
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '10px 14px',
                  borderRadius: '10px',
                  color: active ? '#fff' : 'var(--text-muted)',
                  backgroundColor: active ? 'rgba(99, 102, 241, 0.18)' : 'transparent',
                  border: active ? '1px solid rgba(99, 102, 241, 0.35)' : '1px solid transparent',
                  textDecoration: 'none',
                  fontWeight: active ? '600' : '500',
                  fontSize: '0.92rem',
                  transition: 'all 0.15s ease'
                };
              }}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* User Stats Preview */}
      {user && (
        <div style={{
          backgroundColor: 'rgba(255, 255, 255, 0.03)',
          border: '1px solid var(--border-color)',
          borderRadius: '12px',
          padding: '12px',
          marginBottom: '1rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>Learner</span>
            <span style={{ fontSize: '0.85rem', fontWeight: '700', color: '#fff' }}>{user.username}</span>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <div style={{
              flex: 1,
              backgroundColor: 'rgba(245, 158, 11, 0.1)',
              padding: '6px 8px',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <Flame size={14} color="#f59e0b" />
              <span style={{ fontSize: '0.78rem', color: '#fcd34d', fontWeight: '600' }}>{user.streak || 0}d streak</span>
            </div>
            <div style={{
              flex: 1,
              backgroundColor: 'rgba(99, 102, 241, 0.1)',
              padding: '6px 8px',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <Clock size={14} color="#818cf8" />
              <span style={{ fontSize: '0.78rem', color: '#a5b4fc', fontWeight: '600' }}>{user.total_hours || 0}h</span>
            </div>
          </div>
        </div>
      )}

      {/* Logout */}
      <button
        onClick={handleLogout}
        className="btn-secondary"
        style={{
          width: '100%',
          padding: '10px',
          fontSize: '0.88rem',
          justifyContent: 'center',
          color: '#ef4444'
        }}
      >
        <LogOut size={16} />
        <span>Log Out</span>
      </button>
    </aside>
  );
}

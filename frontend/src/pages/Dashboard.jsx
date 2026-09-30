import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { 
  BookOpen, 
  CheckCircle2, 
  Clock, 
  Flame, 
  Sparkles, 
  Target, 
  TrendingUp, 
  PlayCircle, 
  AlertTriangle, 
  ArrowRight, 
  RefreshCw, 
  FileText,
  Compass,
  Lock,
  Unlock,
  Check,
  Zap,
  ChevronDown,
  ChevronUp,
  Layers,
  HelpCircle,
  BarChart2,
  AlertCircle,
  Code2
} from 'lucide-react';
import { api } from '../api';

export default function Dashboard() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [skillFilter, setSkillFilter] = useState('all');
  const [updatingDsaLang, setUpdatingDsaLang] = useState(false);
  const [dsaNotification, setDsaNotification] = useState(null);
  const [showDsaLangModal, setShowDsaLangModal] = useState(false);
  const [modalSelectedLang, setModalSelectedLang] = useState('cpp');
  const [expandedMilestone, setExpandedMilestone] = useState(null);

  // TanStack Query for instant, cached dashboard data (<0ms on navigation)
  const { 
    data: summary, 
    isLoading: loading, 
    error: queryError 
  } = useQuery({
    queryKey: ['dashboardSummary'],
    queryFn: api.getDashboardSummary,
    staleTime: 5 * 60 * 1000,
  });

  const { 
    data: insightsData, 
    isLoading: insightsLoading 
  } = useQuery({
    queryKey: ['dashboardInsights'],
    queryFn: api.getDashboardInsights,
    staleTime: 10 * 60 * 1000,
  });

  const overview = summary?.overview || null;
  const profile = summary?.profile || null;
  const skillsData = summary?.skills || { skills: [], categorized: {}, summary: {} };
  const recommendations = summary?.recommendations || [];
  const roadmap = summary?.roadmap || null;
  const quizAnalysis = summary?.quiz_analysis || null;
  const timeline = summary?.timeline || [];
  const dsaInfo = summary?.dsa_info || null;
  const insights = insightsData?.insights || [];
  const error = queryError?.message || null;

  useEffect(() => {
    if (dsaInfo) {
      if (dsaInfo.dsa_lang_code) {
        setModalSelectedLang(dsaInfo.dsa_lang_code);
      }
      if (dsaInfo.is_target_role && dsaInfo.has_selected_language === false) {
        setShowDsaLangModal(true);
      }
    }
  }, [dsaInfo]);

  const handleUpdateDsaLanguage = async (newLang) => {
    const cur = (dsaInfo?.dsa_language || dsaInfo?.dsaLanguage || '').toLowerCase();
    const target = newLang.toLowerCase();
    if (updatingDsaLang || cur === target || (target === 'c++' && cur === 'cpp') || (target === 'cpp' && cur === 'c++')) return;
    setUpdatingDsaLang(true);
    setDsaNotification(`Switching DSA track to ${newLang}...`);
    try {
      await api.updateDsaLanguage(newLang);
      setDsaNotification(`DSA track updated to ${newLang}!`);
      queryClient.invalidateQueries({ queryKey: ['dashboardSummary'] });
      queryClient.invalidateQueries({ queryKey: ['learningResume'] });
    } catch (err) {
      console.error('Failed to update DSA language:', err);
      setDsaNotification('Failed to update DSA language.');
    } finally {
      setUpdatingDsaLang(false);
      setTimeout(() => setDsaNotification(null), 3500);
    }
  };

  const handleNavigateTopic = (topic, module = "intro") => {
    navigate(`/learning/${encodeURIComponent(topic)}?module=${encodeURIComponent(module)}`);
  };

  if (loading && !summary) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', gap: '16px' }}>
        <RefreshCw size={36} color="#818cf8" style={{ animation: 'spin 1s linear infinite' }} />
        <p style={{ color: 'var(--text-muted)' }}>Loading your personalized learning dashboard...</p>
      </div>
    );
  }

  const continueCourse = overview?.continue_course;
  const roleReadiness = overview?.role_readiness_pct ?? skillsData?.summary?.role_readiness_pct ?? 0;
  const displayLearningTime = overview?.learning_time_formatted || overview?.learning_time || overview?.overall_learning_time || overview?.overall_progress || (
    overview?.total_learning_hours 
      ? `${Math.floor(overview.total_learning_hours)}h ${Math.round((overview.total_learning_hours % 1) * 60).toString().padStart(2, '0')}m`
      : '0h 00m'
  );
  const topicsMastered = overview?.topics_mastered ?? overview?.completed_modules ?? overview?.topics_completed ?? 0;
  const currentStreak = overview?.current_streak || 0;
  const categorized = skillsData.categorized || {};
  const allSkillsList = skillsData.skills || [];

  const filteredSkills = skillFilter === 'all' 
    ? allSkillsList 
    : (categorized[skillFilter] || []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem', maxWidth: '1200px', margin: '0 auto', paddingBottom: '3rem' }}>
      
      {/* ── Top Header ── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px', flexWrap: 'wrap' }}>
            <h1 style={{ fontSize: '2.2rem', margin: 0 }}>Learning Journey Dashboard</h1>
            <span className="badge badge-indigo" style={{ padding: '4px 12px', fontSize: '0.85rem' }}>
              <Target size={14} style={{ marginRight: '4px' }} />
              {overview?.target_role || 'DevOps Engineer'}
            </span>
            <span className="badge badge-purple" style={{ padding: '4px 12px', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '5px' }}>
              <Award size={14} />
              Research Cohort: {overview?.initial_performance_category || profile?.initial_performance_category || 'Pending First Quiz'}
            </span>
            <span className="badge badge-emerald" style={{ padding: '4px 12px', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '5px' }}>
              <Sparkles size={14} />
              Adaptive Ability (θ): {overview?.current_ability !== undefined ? overview.current_ability : profile?.current_ability !== undefined ? profile.current_ability : 0.5}
            </span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', margin: 0 }}>
            Real-time evidence-based skill analysis, adaptive course continuation, and role readiness.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button onClick={() => navigate('/learning')} className="btn-secondary">
            <BookOpen size={16} />
            <span>Learning Center</span>
          </button>
          <button onClick={() => navigate('/resume')} className="btn-secondary">
            <FileText size={16} />
            <span>Manage Resume</span>
          </button>
          <button onClick={() => navigate('/skill-gap')} className="btn-primary">
            <Target size={16} />
            <span>View Skill Gap</span>
          </button>
        </div>
      </div>

      {error && (
        <div style={{
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          padding: '1rem',
          borderRadius: '12px',
          color: '#fca5a5',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <AlertTriangle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* ── DSA TARGET ROLE & LANGUAGE PROGRESS CARD ── */}
      {dsaInfo && dsaInfo.is_target_role && (
        <div 
          className="glass-card"
          style={{
            background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.75) 0%, rgba(99, 102, 241, 0.12) 50%, rgba(168, 85, 247, 0.1) 100%)',
            border: '1px solid rgba(99, 102, 241, 0.38)',
            borderRadius: '18px',
            padding: '1.5rem 1.75rem',
            position: 'relative',
            boxShadow: '0 8px 30px rgba(0, 0, 0, 0.25)'
          }}
        >
          {dsaNotification && (
            <div style={{
              position: 'absolute',
              top: '12px',
              right: '20px',
              backgroundColor: 'rgba(16, 185, 129, 0.95)',
              color: '#fff',
              padding: '4px 12px',
              borderRadius: '20px',
              fontSize: '0.8rem',
              fontWeight: '600',
              boxShadow: '0 2px 10px rgba(0,0,0,0.3)',
              zIndex: 10
            }}>
              {dsaNotification}
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.1rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                <span className="badge badge-indigo" style={{ padding: '3px 10px', fontSize: '0.78rem', fontWeight: '700' }}>
                  <Code2 size={13} style={{ marginRight: '4px' }} />
                  TARGET ROLE: DATA STRUCTURES & ALGORITHMS (DSA)
                </span>
                <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  Selected Track: <strong style={{ color: '#818cf8' }}>{dsaInfo.dsa_language}</strong>
                </span>
              </div>
              <h2 style={{ fontSize: '1.35rem', color: '#fff', margin: 0 }}>
                Algorithmic Problem Solving in {dsaInfo.dsa_language}
              </h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', margin: '4px 0 0' }}>
                Master linear data structures, trees, graphs, and dynamic programming with questions and curated video lessons tailored for {dsaInfo.dsa_language}.
              </p>
            </div>

            {/* Interactive Language Switcher */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '6px' }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Switch Track Language:
              </span>
              <div style={{ display: 'flex', gap: '6px', backgroundColor: 'rgba(0, 0, 0, 0.35)', padding: '4px', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
                {['C', 'C++', 'Python', 'Java'].map((lang) => {
                  const cur = (dsaInfo?.dsa_language || dsaInfo?.dsaLanguage || 'C++').toLowerCase();
                  const isActive = cur === lang.toLowerCase() ||
                    (lang === 'C++' && (cur === 'cpp' || cur === 'c++')) ||
                    (lang === 'C' && cur === 'c');
                  return (
                    <button
                      key={lang}
                      onClick={() => handleUpdateDsaLanguage(lang)}
                      disabled={updatingDsaLang}
                      style={{
                        padding: '6px 14px',
                        borderRadius: '7px',
                        fontSize: '0.82rem',
                        fontWeight: isActive ? '700' : '500',
                        backgroundColor: isActive ? 'rgba(99, 102, 241, 0.9)' : 'transparent',
                        color: isActive ? '#fff' : 'var(--text-muted)',
                        border: 'none',
                        cursor: updatingDsaLang ? 'not-allowed' : 'pointer',
                        transition: 'all 0.15s ease',
                        boxShadow: isActive ? '0 2px 8px rgba(99, 102, 241, 0.5)' : 'none'
                      }}
                    >
                      {lang}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '1rem',
            alignItems: 'center',
            backgroundColor: 'rgba(255, 255, 255, 0.02)',
            border: '1px solid rgba(255, 255, 255, 0.05)',
            borderRadius: '12px',
            padding: '1rem 1.25rem'
          }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '6px' }}>
                <span style={{ color: 'var(--text-dim)' }}>Curriculum Progress:</span>
                <span style={{ fontWeight: '700', color: dsaInfo.dsa_progress_pct === 100 ? '#10b981' : '#818cf8' }}>
                  {dsaInfo.dsa_progress_pct}% ({dsaInfo.completed_modules_count} / {dsaInfo.total_modules_count} Modules)
                </span>
              </div>
              <div className="progress-track" style={{ height: '6px' }}>
                <div 
                  className={`progress-fill ${dsaInfo.dsa_progress_pct === 100 ? 'progress-fill-emerald' : ''}`}
                  style={{ width: `${dsaInfo.dsa_progress_pct}%` }} 
                />
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-dim)', marginBottom: '4px' }}>
                Active Module:
              </div>
              <span className="badge badge-indigo" style={{ fontSize: '0.8rem', padding: '3px 10px' }}>
                {dsaInfo.current_dsa_module_title || dsaInfo.current_dsa_module?.toUpperCase() || 'MODULE 1'}
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button
                onClick={() => navigate(dsaInfo.navigate_url || '/learning/Data%20Structures%20%26%20Algorithms')}
                className="btn-primary"
                style={{ padding: '8px 16px', fontSize: '0.88rem', whiteSpace: 'nowrap' }}
              >
                <PlayCircle size={16} />
                <span>Open DSA Curriculum</span>
                <ArrowRight size={14} />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── PRIORITY 1: CURRENT ACTIVE COURSE CONTINUATION ── */}
      {continueCourse && (
        <div 
          className="glass-card"
          style={{
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.12) 50%, rgba(16, 185, 129, 0.08) 100%)',
            border: '1px solid rgba(99, 102, 241, 0.45)',
            borderRadius: '20px',
            padding: '1.75rem 2rem',
            boxShadow: '0 8px 32px rgba(99, 102, 241, 0.18)'
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span className="badge badge-indigo" style={{ padding: '6px 14px', fontSize: '0.82rem', fontWeight: '700' }}>
                <PlayCircle size={14} style={{ marginRight: '6px' }} />
                ACTIVE COURSE CONTINUATION
              </span>
              <span style={{ fontSize: '0.84rem', color: 'var(--text-muted)' }}>
                {continueCourse.last_accessed_at ? `Last active: ${new Date(continueCourse.last_accessed_at).toLocaleDateString()}` : 'In Progress'}
              </span>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Topic Progress:</span>
              <span style={{ fontSize: '1.1rem', fontWeight: '700', color: '#818cf8' }}>
                {continueCourse.progress_pct || 0}%
              </span>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '2rem', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: '0.82rem', color: '#a5b4fc', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: '700', marginBottom: '4px' }}>
                Continue Learning
              </div>
              <h2 style={{ fontSize: '1.6rem', marginBottom: '6px', color: '#fff' }}>
                Course: {continueCourse.topic}
              </h2>
              <p style={{ color: '#c7d2fe', fontSize: '0.95rem', marginBottom: '12px' }}>
                📺 Video: {continueCourse.video_title}
              </p>

              <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap', alignItems: 'center', marginBottom: '1rem' }}>
                <span style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  backgroundColor: 'rgba(255, 255, 255, 0.08)',
                  padding: '4px 12px',
                  borderRadius: '20px',
                  fontSize: '0.82rem',
                  color: '#e2e8f0'
                }}>
                  <Clock size={14} color="#818cf8" />
                  <span>Resume Video: <strong>{continueCourse.formatted_position || '00:00'}</strong></span>
                </span>

                <span style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  backgroundColor: 'rgba(255, 255, 255, 0.08)',
                  padding: '4px 12px',
                  borderRadius: '20px',
                  fontSize: '0.82rem',
                  color: '#e2e8f0'
                }}>
                  <Layers size={14} color="#a855f7" />
                  <span>Module: <strong>{continueCourse.module.toUpperCase()}</strong></span>
                </span>

                <span style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  backgroundColor: 'rgba(255, 255, 255, 0.08)',
                  padding: '4px 12px',
                  borderRadius: '20px',
                  fontSize: '0.82rem',
                  color: '#e2e8f0'
                }}>
                  <CheckCircle2 size={14} color="#34d399" />
                  <span>Progress: <strong>{continueCourse.progress_pct || 0}%</strong></span>
                </span>
              </div>

              {/* Progress bar */}
              <div className="progress-track" style={{ height: '7px', maxWidth: '420px' }}>
                <div 
                  className="progress-fill" 
                  style={{ width: `${continueCourse.progress_pct || 0}%` }} 
                />
              </div>
            </div>

            <div>
              <button
                onClick={() => navigate(continueCourse.navigate_url)}
                className="btn-primary"
                style={{
                  padding: '14px 28px',
                  fontSize: '1rem',
                  fontWeight: '700',
                  boxShadow: '0 4px 20px rgba(99, 102, 241, 0.4)',
                  whiteSpace: 'nowrap'
                }}
              >
                <PlayCircle size={18} />
                <span>Continue Learning</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Summary Metrics Grid & Role Readiness Meter ── */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))',
        gap: '1.25rem'
      }}>
        {/* Role Readiness */}
        <div className="glass-card" style={{ padding: '1.25rem', textAlign: 'center', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
          <div style={{ color: '#10b981', marginBottom: '8px' }}><Target size={26} style={{ margin: '0 auto' }} /></div>
          <div style={{ fontSize: '2rem', fontWeight: '800', color: '#34d399' }}>{roleReadiness}%</div>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Role Readiness</div>
        </div>

        {/* Overall Curriculum Progress */}
        <div className="glass-card" style={{ padding: '1.25rem', textAlign: 'center' }}>
          <div style={{ color: '#818cf8', marginBottom: '8px' }}><TrendingUp size={26} style={{ margin: '0 auto' }} /></div>
          <div style={{ fontSize: '2rem', fontWeight: '800', color: '#fff' }}>{overview?.overall_progress ?? 0}%</div>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Overall Progress</div>
        </div>

        {/* Topics Mastered */}
        <div className="glass-card" style={{ padding: '1.25rem', textAlign: 'center' }}>
          <div style={{ color: '#34d399', marginBottom: '8px' }}><CheckCircle2 size={26} style={{ margin: '0 auto' }} /></div>
          <div style={{ fontSize: '2rem', fontWeight: '800', color: '#fff' }}>{topicsMastered}</div>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Topics Mastered</div>
        </div>

        {/* Learning Time */}
        <div className="glass-card" style={{ padding: '1.25rem', textAlign: 'center' }}>
          <div style={{ color: '#a78bfa', marginBottom: '8px' }}><Clock size={26} style={{ margin: '0 auto' }} /></div>
          <div style={{ fontSize: '2rem', fontWeight: '800', color: '#fff' }}>{displayLearningTime}</div>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Learning Time</div>
        </div>

        {/* Learning Streak */}
        <div className="glass-card" style={{ padding: '1.25rem', textAlign: 'center' }}>
          <div style={{ color: '#f59e0b', marginBottom: '8px' }}><Flame size={26} style={{ margin: '0 auto' }} /></div>
          <div style={{ fontSize: '2rem', fontWeight: '800', color: '#fff' }}>{currentStreak} <span style={{ fontSize: '1rem' }}>days</span></div>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Streak</div>
        </div>
      </div>

      {/* ── RL-POWERED PERSONALIZED RECOMMENDATIONS (DUELING DOUBLE DQN) ── */}
      {recommendations && recommendations.length > 0 && (
        <div className="glass-card" style={{ padding: '1.75rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                <span className="badge badge-purple" style={{ padding: '3px 10px', fontSize: '0.75rem', fontWeight: '700' }}>
                  <Zap size={13} style={{ marginRight: '4px' }} />
                  DUELING DOUBLE DQN + PER RECOMMENDATIONS
                </span>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                  Single Source of Truth (Synchronized with Learning Centre)
                </span>
              </div>
              <h2 style={{ fontSize: '1.35rem', color: '#fff', margin: 0 }}>
                Next Recommended Learning Milestones
              </h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', margin: '4px 0 0' }}>
                RL policy recommendations optimized for prerequisite sequences, active progress momentum, and career requirements.
              </p>
            </div>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
            gap: '1.25rem'
          }}>
            {recommendations.map((rec, rIdx) => {
              const isHigh = rec.priority === 'high';
              return (
                <div
                  key={rIdx}
                  className="glass-card"
                  style={{
                    padding: '1.25rem',
                    borderRadius: '14px',
                    border: isHigh ? '1px solid rgba(168, 85, 247, 0.45)' : '1px solid var(--border-color)',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    gap: '12px',
                    background: isHigh ? 'linear-gradient(135deg, rgba(168, 85, 247, 0.08) 0%, rgba(99, 102, 241, 0.04) 100%)' : 'rgba(255, 255, 255, 0.02)'
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <span className={`badge ${isHigh ? 'badge-purple' : 'badge-indigo'}`} style={{ fontSize: '0.72rem' }}>
                        {isHigh ? '★ Top Priority' : 'Recommended'}
                      </span>
                      <span className="badge badge-gray" style={{ fontSize: '0.72rem', textTransform: 'capitalize' }}>
                        {rec.difficulty || 'Intermediate'}
                      </span>
                    </div>

                    <h3 style={{ fontSize: '1.15rem', marginBottom: '6px', color: '#fff' }}>
                      {rec.title || rec.topic}
                    </h3>

                    <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)', margin: '0 0 10px', lineHeight: '1.4' }}>
                      {rec.description}
                    </p>

                    {rec.progress_pct !== undefined && rec.progress_pct > 0 && (
                      <div style={{ marginBottom: '8px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.76rem', color: 'var(--text-dim)', marginBottom: '4px' }}>
                          <span>Current Progress</span>
                          <span>{rec.progress_pct}%</span>
                        </div>
                        <div className="progress-track" style={{ height: '4px' }}>
                          <div className="progress-fill" style={{ width: `${rec.progress_pct}%` }} />
                        </div>
                      </div>
                    )}
                  </div>

                  <button
                    onClick={() => rec.navigate_url ? navigate(rec.navigate_url) : handleNavigateTopic(rec.topic, rec.target_module || 'intro')}
                    className={isHigh ? 'btn-primary' : 'btn-secondary'}
                    style={{ width: '100%', padding: '8px 14px', fontSize: '0.85rem', justifyContent: 'center' }}
                  >
                    <PlayCircle size={15} />
                    <span>{rec.action_label || 'Start Learning'}</span>
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ── EVIDENCE-BASED SKILL ANALYSIS ── */}
      <div className="glass-card" style={{ padding: '1.75rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.4rem', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <BarChart2 size={20} color="#818cf8" />
              <span>Evidence-Based Skill Analysis</span>
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
              Categorized by resume verification, quiz scores, and target role requirements.
            </p>
          </div>

          {/* Filter Pills */}
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <button
              onClick={() => setSkillFilter('all')}
              className={skillFilter === 'all' ? 'btn-primary' : 'btn-secondary'}
              style={{ padding: '6px 14px', fontSize: '0.82rem' }}
            >
              All ({allSkillsList.length})
            </button>
            <button
              onClick={() => setSkillFilter('known')}
              className={skillFilter === 'known' ? 'btn-emerald' : 'btn-secondary'}
              style={{ padding: '6px 14px', fontSize: '0.82rem' }}
            >
              Known ({categorized.known?.length || 0})
            </button>
            <button
              onClick={() => setSkillFilter('learning')}
              className={skillFilter === 'learning' ? 'btn-primary' : 'btn-secondary'}
              style={{ padding: '6px 14px', fontSize: '0.82rem' }}
            >
              Learning ({categorized.learning?.length || 0})
            </button>
            <button
              onClick={() => setSkillFilter('needs_improvement')}
              className={skillFilter === 'needs_improvement' ? 'btn-secondary' : 'btn-secondary'}
              style={{
                padding: '6px 14px',
                fontSize: '0.82rem',
                borderColor: skillFilter === 'needs_improvement' ? '#f59e0b' : 'var(--border-color)',
                color: skillFilter === 'needs_improvement' ? '#f59e0b' : 'var(--text-main)'
              }}
            >
              Needs Review ({categorized.needs_improvement?.length || 0})
            </button>
            <button
              onClick={() => setSkillFilter('missing')}
              className={skillFilter === 'missing' ? 'btn-secondary' : 'btn-secondary'}
              style={{
                padding: '6px 14px',
                fontSize: '0.82rem',
                borderColor: skillFilter === 'missing' ? '#f43f5e' : 'var(--border-color)',
                color: skillFilter === 'missing' ? '#f43f5e' : 'var(--text-main)'
              }}
            >
              Missing ({categorized.missing?.length || 0})
            </button>
          </div>
        </div>

        {/* Skills Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
          gap: '1.25rem'
        }}>
          {filteredSkills.map((sk) => {
            const isKnown = sk.category === 'Known';
            const isLearning = sk.category === 'Learning';
            const isNeedsReview = sk.category === 'Needs Improvement';

            return (
              <div
                key={sk.topic}
                className="glass-card"
                style={{
                  padding: '1.25rem',
                  borderRadius: '14px',
                  border: isKnown 
                    ? '1px solid rgba(16, 185, 129, 0.3)' 
                    : isLearning 
                    ? '1px solid rgba(99, 102, 241, 0.4)' 
                    : isNeedsReview
                    ? '1px solid rgba(245, 158, 11, 0.4)'
                    : '1px solid var(--border-color)',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '12px'
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span className={`badge ${
                      isKnown ? 'badge-emerald' : 
                      isLearning ? 'badge-indigo' : 
                      isNeedsReview ? 'badge-amber' : 
                      'badge-gray'
                    }`} style={{ fontSize: '0.74rem' }}>
                      {sk.category}
                    </span>
                    <span className={`badge ${sk.level === 'Advanced' ? 'badge-emerald' : sk.level === 'Intermediate' ? 'badge-indigo' : 'badge-amber'}`} style={{ fontSize: '0.72rem' }}>
                      {sk.level}
                    </span>
                  </div>

                  <h3 style={{ fontSize: '1.15rem', marginBottom: '4px', color: '#fff' }}>
                    {sk.topic}
                  </h3>

                  {/* Evidence Source Badge */}
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    fontSize: '0.78rem',
                    color: isNeedsReview ? '#fcd34d' : isKnown ? '#6ee7b7' : '#c7d2fe',
                    backgroundColor: isNeedsReview ? 'rgba(245, 158, 11, 0.1)' : isKnown ? 'rgba(16, 185, 129, 0.1)' : 'rgba(99, 102, 241, 0.08)',
                    padding: '4px 10px',
                    borderRadius: '8px',
                    marginBottom: '10px'
                  }}>
                    <span><strong>Evidence:</strong> {sk.evidence}</span>
                  </div>

                  {/* Progress info */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-dim)', marginBottom: '4px' }}>
                    <span>{sk.completed_modules} / {sk.total_modules} Modules</span>
                    {sk.quizzes_taken > 0 && <span>Avg Quiz: {sk.avg_quiz_score}%</span>}
                  </div>

                  <div className="progress-track" style={{ height: '5px' }}>
                    <div 
                      className={`progress-fill ${isKnown ? 'progress-fill-emerald' : ''}`} 
                      style={{ width: `${sk.progress_pct}%` }} 
                    />
                  </div>
                </div>

                <button
                  onClick={() => handleNavigateTopic(sk.topic)}
                  className={isKnown ? 'btn-secondary' : 'btn-primary'}
                  style={{ width: '100%', padding: '8px 14px', fontSize: '0.85rem', justifyContent: 'center' }}
                >
                  <PlayCircle size={15} />
                  <span>{isKnown ? 'Review Content' : isLearning ? 'Continue Learning' : 'Start Skill'}</span>
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── QUIZ PERFORMANCE ANALYSIS SECTION ── */}
      <div className="glass-card" style={{ padding: '1.75rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.4rem', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <Award size={20} color="#f59e0b" />
              <span>Quiz Performance Analysis</span>
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
              15-question adaptive quizzes taken with 30s timers and immediate scoring.
            </p>
          </div>
          {quizAnalysis?.has_quiz_data && (
            <span className="badge badge-emerald" style={{ padding: '4px 12px', fontSize: '0.82rem' }}>
              {quizAnalysis.total_quizzes_taken} Quizzes Completed
            </span>
          )}
        </div>

        {quizAnalysis?.has_quiz_data ? (
          <div>
            {/* Top Quiz Stats */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
              <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', padding: '1rem', borderRadius: '12px', border: '1px solid var(--border-color)', textAlign: 'center' }}>
                <div style={{ fontSize: '1.8rem', fontWeight: '800', color: '#818cf8' }}>{quizAnalysis.average_quiz_score}%</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Average Score</div>
              </div>
              <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', padding: '1rem', borderRadius: '12px', border: '1px solid var(--border-color)', textAlign: 'center' }}>
                <div style={{ fontSize: '1.8rem', fontWeight: '800', color: '#34d399' }}>{quizAnalysis.highest_score}%</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Highest Score</div>
              </div>
              <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', padding: '1rem', borderRadius: '12px', border: '1px solid var(--border-color)', textAlign: 'center' }}>
                <div style={{ fontSize: '1.8rem', fontWeight: '800', color: '#f59e0b' }}>{quizAnalysis.lowest_score}%</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Lowest Score</div>
              </div>
            </div>

            {/* Strengths and Improvement Areas */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
              {/* Strengths */}
              <div style={{ backgroundColor: 'rgba(16, 185, 129, 0.04)', border: '1px solid rgba(16, 185, 129, 0.25)', padding: '1rem', borderRadius: '12px' }}>
                <div style={{ fontWeight: '700', fontSize: '0.95rem', color: '#34d399', marginBottom: '8px' }}>
                  ✓ Core Strengths (≥75%)
                </div>
                {quizAnalysis.strengths?.length > 0 ? (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {quizAnalysis.strengths.map((s, idx) => (
                      <span key={idx} className="badge badge-emerald" style={{ fontSize: '0.8rem' }}>
                        {s.topic} ({s.score}%)
                      </span>
                    ))}
                  </div>
                ) : (
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: 0 }}>
                    Keep practicing to establish high-score mastery benchmarks.
                  </p>
                )}
              </div>

              {/* Needs Review */}
              <div style={{ backgroundColor: 'rgba(245, 158, 11, 0.04)', border: '1px solid rgba(245, 158, 11, 0.25)', padding: '1rem', borderRadius: '12px' }}>
                <div style={{ fontWeight: '700', fontSize: '0.95rem', color: '#fcd34d', marginBottom: '8px' }}>
                  ⚠️ Areas to Review (&lt;60%)
                </div>
                {quizAnalysis.weaknesses?.length > 0 ? (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {quizAnalysis.weaknesses.map((w, idx) => (
                      <span key={idx} className="badge badge-amber" style={{ fontSize: '0.8rem' }}>
                        {w.topic} ({w.score}%)
                      </span>
                    ))}
                  </div>
                ) : (
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: 0 }}>
                    No weak topics identified! All attempted quizzes meet passing standards.
                  </p>
                )}
              </div>
            </div>

            {/* Per-Topic Breakdown Table */}
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left' }}>
                    <th style={{ padding: '10px', color: 'var(--text-dim)' }}>Topic</th>
                    <th style={{ padding: '10px', color: 'var(--text-dim)' }}>Attempts</th>
                    <th style={{ padding: '10px', color: 'var(--text-dim)' }}>Average Score</th>
                    <th style={{ padding: '10px', color: 'var(--text-dim)' }}>Latest Score</th>
                    <th style={{ padding: '10px', color: 'var(--text-dim)' }}>Status</th>
                    <th style={{ padding: '10px', color: 'var(--text-dim)' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {quizAnalysis.topic_analysis?.map((item) => (
                    <tr key={item.topic} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                      <td style={{ padding: '10px', fontWeight: '600' }}>{item.topic}</td>
                      <td style={{ padding: '10px', color: 'var(--text-dim)' }}>{item.attempts}</td>
                      <td style={{ padding: '10px', color: '#818cf8', fontWeight: '700' }}>{item.average_score}%</td>
                      <td style={{ padding: '10px' }}>{item.latest_score}%</td>
                      <td style={{ padding: '10px' }}>
                        <span className={`badge ${item.status === 'Strong' ? 'badge-emerald' : item.status === 'Good' ? 'badge-indigo' : 'badge-amber'}`} style={{ fontSize: '0.74rem' }}>
                          {item.status}
                        </span>
                      </td>
                      <td style={{ padding: '10px' }}>
                        <button
                          onClick={() => handleNavigateTopic(item.topic, item.latest_module || 'intro')}
                          className="btn-secondary"
                          style={{ padding: '4px 10px', fontSize: '0.78rem' }}
                        >
                          Review Topic
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '2.5rem 1rem', backgroundColor: 'rgba(255, 255, 255, 0.015)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
            <HelpCircle size={40} color="#818cf8" style={{ margin: '0 auto 12px', opacity: 0.7 }} />
            <h3 style={{ fontSize: '1.15rem', marginBottom: '6px', color: '#fff' }}>No Quizzes Taken Yet</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', maxWidth: '480px', margin: '0 auto 1.25rem' }}>
              Watch required lesson videos to unlock module quizzes. Each quiz includes 15 adaptive questions with a 30-second timer to test your knowledge!
            </p>
            <button
              onClick={() => navigate('/learning')}
              className="btn-primary"
              style={{ padding: '10px 20px', fontSize: '0.9rem' }}
            >
              <BookOpen size={16} />
              <span>Go to Learning Center</span>
            </button>
          </div>
        )}
      </div>

      {/* ── ROLE ROADMAP (PREREQUISITE ENGINE) ── */}
      {roadmap && roadmap.milestones?.length > 0 && (
        <div className="glass-card" style={{ padding: '1.75rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                <Compass size={20} color="#818cf8" />
                <h2 style={{ fontSize: '1.4rem' }}>{roadmap.target_role} Career Roadmap</h2>
                <span className="badge badge-indigo">{roadmap.category || 'Career Path'}</span>
              </div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '750px' }}>
                {roadmap.role_description || 'Sequential curriculum path with strict prerequisite enforcement and personalized resume gap analysis.'}
              </p>
            </div>

            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-dim)', marginBottom: '4px' }}>
                Milestone Progress
              </div>
              <div style={{ fontSize: '1.2rem', fontWeight: '800', color: '#818cf8' }}>
                {roadmap.mastered_count} / {roadmap.total_milestones} Mastered
              </div>
            </div>
          </div>

          <div style={{ marginBottom: '1.75rem' }}>
            <div className="progress-track" style={{ height: '8px' }}>
              <div 
                className="progress-fill progress-fill-emerald" 
                style={{ width: `${Math.round((roadmap.mastered_count / Math.max(roadmap.total_milestones, 1)) * 100)}%` }} 
              />
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {roadmap.milestones.map((m, idx) => {
              const isExpanded = expandedMilestone === m.topic;
              const isMastered = m.status === 'mastered_via_resume';
              const isCompleted = m.status === 'completed';
              const isLocked = m.status === 'locked';
              const isReady = m.status === 'ready_to_learn';

              return (
                <div
                  key={idx}
                  style={{
                    backgroundColor: isMastered 
                      ? 'rgba(16, 185, 129, 0.04)' 
                      : isCompleted 
                      ? 'rgba(16, 185, 129, 0.08)' 
                      : isLocked 
                      ? 'rgba(255, 255, 255, 0.015)' 
                      : 'rgba(99, 102, 241, 0.05)',
                    border: isMastered 
                      ? '1px solid rgba(16, 185, 129, 0.25)' 
                      : isCompleted 
                      ? '1px solid rgba(16, 185, 129, 0.4)' 
                      : isLocked 
                      ? '1px solid var(--border-color)' 
                      : '1px solid rgba(99, 102, 241, 0.35)',
                    borderRadius: '12px',
                    padding: '1.15rem 1.25rem',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1, minWidth: '280px' }}>
                      <div style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        backgroundColor: (isMastered || isCompleted)
                          ? 'rgba(16, 185, 129, 0.2)'
                          : isLocked
                          ? 'rgba(255, 255, 255, 0.05)'
                          : 'rgba(99, 102, 241, 0.2)',
                        color: (isMastered || isCompleted)
                          ? '#34d399'
                          : isLocked
                          ? '#9ca3af'
                          : '#818cf8',
                        fontWeight: '700',
                        fontSize: '0.9rem',
                        flexShrink: 0
                      }}>
                        {isCompleted ? <CheckCircle2 size={18} /> : isMastered ? <Check size={18} /> : isLocked ? <Lock size={16} /> : idx + 1}
                      </div>

                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', marginBottom: '2px' }}>
                          <span style={{ fontWeight: '700', fontSize: '1.05rem', color: '#fff' }}>
                            {m.title}
                          </span>

                          {isMastered && (
                            <span className="badge badge-emerald" style={{ padding: '2px 8px', fontSize: '0.74rem' }}>
                              ✓ Mastered from Resume
                            </span>
                          )}
                          {isCompleted && (
                            <span className="badge badge-emerald" style={{ padding: '2px 8px', fontSize: '0.74rem' }}>
                              ★ Topic Completed
                            </span>
                          )}
                          {isReady && (
                            <span className="badge badge-indigo" style={{ padding: '2px 8px', fontSize: '0.74rem' }}>
                              ⚡ Next Up (Ready)
                            </span>
                          )}
                          {isLocked && (
                            <span className="badge badge-amber" style={{ padding: '2px 8px', fontSize: '0.74rem' }}>
                              🔒 Missing Prerequisite: {m.unmet_prerequisites?.join(', ')}
                            </span>
                          )}
                        </div>

                        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
                          {m.description}
                        </p>

                        {m.prerequisites?.length > 0 && (
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '6px', fontSize: '0.78rem' }}>
                            <span style={{ color: 'var(--text-dim)' }}>Prerequisites:</span>
                            {m.prerequisites.map((p, pIdx) => {
                              const isUnmet = m.unmet_prerequisites?.includes(p);
                              return (
                                <span
                                  key={pIdx}
                                  style={{
                                    padding: '1px 7px',
                                    borderRadius: '12px',
                                    fontSize: '0.72rem',
                                    backgroundColor: isUnmet ? 'rgba(245, 158, 11, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                                    color: isUnmet ? '#fcd34d' : '#6ee7b7',
                                    border: `1px solid ${isUnmet ? 'rgba(245, 158, 11, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`
                                  }}
                                >
                                  {isUnmet ? `⚠ ${p}` : `✓ ${p}`}
                                </span>
                              );
                            })}
                          </div>
                        )}
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {m.syllabus && (
                        <button
                          onClick={() => setExpandedMilestone(isExpanded ? null : m.topic)}
                          className="btn-secondary"
                          style={{ padding: '7px 12px', fontSize: '0.8rem' }}
                        >
                          <Layers size={14} />
                          <span>4-Module Syllabus</span>
                          {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                        </button>
                      )}

                      {isLocked ? (
                        <button
                          onClick={() => handleNavigateTopic(m.unmet_prerequisites?.[0] || m.topic)}
                          className="btn-secondary"
                          style={{ padding: '8px 16px', fontSize: '0.86rem', color: '#fcd34d', borderColor: 'rgba(245, 158, 11, 0.3)' }}
                        >
                          <Unlock size={14} />
                          <span>Learn {m.unmet_prerequisites?.[0] || 'Prerequisite'} First</span>
                        </button>
                      ) : (
                        <button
                          onClick={() => handleNavigateTopic(m.topic)}
                          className={isReady ? 'btn-primary' : 'btn-secondary'}
                          style={{ padding: '8px 18px', fontSize: '0.86rem' }}
                        >
                          <PlayCircle size={15} />
                          <span>{m.action_label}</span>
                        </button>
                      )}
                    </div>
                  </div>

                  {isExpanded && m.syllabus && (
                    <div style={{
                      marginTop: '1rem',
                      paddingTop: '1rem',
                      borderTop: '1px solid var(--border-color)',
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                      gap: '12px'
                    }}>
                      {['intro', 'core', 'advanced', 'summary'].map((modKey) => {
                        const mod = m.syllabus.modules?.[modKey];
                        if (!mod) return null;
                        return (
                          <div
                            key={modKey}
                            style={{
                              backgroundColor: 'rgba(0, 0, 0, 0.25)',
                              border: '1px solid rgba(255, 255, 255, 0.06)',
                              borderRadius: '8px',
                              padding: '10px 12px'
                            }}
                          >
                            <div style={{ fontSize: '0.84rem', fontWeight: '700', color: '#818cf8', marginBottom: '4px' }}>
                              {mod.title}
                            </div>
                            <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginBottom: '6px' }}>
                              {mod.focus}
                            </div>
                            <ul style={{ margin: 0, paddingLeft: '14px', fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                              {mod.subtopics?.map((st, sIdx) => (
                                <li key={sIdx} style={{ marginBottom: '2px' }}>{st}</li>
                              ))}
                            </ul>
                            <button
                              onClick={() => handleNavigateTopic(m.topic, modKey)}
                              className="btn-secondary"
                              style={{ width: '100%', marginTop: '8px', padding: '4px 8px', fontSize: '0.74rem', justifyContent: 'center' }}
                            >
                              Jump to Module
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ── TWO COLUMN: AI ADVISORY & RECENT ACTIVITIES ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem' }}>
        {/* Groq AI Learning Insights */}
        <div className="glass-card" style={{ padding: '1.75rem', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '1.25rem' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Sparkles size={18} color="#fff" />
            </div>
            <div>
              <h2 style={{ fontSize: '1.25rem' }}>Groq AI Learning Advisory</h2>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>Evidence-backed personalized guidance</span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', flex: 1 }}>
            {insightsLoading ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', padding: '0.5rem 0' }}>
                {[1, 2, 3].map((n) => (
                  <div
                    key={n}
                    style={{
                      height: '52px',
                      borderRadius: '10px',
                      backgroundColor: 'rgba(255, 255, 255, 0.03)',
                      border: '1px solid rgba(255, 255, 255, 0.05)',
                      animation: 'pulse 1.5s infinite ease-in-out'
                    }}
                  />
                ))}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', color: 'var(--text-dim)', fontSize: '0.8rem', marginTop: '6px' }}>
                  <RefreshCw size={13} style={{ animation: 'spin 1s linear infinite' }} />
                  <span>Synthesizing Groq AI Advisory...</span>
                </div>
              </div>
            ) : insights.length > 0 ? (
              insights.map((ins, idx) => (
                <div
                  key={idx}
                  style={{
                    backgroundColor: 'rgba(99, 102, 241, 0.05)',
                    border: '1px solid rgba(99, 102, 241, 0.15)',
                    borderRadius: '10px',
                    padding: '12px 14px',
                    fontSize: '0.88rem',
                    lineHeight: '1.45',
                    color: '#e0e7ff',
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '10px'
                  }}
                >
                  <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#818cf8', marginTop: '6px', flexShrink: 0 }} />
                  <span>{ins}</span>
                </div>
              ))
            ) : (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', margin: 'auto', textAlign: 'center' }}>
                Complete lessons and quizzes to generate personalized AI advisory recommendations.
              </p>
            )}
          </div>
        </div>

        {/* Recent Learning Activities */}
        <div className="glass-card" style={{ padding: '1.75rem', display: 'flex', flexDirection: 'column' }}>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '1.25rem' }}>Recent Learning Timeline</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', flex: 1 }}>
            {timeline.slice(0, 6).map((act, i) => (
              <div
                key={i}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '10px 14px',
                  backgroundColor: 'rgba(255, 255, 255, 0.02)',
                  borderRadius: '8px',
                  border: '1px solid var(--border-color)',
                  fontSize: '0.88rem'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <CheckCircle2 size={16} color="#10b981" />
                  <span style={{ fontWeight: '500' }}>{act.title}</span>
                  {act.description && <span style={{ color: 'var(--text-dim)', fontSize: '0.82rem' }}>— {act.description}</span>}
                </div>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                  {new Date(act.created_at).toLocaleDateString()}
                </span>
              </div>
            ))}
            {timeline.length === 0 && (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', textAlign: 'center', margin: 'auto' }}>
                No recent activity logged yet. Start watching course lessons to build your timeline!
              </p>
            )}
          </div>
        </div>
      </div>

      {/* ── DSA Programming Language Selection Modal ── */}
      {showDsaLangModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 9999,
          padding: '1rem'
        }}>
          <div className="glass-card" style={{ maxWidth: '520px', width: '100%', padding: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <div style={{ width: '38px', height: '38px', borderRadius: '10px', backgroundColor: 'rgba(99, 102, 241, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Code2 size={22} color="#818cf8" />
              </div>
              <h2 style={{ fontSize: '1.4rem', margin: 0 }}>Select DSA Programming Language</h2>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem', lineHeight: '1.5' }}>
              SkillPath AI DSA exclusively supports four core industry languages. The shared DSA curriculum, algorithmic roadmaps, and RL recommendations remain unified, while your learning content, quizzes, and code syntax adapt strictly to your selected language.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '1.75rem' }}>
              {[
                { id: 'c', label: 'C', icon: '⚙️', desc: 'Pointers, manual memory allocation & procedural logic' },
                { id: 'cpp', label: 'C++', icon: '⚡', desc: 'C++ Standard Template Library (STL) & algorithms' },
                { id: 'python', label: 'Python', icon: '🐍', desc: 'Pythonic structures, lists & built-in collections' },
                { id: 'java', label: 'Java', icon: '☕', desc: 'Java Collections Framework (JCF) & OOP' }
              ].map((opt) => {
                const isSelected = modalSelectedLang === opt.id;
                return (
                  <div
                    key={opt.id}
                    onClick={() => setModalSelectedLang(opt.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      padding: '12px 16px',
                      borderRadius: '12px',
                      cursor: 'pointer',
                      border: isSelected ? '2px solid #818cf8' : '1px solid var(--border-color)',
                      backgroundColor: isSelected ? 'rgba(99, 102, 241, 0.15)' : 'rgba(255, 255, 255, 0.02)',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    <input
                      type="radio"
                      name="dsaLanguageSelection"
                      checked={isSelected}
                      onChange={() => setModalSelectedLang(opt.id)}
                      style={{ accentColor: '#818cf8', width: '16px', height: '16px' }}
                    />
                    <span style={{ fontSize: '1.25rem' }}>{opt.icon}</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: '700', fontSize: '0.95rem', color: isSelected ? '#fff' : '#cbd5e1' }}>
                        {opt.label}
                      </div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                        {opt.desc}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
              {dsaInfo?.has_selected_language && (
                <button
                  onClick={() => setShowDsaLangModal(false)}
                  className="btn-secondary"
                  style={{ padding: '10px 18px' }}
                >
                  Cancel
                </button>
              )}
              <button
                onClick={async () => {
                  await handleUpdateDsaLanguage(modalSelectedLang);
                  setShowDsaLangModal(false);
                }}
                disabled={updatingDsaLang}
                className="btn-primary"
                style={{ padding: '10px 22px', fontWeight: '700' }}
              >
                <span>{updatingDsaLang ? 'Saving...' : 'Confirm Language Selection'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

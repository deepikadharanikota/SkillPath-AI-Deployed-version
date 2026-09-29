import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  PlayCircle, 
  CheckCircle2, 
  Sparkles, 
  RefreshCw,
  Clock,
  Layers,
  Award,
  ArrowRight,
  Compass,
  Lock,
  BookOpen,
  ChevronRight,
  TrendingUp,
  Zap
} from 'lucide-react';
import { api } from '../api';

import { useQuery } from '@tanstack/react-query';

export default function LearningCatalog() {
  const navigate = useNavigate();

  const { data: resumeData, isLoading: loading } = useQuery({
    queryKey: ['learningResume'],
    queryFn: api.getLearningResume,
    staleTime: 5 * 60 * 1000,
  });

  if (loading && !resumeData) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', minHeight: '60vh', gap: '16px' }}>
        <RefreshCw size={36} color="#818cf8" style={{ animation: 'spin 1s linear infinite' }} />
        <span style={{ color: 'var(--text-muted)' }}>Loading Learning Center...</span>
      </div>
    );
  }

  const continueCourse = resumeData?.continue_course;
  const nextCourse = resumeData?.next_course;
  const learningPath = resumeData?.learning_path || [];
  const allTopics = resumeData?.all_topics || [];
  const targetRole = resumeData?.target_role || 'DevOps Engineer';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem', maxWidth: '1200px', margin: '0 auto', paddingBottom: '3rem' }}>
      
      {/* ── Page Header ── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <span className="badge badge-indigo" style={{ padding: '4px 10px', fontSize: '0.8rem' }}>
              Target Role: {targetRole}
            </span>
            <span className="badge badge-amber" style={{ padding: '4px 10px', fontSize: '0.8rem' }}>
              Priority Learning Journey
            </span>
          </div>
          <h1 style={{ fontSize: '2.2rem', marginBottom: '6px' }}>Learning Center</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            Resume active lessons right where you stopped, follow your role roadmap, and master career-critical skills.
          </p>
        </div>
      </div>

      {/* ── SECTION 1: HERO CONTINUE LEARNING CARD (Priority 1) ── */}
      {continueCourse ? (
        <div 
          className="glass-card" 
          style={{
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.14) 0%, rgba(168, 85, 247, 0.1) 50%, rgba(16, 185, 129, 0.06) 100%)',
            border: '1px solid rgba(99, 102, 241, 0.4)',
            borderRadius: '20px',
            padding: '2rem',
            boxShadow: '0 8px 32px rgba(99, 102, 241, 0.15)'
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span className="badge badge-indigo" style={{ padding: '6px 14px', fontSize: '0.85rem', fontWeight: '700' }}>
                <PlayCircle size={14} style={{ marginRight: '6px' }} />
                CONTINUE LEARNING
              </span>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                {continueCourse.last_accessed_at ? `Last active: ${new Date(continueCourse.last_accessed_at).toLocaleDateString()}` : 'In Progress'}
              </span>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '0.88rem', fontWeight: '600', color: 'var(--text-muted)' }}>Overall Progress:</span>
              <span style={{ fontSize: '1.1rem', fontWeight: '700', color: '#818cf8' }}>
                {continueCourse.progress?.percentage || 0}%
              </span>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '2rem', alignItems: 'center' }}>
            <div>
              <h2 style={{ fontSize: '1.8rem', marginBottom: '8px', color: '#fff' }}>
                {continueCourse.topic}
              </h2>
              <p style={{ color: '#c7d2fe', fontSize: '1rem', marginBottom: '14px', fontWeight: '500' }}>
                📺 {continueCourse.video_title || `Module ${continueCourse.current_module.toUpperCase()} Lesson`}
              </p>

              <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', alignItems: 'center', marginBottom: '1.25rem' }}>
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
                  <span>Resume from: <strong>{continueCourse.formatted_position || '00:00'}</strong></span>
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
                  <span>Module: <strong>{continueCourse.current_module.toUpperCase()}</strong></span>
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
                  <Award size={14} color="#10b981" />
                  <span>{continueCourse.progress?.completed_modules || 0} of 4 Modules Mastered</span>
                </span>
              </div>

              {/* Progress bar */}
              <div className="progress-track" style={{ height: '8px', maxWidth: '480px' }}>
                <div 
                  className="progress-fill" 
                  style={{ width: `${continueCourse.progress?.percentage || 0}%` }} 
                />
              </div>
            </div>

            <div>
              <button
                onClick={() => navigate(continueCourse.action_url)}
                className="btn-primary"
                style={{
                  padding: '16px 32px',
                  fontSize: '1.05rem',
                  fontWeight: '700',
                  boxShadow: '0 4px 20px rgba(99, 102, 241, 0.4)',
                  whiteSpace: 'nowrap'
                }}
              >
                <PlayCircle size={20} />
                <span>Resume Course</span>
                <ArrowRight size={18} />
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div 
          className="glass-card" 
          style={{
            padding: '2rem',
            borderRadius: '20px',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(6, 182, 212, 0.06) 100%)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '1.5rem'
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <CheckCircle2 size={22} color="#10b981" />
              <h2 style={{ fontSize: '1.4rem', color: '#fff' }}>All Active Courses Completed!</h2>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem' }}>
              You don't have any unfinished lessons right now. Advance your {targetRole} journey with the next recommended course below.
            </p>
          </div>
          {nextCourse && (
            <button
              onClick={() => navigate(nextCourse.action_url)}
              className="btn-emerald"
              style={{ padding: '14px 28px', fontSize: '0.98rem', fontWeight: '700' }}
            >
              <Sparkles size={18} />
              <span>Start Next: {nextCourse.topic}</span>
            </button>
          )}
        </div>
      )}

      {/* ── SECTION 2: NEXT RECOMMENDED COURSE (Intelligent Roadmap Recommendation) ── */}
      {nextCourse && (
        <div 
          className="glass-card"
          style={{
            padding: '1.75rem 2rem',
            border: '1px solid rgba(168, 85, 247, 0.35)',
            background: 'rgba(168, 85, 247, 0.04)',
            borderRadius: '18px'
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                <span className="badge badge-amber" style={{ padding: '4px 10px', fontSize: '0.78rem' }}>
                  <Sparkles size={12} style={{ marginRight: '4px' }} />
                  NEXT RECOMMENDED COURSE
                </span>
                <span className="badge badge-indigo" style={{ padding: '4px 10px', fontSize: '0.78rem' }}>
                  Adapted Level: {nextCourse.difficulty.toUpperCase()}
                </span>
              </div>
              <h3 style={{ fontSize: '1.5rem', color: '#fff', marginBottom: '4px' }}>
                {nextCourse.title}
              </h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                {nextCourse.description}
              </p>
            </div>

            <button
              onClick={() => navigate(nextCourse.action_url)}
              className="btn-secondary"
              style={{
                padding: '12px 24px',
                fontSize: '0.95rem',
                fontWeight: '600',
                border: '1px solid rgba(168, 85, 247, 0.5)',
                color: '#e9d5ff'
              }}
            >
              <span>Explore Course</span>
              <ArrowRight size={16} />
            </button>
          </div>

          {/* AI Rationale Box */}
          {nextCourse.rationale && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              backgroundColor: 'rgba(168, 85, 247, 0.08)',
              border: '1px solid rgba(168, 85, 247, 0.2)',
              borderRadius: '12px',
              padding: '12px 16px',
              fontSize: '0.88rem',
              color: '#d8b4fe'
            }}>
              <Zap size={18} color="#c084fc" style={{ flexShrink: 0 }} />
              <div>
                <strong>Why this course?</strong> {nextCourse.rationale}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── SECTION 3: YOUR ROLE ROADMAP ── */}
      {learningPath.length > 0 && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <div>
              <h2 style={{ fontSize: '1.45rem', marginBottom: '4px' }}>Your {targetRole} Roadmap</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
                Milestones ordered by prerequisites, career industry standards, and your existing skills.
              </p>
            </div>
            <button
              onClick={() => navigate('/dashboard')}
              className="btn-secondary"
              style={{ padding: '8px 16px', fontSize: '0.84rem' }}
            >
              <TrendingUp size={15} />
              <span>View Skill Analytics</span>
            </button>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
            gap: '1.25rem'
          }}>
            {learningPath.map((milestone, idx) => {
              const isLocked = milestone.status === 'locked';
              const isComp = milestone.status === 'completed';
              const isResume = milestone.status === 'mastered_via_resume';
              const isInProg = milestone.status === 'in_progress';
              const isNext = milestone.status === 'next_recommended';

              return (
                <div
                  key={milestone.topic}
                  className="glass-card"
                  style={{
                    padding: '1.4rem',
                    borderRadius: '16px',
                    border: isInProg 
                      ? '1px solid rgba(99, 102, 241, 0.5)' 
                      : isNext 
                      ? '1px solid rgba(168, 85, 247, 0.4)' 
                      : isComp 
                      ? '1px solid rgba(16, 185, 129, 0.3)' 
                      : '1px solid var(--border-color)',
                    background: isInProg 
                      ? 'rgba(99, 102, 241, 0.05)' 
                      : isNext
                      ? 'rgba(168, 85, 247, 0.04)'
                      : 'rgba(255, 255, 255, 0.02)',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    gap: '14px',
                    opacity: isLocked ? 0.7 : 1
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)', fontWeight: '600' }}>
                        Step {idx + 1}
                      </span>
                      <span className={`badge ${
                        isComp ? 'badge-emerald' : 
                        isResume ? 'badge-indigo' : 
                        isInProg ? 'badge-indigo' : 
                        isNext ? 'badge-amber' : 
                        'badge-gray'
                      }`} style={{ fontSize: '0.72rem' }}>
                        {isComp ? '✓ Mastered' : 
                         isResume ? 'Resume Verified' : 
                         isInProg ? '▶ Active' : 
                         isNext ? '⭐ Next Up' : 
                         isLocked ? '🔒 Locked' : 'Ready'}
                      </span>
                    </div>

                    <h3 style={{ fontSize: '1.18rem', marginBottom: '6px', color: '#fff' }}>
                      {milestone.topic}
                    </h3>
                    <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)', marginBottom: '10px', lineHeight: '1.4' }}>
                      {milestone.description || `Key milestone for ${targetRole}`}
                    </p>

                    {milestone.prerequisites?.length > 0 && (
                      <div style={{ fontSize: '0.76rem', color: isLocked ? '#f87171' : 'var(--text-dim)', marginBottom: '10px' }}>
                        {isLocked ? (
                          <span>⚠️ Prerequisite: {milestone.unmet_prerequisites?.join(', ')}</span>
                        ) : (
                          <span>✓ Prerequisites met: {milestone.prerequisites.join(', ')}</span>
                        )}
                      </div>
                    )}

                    {/* Progress bar */}
                    <div className="progress-track" style={{ height: '5px' }}>
                      <div 
                        className={`progress-fill ${isComp ? 'progress-fill-emerald' : ''}`}
                        style={{ width: `${milestone.progress?.percentage || 0}%` }}
                      />
                    </div>
                  </div>

                  <button
                    onClick={() => navigate(milestone.navigate_url)}
                    disabled={isLocked}
                    className={isInProg ? 'btn-primary' : isComp ? 'btn-secondary' : 'btn-secondary'}
                    style={{
                      width: '100%',
                      padding: '10px',
                      justifyContent: 'center',
                      fontSize: '0.88rem',
                      cursor: isLocked ? 'not-allowed' : 'pointer'
                    }}
                  >
                    {isLocked ? (
                      <>
                        <Lock size={15} />
                        <span>Locked</span>
                      </>
                    ) : (
                      <>
                        <PlayCircle size={15} />
                        <span>{milestone.action_label}</span>
                      </>
                    )}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ── SECTION 4: ALL CURRICULUM TOPICS CATALOG ── */}
      <div>
        <div style={{ marginBottom: '1.25rem' }}>
          <h2 style={{ fontSize: '1.45rem', marginBottom: '4px' }}>All Curriculum Topics</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
            Comprehensive catalog of technical disciplines available on SkillPath AI.
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
          gap: '1.5rem'
        }}>
          {allTopics.map((item) => {
            const isCompleted = item.progress?.is_completed;
            const pct = item.progress?.percentage || 0;
            return (
              <div
                key={item.topic}
                className="glass-card-interactive"
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.03)',
                  border: item.is_current ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid var(--border-color)',
                  borderRadius: '16px',
                  padding: '1.5rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '16px'
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                    <span className="badge badge-indigo" style={{ fontSize: '0.75rem' }}>
                      4 Modules
                    </span>
                    <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                      {(item.topic.toLowerCase().includes('data structure') || item.topic.toLowerCase() === 'dsa') && (
                        <span className="badge badge-purple" style={{ padding: '2px 8px', fontSize: '0.72rem' }}>
                          C++ / Java / Python
                        </span>
                      )}
                      {item.is_current && (
                        <span className="badge badge-amber" style={{ padding: '2px 8px', fontSize: '0.72rem' }}>
                          Active Course
                        </span>
                      )}
                    </div>
                  </div>

                  <h3 style={{ fontSize: '1.25rem', marginBottom: '6px', color: '#fff' }}>{item.topic}</h3>
                  <p style={{ fontSize: '0.84rem', color: 'var(--text-dim)', marginBottom: '12px' }}>
                    {item.description}
                  </p>

                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '8px', display: 'flex', justifyContent: 'space-between' }}>
                    <span>{item.progress?.completed_modules || 0} / 4 Modules Completed</span>
                    <span style={{ fontWeight: '600', color: isCompleted ? '#10b981' : '#818cf8' }}>{pct}%</span>
                  </div>

                  {/* Progress bar */}
                  <div className="progress-track" style={{ height: '6px' }}>
                    <div 
                      className={`progress-fill ${isCompleted ? 'progress-fill-emerald' : ''}`} 
                      style={{ width: `${pct}%` }} 
                    />
                  </div>
                </div>

                <button
                  onClick={() => navigate(item.navigate_url)}
                  className={isCompleted ? 'btn-secondary' : item.is_current ? 'btn-primary' : 'btn-secondary'}
                  style={{ width: '100%', padding: '10px', justifyContent: 'center' }}
                >
                  <PlayCircle size={16} />
                  <span>{isCompleted ? 'Review Content' : pct > 0 ? 'Continue Topic' : 'Start Topic'}</span>
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

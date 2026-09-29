import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  CheckCircle2, 
  AlertTriangle, 
  ArrowRight, 
  Target, 
  Sparkles, 
  RefreshCw,
  PlayCircle,
  TrendingUp,
  FileText
} from 'lucide-react';
import { api } from '../api';

import { useQuery } from '@tanstack/react-query';

export default function SkillGap() {
  const navigate = useNavigate();

  const { data: gapData, isLoading: loading, error: queryError } = useQuery({
    queryKey: ['skillGap'],
    queryFn: api.getSkillGap,
    staleTime: 5 * 60 * 1000,
  });

  const error = queryError?.message || '';

  if (loading && !gapData) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', minHeight: '50vh', gap: '14px' }}>
        <RefreshCw size={32} color="#818cf8" style={{ animation: 'spin 1s linear infinite' }} />
        <span style={{ color: 'var(--text-muted)' }}>Analyzing skill gaps...</span>
      </div>
    );
  }

  const matchPct = gapData?.match_percentage || 0;
  const alreadyHave = gapData?.already_have || [];
  const missing = gapData?.missing || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '1100px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
            <h1 style={{ fontSize: '2rem' }}>Skill Gap Analysis</h1>
            <span className="badge badge-indigo">
              <Target size={14} />
              {gapData?.target_role || 'Target Role'}
            </span>
          </div>
          <p style={{ color: 'var(--text-muted)' }}>
            Comparing your verified resume skills against the industry requirements for your target role.
          </p>
        </div>

        <button onClick={() => navigate('/resume')} className="btn-secondary">
          <FileText size={16} />
          <span>Update Resume</span>
        </button>
      </div>

      {/* Role Readiness Score Card */}
      <div className="glass-card" style={{ padding: '2rem', display: 'flex', alignItems: 'center', gap: '2rem', flexWrap: 'wrap' }}>
        <div style={{
          width: '120px',
          height: '120px',
          borderRadius: '50%',
          border: '8px solid rgba(99, 102, 241, 0.2)',
          borderTopColor: matchPct >= 70 ? '#10b981' : matchPct >= 40 ? '#f59e0b' : '#6366f1',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0
        }}>
          <span style={{ fontSize: '1.8rem', fontWeight: '800', color: '#fff' }}>{matchPct}%</span>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Readiness</span>
        </div>

        <div style={{ flex: 1, minWidth: '280px' }}>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '8px' }}>
            {matchPct >= 70 
              ? 'Strong Foundation for ' + gapData?.target_role 
              : matchPct >= 40 
              ? 'Moderate Alignment — Key Gaps Identified' 
              : 'Early Stage — Comprehensive Learning Needed'}
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', marginBottom: '1rem', lineHeight: '1.5' }}>
            You have acquired <strong style={{ color: '#fff' }}>{alreadyHave.length} of {gapData?.total_required || 0}</strong> core skills required for this role. 
            SkillPath AI will tailor your curriculum specifically around the <strong style={{ color: '#f59e0b' }}>{missing.length} missing skill gaps</strong> so you don't repeat what you already know.
          </p>

          <div className="progress-track" style={{ height: '10px' }}>
            <div 
              className={`progress-fill ${matchPct >= 70 ? 'progress-fill-emerald' : ''}`} 
              style={{ width: `${matchPct}%` }} 
            />
          </div>
        </div>
      </div>

      {/* ── Two Columns: Already Have vs Missing Gaps ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        {/* Missing Skills (GAPS) */}
        <div className="glass-card" style={{ padding: '1.75rem', border: '1px solid rgba(244, 63, 94, 0.2)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '1.25rem' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              backgroundColor: 'rgba(244, 63, 94, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <AlertTriangle size={18} color="#f43f5e" />
            </div>
            <div>
              <h3 style={{ fontSize: '1.15rem' }}>Missing Skill Gaps ({missing.length})</h3>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>Prioritized in your adaptive curriculum</span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {missing.map((sk) => (
              <div
                key={sk}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '12px 14px',
                  backgroundColor: 'rgba(244, 63, 94, 0.05)',
                  border: '1px solid rgba(244, 63, 94, 0.15)',
                  borderRadius: '10px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ color: '#f43f5e', fontWeight: '700' }}>⚠</span>
                  <span style={{ fontWeight: '600', fontSize: '0.95rem' }}>{sk}</span>
                  <span className="badge badge-rose" style={{ fontSize: '0.72rem', padding: '2px 8px' }}>Missing</span>
                </div>

                <button
                  onClick={() => navigate(`/learning/${encodeURIComponent(sk)}?module=intro`)}
                  className="btn-secondary"
                  style={{ padding: '6px 12px', fontSize: '0.8rem', gap: '4px' }}
                >
                  <PlayCircle size={14} />
                  <span>Learn</span>
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Acquired Skills */}
        <div className="glass-card" style={{ padding: '1.75rem', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '1.25rem' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              backgroundColor: 'rgba(16, 185, 129, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <CheckCircle2 size={18} color="#10b981" />
            </div>
            <div>
              <h3 style={{ fontSize: '1.15rem' }}>Already Acquired Skills ({alreadyHave.length})</h3>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>Detected from your uploaded resume</span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {alreadyHave.map((sk) => (
              <div
                key={sk}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '12px 14px',
                  backgroundColor: 'rgba(16, 185, 129, 0.05)',
                  border: '1px solid rgba(16, 185, 129, 0.15)',
                  borderRadius: '10px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <CheckCircle2 size={16} color="#10b981" />
                  <span style={{ fontWeight: '600', fontSize: '0.95rem' }}>{sk}</span>
                  <span className="badge badge-emerald" style={{ fontSize: '0.72rem', padding: '2px 8px' }}>Already Have</span>
                </div>

                <button
                  onClick={() => navigate(`/learning/${encodeURIComponent(sk)}?module=intro`)}
                  className="btn-secondary"
                  style={{ padding: '6px 12px', fontSize: '0.8rem', color: 'var(--text-muted)' }}
                >
                  <span>Review</span>
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Banner */}
      <div className="glass-card" style={{
        padding: '2rem',
        background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.1) 100%)',
        border: '1px solid rgba(99, 102, 241, 0.3)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <div>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '6px' }}>Ready to bridge your skill gaps?</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Start with your highest-priority missing skill. Watch required videos to unlock your adaptive quiz.
          </p>
        </div>

        {missing.length > 0 && (
          <button
            onClick={() => navigate(`/learning/${encodeURIComponent(missing[0])}?module=intro`)}
            className="btn-primary"
            style={{ padding: '12px 24px', fontSize: '1rem' }}
          >
            <span>Start Learning {missing[0]}</span>
            <ArrowRight size={18} />
          </button>
        )}
      </div>
    </div>
  );
}

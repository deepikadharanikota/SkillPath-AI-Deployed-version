import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { 
  CheckCircle2, 
  XCircle, 
  Sparkles, 
  ArrowRight, 
  RefreshCw, 
  TrendingUp, 
  BookOpen, 
  Award,
  AlertCircle
} from 'lucide-react';
import { api } from '../api';
import { useQueryClient } from '@tanstack/react-query';

export default function QuizResults() {
  const { quizId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  const [results, setResults] = useState(location.state?.results || null);
  const [loading, setLoading] = useState(!location.state?.results);
  const [error, setError] = useState('');

  const queryClient = useQueryClient();

  useEffect(() => {
    // Invalidate caches so dashboard and resume reflect the completed quiz
    queryClient.invalidateQueries({ queryKey: ['dashboardSummary'] });
    queryClient.invalidateQueries({ queryKey: ['learningResume'] });
    queryClient.invalidateQueries({ queryKey: ['dashboardInsights'] });

    if (!results && quizId) {
      const loadResults = async () => {
        setLoading(true);
        try {
          const data = await api.getQuizResults(quizId);
          setResults(data);
        } catch (err) {
          console.error('Failed to load quiz results:', err);
          setError('Could not retrieve quiz results.');
        } finally {
          setLoading(false);
        }
      };
      loadResults();
    }
  }, [quizId, results, queryClient]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <RefreshCw size={36} color="#818cf8" style={{ animation: 'spin 1s linear infinite' }} />
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className="glass-card" style={{ maxWidth: '600px', margin: '3rem auto', padding: '2rem', textAlign: 'center' }}>
        <AlertCircle size={44} color="#f43f5e" style={{ margin: '0 auto 1rem' }} />
        <h2 style={{ fontSize: '1.3rem', marginBottom: '8px' }}>Result Not Found</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>{error || 'No quiz submission details found.'}</p>
        <button onClick={() => navigate('/dashboard')} className="btn-primary">
          <span>Return to Dashboard</span>
        </button>
      </div>
    );
  }

  const score = results.score || 0;
  const total = results.total_questions || results.questions?.length || 15;
  const percentage = results.percentage || 0;
  const correctCount = results.correct_count !== undefined ? results.correct_count : score;
  const unansweredCount = results.unanswered_count !== undefined 
    ? results.unanswered_count 
    : (results.questions ? results.questions.filter(q => q.isUnanswered || q.userAnswer?.includes('Not answered')).length : 0);
  const incorrectCount = results.incorrect_count !== undefined 
    ? results.incorrect_count 
    : Math.max(0, total - correctCount - unansweredCount);
  const performanceLevel = results.performance_level || (percentage >= 85 ? 'Exceptional' : percentage >= 70 ? 'Strong' : percentage >= 50 ? 'Satisfactory' : 'Needs Improvement');

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* ── Celebration Header & Scores ── */}
      <div className="glass-card" style={{
        padding: '2.5rem',
        textAlign: 'center',
        background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(168, 85, 247, 0.08) 100%)'
      }}>
        <div style={{ fontSize: '3rem', marginBottom: '8px' }}>🎉</div>
        <h1 style={{ fontSize: '2.2rem', marginBottom: '6px' }}>Quiz Completed!</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '1rem', marginBottom: '1.75rem' }}>
          {results.topic} &nbsp;|&nbsp; {results.module?.toUpperCase()} MODULE &nbsp;|&nbsp; {results.difficulty?.toUpperCase()} LEVEL
        </p>

        {/* Score Metrics Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
          gap: '0.85rem',
          maxWidth: '800px',
          margin: '0 auto 1.5rem'
        }}>
          <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.03)', padding: '1.25rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>Score</div>
            <div style={{ fontSize: '1.6rem', fontWeight: '800', color: '#fff' }}>{score} / {total}</div>
          </div>

          <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.03)', padding: '1.25rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>Percentage</div>
            <div style={{ fontSize: '1.6rem', fontWeight: '800', color: percentage >= 70 ? '#10b981' : '#818cf8' }}>{percentage}%</div>
          </div>

          <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.03)', padding: '1.25rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>Correct</div>
            <div style={{ fontSize: '1.6rem', fontWeight: '800', color: '#10b981' }}>{correctCount}</div>
          </div>

          <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.03)', padding: '1.25rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>Incorrect</div>
            <div style={{ fontSize: '1.6rem', fontWeight: '800', color: '#f43f5e' }}>{incorrectCount}</div>
          </div>

          <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.03)', padding: '1.25rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>Unanswered</div>
            <div style={{ fontSize: '1.6rem', fontWeight: '800', color: '#f59e0b' }}>{unansweredCount}</div>
          </div>

          <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.03)', padding: '1.25rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>Difficulty</div>
            <div style={{ fontSize: '1.3rem', fontWeight: '800', color: '#a855f7', textTransform: 'capitalize' }}>
              {results.difficulty || 'Intermediate'}
            </div>
          </div>
        </div>

        {/* Performance Level */}
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', marginBottom: '1.5rem' }}>
          <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Performance Level:</span>
          <span className={`badge ${percentage >= 85 ? 'badge-emerald' : percentage >= 70 ? 'badge-indigo' : 'badge-amber'}`} style={{ fontSize: '0.9rem', padding: '4px 14px' }}>
            {performanceLevel}
          </span>
        </div>

        {/* Adaptive Feedback */}
        {results.adaptive_feedback && (
          <div style={{
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            border: '1px solid rgba(99, 102, 241, 0.25)',
            borderRadius: '12px',
            padding: '12px 18px',
            maxWidth: '650px',
            margin: '0 auto 1.5rem',
            color: '#e0e7ff',
            fontSize: '0.92rem'
          }}>
            <Sparkles size={16} color="#818cf8" style={{ display: 'inline', marginRight: '6px' }} />
            {results.adaptive_feedback}
          </div>
        )}

        {/* Action CTAs */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <button onClick={() => navigate('/dashboard')} className="btn-secondary">
            <span>Return to Dashboard</span>
          </button>
          <button onClick={() => navigate('/learning')} className="btn-primary">
            <span>Continue Curriculum</span>
            <ArrowRight size={16} />
          </button>
        </div>
      </div>

      {/* ── Question by Question Breakdown ── */}
      <div>
        <h2 style={{ fontSize: '1.4rem', marginBottom: '1rem' }}>Detailed Answer Review (All 15 Questions)</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {(results.questions || []).map((q, idx) => {
            const isCorrect = q.isCorrect;
            const isUnanswered = q.isUnanswered || q.userAnswer?.includes('Not answered');

            return (
              <div
                key={idx}
                className="glass-card"
                style={{
                  padding: '1.75rem',
                  border: isCorrect 
                    ? '1px solid rgba(16, 185, 129, 0.25)' 
                    : isUnanswered 
                      ? '1px solid rgba(245, 158, 11, 0.3)' 
                      : '1px solid rgba(244, 63, 94, 0.25)'
                }}
              >
                {/* Question Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '10px', marginBottom: '1rem' }}>
                  <h3 style={{ fontSize: '1.1rem', lineHeight: '1.4', flex: 1 }}>
                    <span style={{ color: 'var(--text-dim)', marginRight: '8px' }}>#{idx + 1}</span>
                    {q.question}
                  </h3>
                  {isCorrect ? (
                    <span className="badge badge-emerald" style={{ padding: '4px 12px' }}>
                      <CheckCircle2 size={14} />
                      <span>✓ Correct</span>
                    </span>
                  ) : isUnanswered ? (
                    <span className="badge badge-amber" style={{ padding: '4px 12px' }}>
                      <span>⏱ Time expired (Not answered)</span>
                    </span>
                  ) : (
                    <span className="badge badge-rose" style={{ padding: '4px 12px' }}>
                      <XCircle size={14} />
                      <span>✗ Incorrect</span>
                    </span>
                  )}
                </div>

                {/* Answers Comparison */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '1rem' }}>
                  <div style={{
                    padding: '10px 14px',
                    borderRadius: '8px',
                    backgroundColor: isCorrect 
                      ? 'rgba(16, 185, 129, 0.1)' 
                      : isUnanswered 
                        ? 'rgba(245, 158, 11, 0.1)' 
                        : 'rgba(244, 63, 94, 0.1)',
                    border: isCorrect 
                      ? '1px solid rgba(16, 185, 129, 0.3)' 
                      : isUnanswered 
                        ? '1px solid rgba(245, 158, 11, 0.3)' 
                        : '1px solid rgba(244, 63, 94, 0.3)',
                    fontSize: '0.92rem'
                  }}>
                    <strong style={{ color: isCorrect ? '#6ee7b7' : isUnanswered ? '#fcd34d' : '#fda4af' }}>
                      Your Answer: 
                    </strong>
                    <span> {q.userAnswer || 'Not answered'}</span>
                  </div>

                  {!isCorrect && (
                    <div style={{
                      padding: '10px 14px',
                      borderRadius: '8px',
                      backgroundColor: 'rgba(16, 185, 129, 0.1)',
                      border: '1px solid rgba(16, 185, 129, 0.3)',
                      fontSize: '0.92rem'
                    }}>
                      <strong style={{ color: '#6ee7b7' }}>Correct Answer: </strong>
                      <span> {q.correctAnswer}</span>
                    </div>
                  )}
                </div>

                {/* Educational Explanation */}
                {q.explanation && (
                  <div style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.02)',
                    padding: '12px 14px',
                    borderRadius: '8px',
                    fontSize: '0.86rem',
                    color: 'var(--text-muted)',
                    lineHeight: '1.45',
                    borderLeft: '3px solid #818cf8'
                  }}>
                    <strong style={{ color: '#fff' }}>Explanation: </strong>
                    {q.explanation}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

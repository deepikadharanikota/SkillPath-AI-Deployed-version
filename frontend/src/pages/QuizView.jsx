import React, { useState, useEffect, useRef } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { 
  Sparkles, 
  HelpCircle, 
  ArrowRight, 
  ArrowLeft,
  RefreshCw, 
  AlertCircle, 
  Clock,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import { api } from '../api';
import { useLearning } from '../context/LearningContext';
import { useQueryClient } from '@tanstack/react-query';

const QUESTION_TIME_LIMIT = 30; // Strictly 30 seconds per question

export default function QuizView() {
  const { topicId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const currentTopic = decodeURIComponent(topicId || 'Machine Learning');
  const currentModule = searchParams.get('module') || 'intro';

  const [quizData, setQuizData] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // 30-second timer state
  const [timeLeft, setTimeLeft] = useState(QUESTION_TIME_LIMIT);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [unansweredCountForModal, setUnansweredCountForModal] = useState(0);

  // Timer interval reference to prevent duplicate/leaked timers
  const timerRef = useRef(null);

  // Refs for real-time access inside asynchronous timer callbacks
  const answersRef = useRef({});
  const currentIndexRef = useRef(0);
  const quizDataRef = useRef(null);
  const isTransitioningRef = useRef(false);

  answersRef.current = selectedAnswers;
  currentIndexRef.current = currentIndex;
  quizDataRef.current = quizData;
  isTransitioningRef.current = isTransitioning;

  // Clear running timer safely
  const stopTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const { activeQuiz: savedQuiz, setQuizSession, clearQuizSession } = useLearning();
  const queryClient = useQueryClient();

  // 1. Fetch or Restore Quiz Data on Mount
  useEffect(() => {
    const fetchQuiz = async () => {
      // Check if active quiz session already exists for this exact topic and module
      if (savedQuiz && savedQuiz.topic === currentTopic && savedQuiz.module === currentModule && savedQuiz.questions?.length) {
        setQuizData(savedQuiz);
        setLoading(false);
        return;
      }

      setLoading(true);
      setError('');
      try {
        const data = await api.generateQuiz(currentTopic, currentModule);
        const quizPayload = { ...data, topic: currentTopic, module: currentModule };
        setQuizData(quizPayload);
        setQuizSession(quizPayload);
      } catch (err) {
        console.error('Quiz generate error:', err);
        setError(err.message || 'Could not load quiz. Complete all required course videos first.');
      } finally {
        setLoading(false);
      }
    };

    fetchQuiz();

    return () => stopTimer();
  }, [currentTopic, currentModule]);

  // 2. Core Submission Function
  const executeSubmit = async (answersToSubmit) => {
    if (submitting) return;
    stopTimer();
    setSubmitting(true);
    setError('');
    setShowConfirmModal(false);

    const activeQuiz = quizDataRef.current || savedQuiz;
    if (!activeQuiz) {
      setError('Quiz session could not be completed. Please click Retry.');
      setSubmitting(false);
      return;
    }

    // Assemble final answers for all 15 questions
    const finalAnswers = {};
    const questions = activeQuiz.questions || [];
    for (let i = 0; i < questions.length; i++) {
      const qKey = String(questions[i].id);
      finalAnswers[qKey] = (answersToSubmit && answersToSubmit[qKey]) || answersRef.current[qKey] || '__UNANSWERED__';
    }

    try {
      const results = await api.submitQuiz(
        activeQuiz.quiz_id,
        currentTopic,
        currentModule,
        finalAnswers
      );
      // Clean up active quiz session
      clearQuizSession();
      // Invalidate dashboard and learning caches so updated mastery shows instantly
      queryClient.invalidateQueries({ queryKey: ['dashboardSummary'] });
      queryClient.invalidateQueries({ queryKey: ['learningResume'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardInsights'] });
      
      // Navigate to results page with response state
      navigate(`/quiz/${activeQuiz.quiz_id}/results`, { state: { results } });
    } catch (err) {
      console.error('Submit quiz error:', err);
      setError(err.message || 'Failed to submit quiz. Please try again.');
      setSubmitting(false);
    }
  };

  // 3. 30-Second Timer Lifecycle per Question
  useEffect(() => {
    // Stop timer if loading, error, submitting, or no quiz
    if (loading || error || submitting || !quizData || !quizData.questions?.length) {
      stopTimer();
      return;
    }

    // Stop any existing timer before starting fresh
    stopTimer();

    // Reset countdown to exactly 30 seconds for this question
    setTimeLeft(QUESTION_TIME_LIMIT);
    setIsTransitioning(false);

    // Start clean 1-second ticking interval
    timerRef.current = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          return 0; // Expiry handled cleanly in dedicated effect below
        }
        return prev - 1;
      });
    }, 1000);

    return () => stopTimer();
  }, [currentIndex, quizData, loading, submitting]);

  // 4. Handle Timer Expiration when timeLeft reaches 0
  useEffect(() => {
    if (timeLeft === 0 && !loading && !submitting && !isTransitioningRef.current && quizData) {
      handleTimeExpired();
    }
  }, [timeLeft]);

  const handleTimeExpired = () => {
    if (isTransitioningRef.current || submitting) return;
    setIsTransitioning(true);
    stopTimer();

    const questions = quizDataRef.current?.questions || [];
    const total = questions.length || 15;
    const currentQ = questions[currentIndexRef.current];

    if (!currentQ) return;

    const qKey = String(currentQ.id);
    const updatedAnswers = { ...answersRef.current };
    if (!updatedAnswers[qKey]) {
      updatedAnswers[qKey] = '__UNANSWERED__';
    }
    setSelectedAnswers(updatedAnswers);
    answersRef.current = updatedAnswers;

    // Advance to next question or submit if on Question 15
    setTimeout(() => {
      if (currentIndexRef.current + 1 < total) {
        setCurrentIndex((prev) => prev + 1);
      } else {
        // Question 15 timed out -> submit entire quiz
        executeSubmit(updatedAnswers);
      }
    }, 300);
  };

  // 5. Handle Option Click (Automatic Navigation)
  const handleSelectOption = (optionText) => {
    if (isTransitioningRef.current || submitting) return;
    setIsTransitioning(true);
    stopTimer();

    const questions = quizData?.questions || [];
    const total = questions.length || 15;
    const currentQ = questions[currentIndex];

    if (!currentQ) return;

    const qKey = String(currentQ.id);
    const updatedAnswers = {
      ...selectedAnswers,
      [qKey]: optionText
    };
    setSelectedAnswers(updatedAnswers);
    answersRef.current = updatedAnswers;

    // 250ms visual confirmation of choice, then auto-advance or submit
    setTimeout(() => {
      if (currentIndex + 1 < total) {
        setCurrentIndex((prev) => prev + 1);
      } else {
        // Question 15 completed -> submit automatically
        executeSubmit(updatedAnswers);
      }
    }, 250);
  };

  // 6. Manual [Submit Quiz] Button Handler
  const handleManualSubmitClick = () => {
    if (submitting) return;

    const questions = quizData?.questions || [];
    let unansweredCount = 0;
    questions.forEach((q) => {
      const val = selectedAnswers[String(q.id)];
      if (!val || val === '__UNANSWERED__') {
        unansweredCount++;
      }
    });

    if (unansweredCount > 0) {
      setUnansweredCountForModal(unansweredCount);
      setShowConfirmModal(true);
    } else {
      executeSubmit(selectedAnswers);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', gap: '16px' }}>
        <RefreshCw size={38} color="#818cf8" style={{ animation: 'spin 1s linear infinite' }} />
        <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem' }}>Generating 15 Adaptive Questions via Groq AI...</p>
        <style>{`@keyframes spin { 100% { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (error && !quizData) {
    return (
      <div className="glass-card" style={{ maxWidth: '600px', margin: '3rem auto', padding: '2.5rem', textAlign: 'center' }}>
        <AlertCircle size={48} color="#f43f5e" style={{ margin: '0 auto 1rem' }} />
        <h2 style={{ fontSize: '1.4rem', marginBottom: '8px' }}>Quiz Access Restricted</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', lineHeight: '1.5' }}>
          {error}
        </p>
        <button
          onClick={() => navigate(`/learning/${encodeURIComponent(currentTopic)}?module=${encodeURIComponent(currentModule)}`)}
          className="btn-primary"
        >
          <span>Return to Course Videos</span>
          <ArrowRight size={16} />
        </button>
      </div>
    );
  }

  const questions = quizData?.questions || [];
  const currentQ = questions[currentIndex];
  const totalQuestions = questions.length || 15;
  const isTimeCritical = timeLeft <= 8;
  const timerPercentage = (timeLeft / QUESTION_TIME_LIMIT) * 100;
  const answeredCount = Object.values(selectedAnswers).filter(v => v && v !== '__UNANSWERED__').length;

  return (
    <div style={{ maxWidth: '840px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* ── Top Header Card ── */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '0.82rem', color: '#818cf8', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Adaptive Assessment • {quizData?.difficulty?.toUpperCase()} LEVEL
              </span>
              <span className="badge badge-indigo" style={{ padding: '2px 8px', fontSize: '0.75rem' }}>
                15 Questions
              </span>
              {(quizData?.language || quizData?.dsa_language) && (
                <span className="badge badge-purple" style={{ padding: '2px 8px', fontSize: '0.75rem' }}>
                  Language: {quizData.language || quizData.dsa_language}
                </span>
              )}
            </div>
            <h1 style={{ fontSize: '1.45rem', marginTop: '4px' }}>{currentTopic} — {currentModule.toUpperCase()}</h1>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '0.86rem', color: 'var(--text-muted)' }}>
              Answered: <strong style={{ color: '#fff' }}>{answeredCount} / {totalQuestions}</strong>
            </span>
          </div>
        </div>

        {/* Overall 15-Question Progress Track */}
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', color: 'var(--text-dim)', marginBottom: '6px' }}>
          <span>Question {currentIndex + 1} of {totalQuestions}</span>
          <span>{Math.round(((currentIndex + 1) / totalQuestions) * 100)}% Progress</span>
        </div>
        <div className="progress-track" style={{ height: '6px' }}>
          <div className="progress-fill" style={{ width: `${((currentIndex + 1) / totalQuestions) * 100}%` }} />
        </div>
      </div>

      {/* Error Alert if any during submit */}
      {error && (
        <div style={{
          backgroundColor: 'rgba(239, 68, 68, 0.15)',
          border: '1px solid rgba(239, 68, 68, 0.4)',
          borderRadius: '12px',
          padding: '12px 16px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          color: '#fca5a5'
        }}>
          <AlertCircle size={20} style={{ flexShrink: 0 }} />
          <span>{error}</span>
        </div>
      )}

      {/* ── Active Question Card with PROMINENT 30-SECOND COUNTDOWN ── */}
      {currentQ && (
        <div className="glass-card" style={{ padding: '2rem', position: 'relative' }}>
          {/* Submitting Overlay */}
          {submitting && (
            <div style={{
              position: 'absolute',
              top: 0, left: 0, right: 0, bottom: 0,
              backgroundColor: 'rgba(11, 15, 25, 0.88)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '14px',
              borderRadius: '16px',
              zIndex: 20
            }}>
              <RefreshCw size={40} color="#818cf8" style={{ animation: 'spin 1s linear infinite' }} />
              <span style={{ fontSize: '1.1rem', fontWeight: '700', color: '#fff' }}>Evaluating 15 Questions & Updating Adaptive Level...</span>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Saving attempt to your learning history</span>
            </div>
          )}

          {/* 30-Second Countdown Timer Header */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '12px 18px',
            borderRadius: '12px',
            backgroundColor: isTimeCritical ? 'rgba(239, 68, 68, 0.16)' : 'rgba(99, 102, 241, 0.12)',
            border: isTimeCritical ? '1px solid rgba(239, 68, 68, 0.6)' : '1px solid rgba(99, 102, 241, 0.3)',
            marginBottom: '1rem',
            transition: 'all 0.3s ease'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Clock size={22} color={isTimeCritical ? '#ef4444' : '#818cf8'} />
              <span style={{ fontSize: '1.05rem', fontWeight: '600', color: isTimeCritical ? '#fca5a5' : '#fff' }}>
                Time Remaining: <strong style={{
                  fontSize: '1.3rem',
                  color: isTimeCritical ? '#ef4444' : '#818cf8',
                  fontVariantNumeric: 'tabular-nums',
                  marginLeft: '4px'
                }}>{timeLeft}s</strong>
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="badge badge-indigo" style={{ padding: '6px 12px', fontSize: '0.85rem' }}>
                Question {currentIndex + 1} / {totalQuestions}
              </span>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)', textTransform: 'capitalize' }}>
                Level: {currentQ.difficulty || quizData.difficulty}
              </span>
            </div>
          </div>

          {/* 30-Second Visual Depleting Progress Bar */}
          <div style={{
            height: '5px',
            backgroundColor: 'rgba(255, 255, 255, 0.08)',
            borderRadius: '3px',
            overflow: 'hidden',
            marginBottom: '1.75rem'
          }}>
            <div style={{
              height: '100%',
              width: `${timerPercentage}%`,
              backgroundColor: isTimeCritical ? '#ef4444' : '#6366f1',
              transition: 'width 1s linear, background-color 0.3s ease'
            }} />
          </div>

          {/* Question Text */}
          <h2 style={{ fontSize: '1.3rem', lineHeight: '1.5', marginBottom: '1.75rem', fontWeight: '600' }}>
            {currentQ.question}
          </h2>

          {/* Multiple Choice Options */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '2rem' }}>
            {currentQ.options.map((opt, optIdx) => {
              const qKey = String(currentQ.id);
              const isSelected = selectedAnswers[qKey] === opt;

              return (
                <div
                  key={optIdx}
                  onClick={() => handleSelectOption(opt)}
                  style={{
                    padding: '16px 20px',
                    borderRadius: '14px',
                    backgroundColor: isSelected ? 'rgba(99, 102, 241, 0.25)' : 'rgba(255, 255, 255, 0.03)',
                    border: isSelected ? '2px solid #6366f1' : '1px solid var(--border-color)',
                    cursor: isTransitioning || submitting ? 'default' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '16px',
                    transition: 'all 0.15s ease',
                    boxShadow: isSelected ? '0 4px 16px rgba(99, 102, 241, 0.35)' : 'none'
                  }}
                  onMouseEnter={(e) => {
                    if (!isSelected && !isTransitioning) e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.06)';
                  }}
                  onMouseLeave={(e) => {
                    if (!isSelected && !isTransitioning) e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.03)';
                  }}
                >
                  <div style={{
                    width: '30px',
                    height: '30px',
                    borderRadius: '50%',
                    border: isSelected ? '2px solid #6366f1' : '2px solid rgba(255, 255, 255, 0.3)',
                    backgroundColor: isSelected ? '#6366f1' : 'transparent',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                    fontSize: '0.85rem',
                    fontWeight: '700',
                    flexShrink: 0
                  }}>
                    {String.fromCharCode(65 + optIdx)}
                  </div>
                  <span style={{ fontSize: '1.02rem', color: isSelected ? '#fff' : 'var(--text-main)', fontWeight: isSelected ? '600' : '400', flex: 1 }}>
                    {opt}
                  </span>
                  {isSelected && <CheckCircle2 size={20} color="#818cf8" />}
                </div>
              );
            })}
          </div>

          {/* ── Navigation and SUBMIT QUIZ Button Bar ── */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            paddingTop: '1.5rem',
            borderTop: '1px solid var(--border-color)',
            flexWrap: 'wrap',
            gap: '12px'
          }}>
            <button
              type="button"
              onClick={() => {
                stopTimer();
                setCurrentIndex((prev) => Math.max(0, prev - 1));
              }}
              disabled={currentIndex === 0 || submitting}
              className="btn-secondary"
              style={{ opacity: currentIndex === 0 ? 0.3 : 1 }}
            >
              <ArrowLeft size={16} />
              <span>Previous</span>
            </button>

            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              {currentIndex + 1 < totalQuestions && (
                <button
                  type="button"
                  onClick={() => {
                    stopTimer();
                    setCurrentIndex((prev) => Math.min(totalQuestions - 1, prev + 1));
                  }}
                  disabled={submitting}
                  className="btn-secondary"
                >
                  <span>Next Question</span>
                  <ArrowRight size={16} />
                </button>
              )}

              {/* Working Submit Quiz Button */}
              <button
                type="button"
                onClick={handleManualSubmitClick}
                disabled={submitting}
                className="btn-emerald"
                style={{
                  padding: '12px 24px',
                  fontSize: '1rem',
                  fontWeight: '700',
                  opacity: submitting ? 0.7 : 1,
                  cursor: submitting ? 'not-allowed' : 'pointer',
                  boxShadow: currentIndex === totalQuestions - 1 ? '0 0 16px rgba(16, 185, 129, 0.45)' : 'none'
                }}
              >
                {submitting ? (
                  <>
                    <RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} />
                    <span>Submitting Quiz...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={16} />
                    <span>{currentIndex === totalQuestions - 1 ? 'Submit Final Quiz' : 'Submit Quiz'}</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Confirmation Modal for Unanswered Questions ── */}
      {showConfirmModal && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.78)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 999,
          padding: '1rem'
        }}>
          <div className="glass-card" style={{ maxWidth: '480px', width: '100%', padding: '2rem', textAlign: 'center' }}>
            <AlertTriangle size={48} color="#f59e0b" style={{ margin: '0 auto 1rem' }} />
            <h3 style={{ fontSize: '1.35rem', marginBottom: '0.75rem' }}>Submit with Unanswered Questions?</h3>
            <p style={{ color: 'var(--text-muted)', marginBottom: '1.75rem', lineHeight: '1.5', fontSize: '0.95rem' }}>
              You have <strong style={{ color: '#f59e0b' }}>{unansweredCountForModal}</strong> unanswered question{unansweredCountForModal > 1 ? 's' : ''} out of {totalQuestions}.
              Any unanswered questions will be marked as incorrect.
            </p>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button
                type="button"
                onClick={() => setShowConfirmModal(false)}
                className="btn-secondary"
                style={{ padding: '10px 20px' }}
              >
                <span>Keep Answering</span>
              </button>
              <button
                type="button"
                onClick={() => executeSubmit(selectedAnswers)}
                disabled={submitting}
                className="btn-emerald"
                style={{ padding: '10px 22px' }}
              >
                <span>{submitting ? 'Submitting...' : 'Yes, Submit Quiz'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

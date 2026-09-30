import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../api';

const LearningContext = createContext(null);

const STORAGE_KEY_POSITIONS = 'skillpath_video_positions';
const STORAGE_KEY_LAST_SESSION = 'skillpath_last_learning_session';

export function LearningProvider({ children }) {
  // 1. Playback positions per video ID
  const [videoPositions, setVideoPositions] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_POSITIONS);
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  });

  // 2. Active learning session (topic, module, video)
  const [activeSession, setActiveSession] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_LAST_SESSION);
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  // 3. In-memory Quiz state (preserves active quiz progress across navigation)
  const [activeQuiz, setActiveQuiz] = useState(null);

  // 4. Learning Time State (persisted & live updated)
  const [learningHours, setLearningHours] = useState(0.0);
  const [formattedLearningTime, setFormattedLearningTime] = useState('0h 00m');

  // Ref tracking uncommitted active seconds to batch updates every 30s
  const uncommittedSecondsRef = React.useRef(0);
  const lastInteractionRef = React.useRef(Date.now());
  const activeSessionRef = React.useRef(activeSession);
  activeSessionRef.current = activeSession;

  // Track user interaction to detect idle state (idle threshold: 2 minutes)
  useEffect(() => {
    const handleUserInteraction = () => {
      lastInteractionRef.current = Date.now();
    };

    const events = ['mousemove', 'keydown', 'click', 'scroll', 'touchstart'];
    events.forEach((ev) => window.addEventListener(ev, handleUserInteraction, { passive: true }));

    return () => {
      events.forEach((ev) => window.removeEventListener(ev, handleUserInteraction));
    };
  }, []);

  // Flush accumulated active time to backend
  const flushHeartbeat = useCallback(async (isUnload = false) => {
    const secs = uncommittedSecondsRef.current;
    if (secs < 3) return; // Ignore trivial bursts under 3 seconds

    uncommittedSecondsRef.current = 0;
    const session = activeSessionRef.current;
    const topic = session?.topic || null;
    const module = session?.module || null;
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const now = new Date();
    const localDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;

    if (isUnload) {
      // Use keepalive fetch on tab close or navigation away
      try {
        const token = localStorage.getItem('skillpath_token') || '';
        const payload = JSON.stringify({
          duration_seconds: secs,
          topic,
          module,
          client_date: localDate,
          timezone: tz,
        });
        const headers = { 'Content-Type': 'application/json' };
        if (token) {
          headers['token'] = token;
          headers['Authorization'] = `Bearer ${token}`;
        }
        fetch(`${api.API_URL || ''}/learning/time-heartbeat`, {
          method: 'POST',
          headers,
          body: payload,
          keepalive: true,
        }).catch(() => {});
      } catch {}
      return;
    }

    try {
      const res = await api.sendTimeHeartbeat(secs, topic, module, localDate, tz);
      if (res && res.formatted_time) {
        setFormattedLearningTime(res.formatted_time);
        setLearningHours(res.total_learning_hours || 0);
      }
    } catch (err) {
      console.warn('Time heartbeat note:', err?.message);
    }
  }, []);

  // Active time ticker: ticks every 1 second when tab is active and user is interacting
  useEffect(() => {
    const interval = setInterval(() => {
      const isVisible = document.visibilityState === 'visible';
      const isNotIdle = Date.now() - lastInteractionRef.current < 120000; // 2 min threshold
      const hasToken = !!localStorage.getItem('skillpath_token');

      if (isVisible && isNotIdle && hasToken) {
        uncommittedSecondsRef.current += 1;

        // Batch send every 30 seconds
        if (uncommittedSecondsRef.current >= 30) {
          flushHeartbeat(false);
        }
      }
    }, 1000);

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'hidden') {
        flushHeartbeat(true);
      }
    };

    const handleBeforeUnload = () => {
      flushHeartbeat(true);
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      clearInterval(interval);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('beforeunload', handleBeforeUnload);
      flushHeartbeat(false);
    };
  }, [flushHeartbeat]);

  // Sync positions to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY_POSITIONS, JSON.stringify(videoPositions));
    } catch (e) {
      console.warn('Could not save video positions to localStorage:', e);
    }
  }, [videoPositions]);

  // Sync activeSession to localStorage
  useEffect(() => {
    if (activeSession) {
      try {
        localStorage.setItem(STORAGE_KEY_LAST_SESSION, JSON.stringify(activeSession));
      } catch (e) {
        console.warn('Could not save active session to localStorage:', e);
      }
    }
  }, [activeSession]);

  const saveVideoPosition = useCallback((videoId, seconds, topic = null, module = null, title = '') => {
    if (!videoId) return;
    setVideoPositions((prev) => ({
      ...prev,
      [videoId]: seconds,
    }));

    if (topic && module) {
      setActiveSession((prev) => ({
        ...(prev || {}),
        topic,
        module,
        videoId,
        title: title || prev?.title || '',
        position: seconds,
        updatedAt: new Date().toISOString(),
      }));

      // Async backend sync without blocking the UI
      api.saveLearningPosition(topic, module, videoId, seconds, title).catch((err) => {
        console.warn('Background learning position sync note:', err?.message);
      });
    }
  }, []);

  const getVideoPosition = useCallback((videoId) => {
    if (!videoId) return 0;
    return videoPositions[videoId] || 0;
  }, [videoPositions]);

  const updateActiveSession = useCallback((topic, module, video = null) => {
    setActiveSession((prev) => ({
      topic: topic || prev?.topic || 'Machine Learning',
      module: module || prev?.module || 'intro',
      videoId: video?.id || video?.url || prev?.videoId || null,
      title: video?.title || prev?.title || '',
      position: prev?.videoId === (video?.id || video?.url) ? prev?.position || 0 : 0,
      updatedAt: new Date().toISOString(),
    }));
  }, []);

  const setQuizSession = useCallback((quizData) => {
    setActiveQuiz(quizData);
  }, []);

  const clearQuizSession = useCallback(() => {
    setActiveQuiz(null);
  }, []);

  const value = {
    videoPositions,
    saveVideoPosition,
    getVideoPosition,
    activeSession,
    updateActiveSession,
    activeQuiz,
    setQuizSession,
    clearQuizSession,
    learningHours,
    formattedLearningTime,
    flushHeartbeat,
  };

  return <LearningContext.Provider value={value}>{children}</LearningContext.Provider>;
}

export function useLearning() {
  const context = useContext(LearningContext);
  if (!context) {
    throw new Error('useLearning must be used within a LearningProvider');
  }
  return context;
}

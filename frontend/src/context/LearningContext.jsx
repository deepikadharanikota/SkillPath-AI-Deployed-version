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

import React, { useState, useEffect, useRef } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { 
  Play, 
  CheckCircle2, 
  Lock, 
  Sparkles, 
  RefreshCw, 
  AlertCircle, 
  ArrowRight,
  ArrowLeft,
  Tv,
  Clock,
  Eye,
  Check,
  Code2,
  ChevronRight,
  ChevronLeft,
  SkipForward
} from 'lucide-react';
import { api } from '../api';
import { useLearning } from '../context/LearningContext';

const DEFAULT_MODULES = [
  { key: 'intro', fallbackLabel: '1. Fundamentals', icon: '🌱' },
  { key: 'core', fallbackLabel: '2. Core Concepts', icon: '🔥' },
  { key: 'advanced', fallbackLabel: '3. Advanced Concepts', icon: '⚡' },
  { key: 'summary', fallbackLabel: '4. Integration & Review', icon: '🎓' }
];

const DSA_MODULES = [
  { key: 'module_1', fallbackLabel: 'M1. Complexity Analysis', phase: 'Phase 1: Fundamentals', icon: '⏱️' },
  { key: 'module_2', fallbackLabel: 'M2. Arrays', phase: 'Phase 1: Fundamentals', icon: '📊' },
  { key: 'module_3', fallbackLabel: 'M3. Strings', phase: 'Phase 1: Fundamentals', icon: '🔤' },
  { key: 'module_4', fallbackLabel: 'M4. Linked Lists', phase: 'Phase 2: Linear Structures', icon: '🔗' },
  { key: 'module_5', fallbackLabel: 'M5. Stacks', phase: 'Phase 2: Linear Structures', icon: '🥞' },
  { key: 'module_6', fallbackLabel: 'M6. Queues', phase: 'Phase 2: Linear Structures', icon: '🚶' },
  { key: 'module_7', fallbackLabel: 'M7. Trees & BST', phase: 'Phase 3: Non-Linear Structures', icon: '🌳' },
  { key: 'module_8', fallbackLabel: 'M8. Heaps & Priority Queues', phase: 'Phase 3: Non-Linear Structures', icon: '⛰️' },
  { key: 'module_9', fallbackLabel: 'M9. Graphs', phase: 'Phase 3: Non-Linear Structures', icon: '🕸️' },
  { key: 'module_10', fallbackLabel: 'M10. Recursion & Backtracking', phase: 'Phase 4: Algorithmic Techniques', icon: '🔄' },
  { key: 'module_11', fallbackLabel: 'M11. Searching & Sorting', phase: 'Phase 4: Algorithmic Techniques', icon: '🔍' },
  { key: 'module_12', fallbackLabel: 'M12. Greedy Algorithms', phase: 'Phase 4: Algorithmic Techniques', icon: '💡' },
  { key: 'module_13', fallbackLabel: 'M13. Dynamic Programming', phase: 'Phase 4: Algorithmic Techniques', icon: '🧩' },
  { key: 'module_14', fallbackLabel: 'M14. Advanced & Interviews', phase: 'Phase 5: Advanced & Interviews', icon: '🏆' }
];

const DSA_ALIASES = {
  intro: 'module_1',
  core: 'module_2',
  advanced: 'module_8',
  summary: 'module_14'
};

export default function LearningView() {
  const { topicId } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const { saveVideoPosition, getVideoPosition, updateActiveSession } = useLearning();

  const currentTopic = decodeURIComponent(topicId || 'Machine Learning');
  const isDsa = currentTopic.toLowerCase().includes('data structure') || currentTopic.toLowerCase() === 'dsa';
  const rawModule = searchParams.get('module') || (isDsa ? 'module_1' : 'intro');
  const effectiveModule = isDsa ? (DSA_ALIASES[rawModule] || rawModule) : rawModule;

  const [videoData, setVideoData] = useState(null);
  const [activeVideo, setActiveVideo] = useState(null);
  const [completingVideoId, setCompletingVideoId] = useState(null);
  const [resumeSeconds, setResumeSeconds] = useState(0);
  const [updatingLang, setUpdatingLang] = useState(false);
  const [phase0Open, setPhase0Open] = useState(false);
  const [phase0Checked, setPhase0Checked] = useState({});
  const [phase0Data, setPhase0Data] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isNavigatingModule, setIsNavigatingModule] = useState(false);
  const [error, setError] = useState('');
  const [findingAlternative, setFindingAlternative] = useState(false);
  const [replacementNotice, setReplacementNotice] = useState('');

  // Cache videoData by topic in ref to avoid full reload on module switch
  const cachedVideoDataRef = useRef({});

  const loadVideosForTopic = async (topic, mod, isTopicSwitch = false) => {
    // Check if we already have video data cached for this topic
    if (!isTopicSwitch && cachedVideoDataRef.current[topic]) {
      const cached = cachedVideoDataRef.current[topic];
      setVideoData(cached);
      selectActiveVideo(cached, mod);
      setLoading(false);
      // Background sync navigation state
      api.navigateTopic(topic, mod).catch(() => {});
      return;
    }

    if (isTopicSwitch || !videoData) {
      setLoading(true);
    }
    setError('');

    try {
      // 1. Switch server state asynchronously
      api.navigateTopic(topic, mod).catch(() => {});

      // 2. Fetch videos & gating status
      const data = await api.getVideos(topic, mod);
      cachedVideoDataRef.current[topic] = data;
      setVideoData(data);

      if (isDsa) {
        if (data.dsa_phase0) {
          setPhase0Data(data.dsa_phase0);
          const saved = localStorage.getItem(`skillpath_phase0_${data.dsa_lang_code || 'python'}`);
          if (saved) {
            try { setPhase0Checked(JSON.parse(saved)); } catch {}
          }
        } else {
          try {
            const p0 = await api.getDsaPhase0();
            setPhase0Data(p0?.phase0);
            const saved = localStorage.getItem(`skillpath_phase0_${p0?.dsa_lang_code || 'python'}`);
            if (saved) {
              try { setPhase0Checked(JSON.parse(saved)); } catch {}
            }
          } catch {}
        }
      }

      selectActiveVideo(data, mod);
    } catch (err) {
      console.error('Failed to load videos:', err);
      setError(err.message || 'Error loading course videos');
    } finally {
      setLoading(false);
      setIsNavigatingModule(false);
    }
  };

  const selectActiveVideo = (data, mod) => {
    const targetVideoParam = searchParams.get('video');
    const targetTimeParam = parseFloat(searchParams.get('t') || '0');

    const modVids = (data.videos || []).filter(v => v.module === mod);
    let matchedVideo = null;
    let startPos = 0;

    if (targetVideoParam) {
      matchedVideo = (data.videos || []).find(v => (v.id === targetVideoParam || v.url === targetVideoParam || v.url?.includes(targetVideoParam)));
      startPos = targetTimeParam;
    } else if (data.last_video_id) {
      matchedVideo = (data.videos || []).find(v => (v.id === data.last_video_id || v.url === data.last_video_id || v.url?.includes(data.last_video_id)));
      startPos = parseFloat(data.last_video_position_seconds || 0);
    }

    if (!matchedVideo) {
      matchedVideo = modVids.find(v => v.recommended) || modVids[0] || (data.videos || [])[0];
    }

    // Check if learning context has a saved position for this video
    if (matchedVideo) {
      const vidKey = matchedVideo.id || matchedVideo.url;
      const localSavedPos = getVideoPosition(vidKey);
      if (localSavedPos > 0 && startPos === 0) {
        startPos = localSavedPos;
      }
    }

    setActiveVideo(matchedVideo);
    setResumeSeconds(startPos);

    if (matchedVideo) {
      updateActiveSession(currentTopic, mod, matchedVideo);
      saveVideoPosition(
        matchedVideo.id || matchedVideo.url,
        startPos,
        currentTopic,
        mod,
        matchedVideo.title
      );
    }
  };

  useEffect(() => {
    const isTopicChanged = !cachedVideoDataRef.current[currentTopic];
    loadVideosForTopic(currentTopic, effectiveModule, isTopicChanged);
  }, [currentTopic]);

  // Instant Module Navigation without remounting or full reload
  const handleModuleChange = (modKey) => {
    if (modKey === effectiveModule) return;
    setIsNavigatingModule(true);
    setSearchParams({ module: modKey }, { replace: true });

    // If we already have the videos for this topic, switch instantly (0ms latency!)
    if (videoData && videoData.videos) {
      const modVids = (videoData.videos || []).filter(v => v.module === modKey);
      const nextActive = modVids.find(v => v.recommended) || modVids[0];
      if (nextActive) {
        const vidKey = nextActive.id || nextActive.url;
        const pos = getVideoPosition(vidKey);
        setActiveVideo(nextActive);
        setResumeSeconds(pos);
        updateActiveSession(currentTopic, modKey, nextActive);
        saveVideoPosition(vidKey, pos, currentTopic, modKey, nextActive.title);
      }
      setIsNavigatingModule(false);
      // Background sync navigation to server
      api.navigateTopic(currentTopic, modKey).catch(() => {});
    } else {
      loadVideosForTopic(currentTopic, modKey, false);
    }
  };

  // Video Selection with exact playback position memory
  const handleSelectVideo = (video) => {
    if (!video) return;
    const vidKey = video.id || video.url;
    const rememberedPos = getVideoPosition(vidKey);

    setActiveVideo(video);
    setResumeSeconds(rememberedPos);
    setSearchParams({ module: effectiveModule, video: vidKey }, { replace: true });

    updateActiveSession(currentTopic, effectiveModule, video);
    saveVideoPosition(vidKey, rememberedPos, currentTopic, effectiveModule, video.title);
  };

  const currentModuleVideos = (videoData?.videos || []).filter(v => v.module === effectiveModule);
  const currentVideoIndex = currentModuleVideos.findIndex(v => 
    activeVideo && (activeVideo.id || activeVideo.url) === (v.id || v.url)
  );

  const hasNextVideo = currentVideoIndex >= 0 && currentVideoIndex < currentModuleVideos.length - 1;
  const hasPrevVideo = currentVideoIndex > 0;

  const handleNextVideo = () => {
    if (hasNextVideo) {
      handleSelectVideo(currentModuleVideos[currentVideoIndex + 1]);
    }
  };

  const handlePrevVideo = () => {
    if (hasPrevVideo) {
      handleSelectVideo(currentModuleVideos[currentVideoIndex - 1]);
    }
  };

  const handleMarkVideoCompleted = async (video) => {
    const videoId = video.id || video.url;
    setCompletingVideoId(videoId);
    try {
      const res = await api.completeVideo(currentTopic, effectiveModule, videoId);
      if (videoData) {
        const updatedVideos = (videoData.videos || []).map(v => {
          if ((v.id || v.url) === videoId) {
            return { ...v, is_completed: true };
          }
          return v;
        });
        const updatedData = {
          ...videoData,
          videos: updatedVideos,
          completed_count: res.completed_count,
          is_quiz_unlocked: res.is_quiz_unlocked,
          course_progress: res.course_progress || videoData.course_progress
        };
        setVideoData(updatedData);
        cachedVideoDataRef.current[currentTopic] = updatedData;
      }
    } catch (err) {
      console.error('Failed to complete video:', err);
    } finally {
      setCompletingVideoId(null);
    }
  };

  const handleFindAlternative = async (video) => {
    if (!video || findingAlternative) return;
    const vidId = video.id || video.url;
    setFindingAlternative(true);
    setReplacementNotice('This video is unavailable or restricted. Finding verified alternative for this topic...');
    try {
      const res = await api.reportVideoUnavailable(currentTopic, effectiveModule, vidId, 'User requested alternative video');
      if (res && res.success && res.replacement_video) {
        const newVid = res.replacement_video;
        const newId = newVid.url || newVid.id;

        // Update topic videos list in place without reload
        if (videoData && videoData.videos) {
          const updatedVideos = (videoData.videos || []).map(v => {
            if ((v.id || v.url) === vidId) {
              return {
                ...newVid,
                id: newId,
                module: effectiveModule,
                is_current_module: true,
                is_completed: false,
                recommended: true
              };
            }
            return v;
          });
          const updatedData = { ...videoData, videos: updatedVideos };
          setVideoData(updatedData);
          cachedVideoDataRef.current[currentTopic] = updatedData;
        }

        // Set new active video
        setActiveVideo({
          ...newVid,
          id: newId,
          module: effectiveModule,
          is_current_module: true
        });
        setResumeSeconds(0);
        setSearchParams({ module: effectiveModule, video: newId }, { replace: true });
        updateActiveSession(currentTopic, effectiveModule, newVid);
        saveVideoPosition(newId, 0, currentTopic, effectiveModule, newVid.title);

        setReplacementNotice(`✓ Replaced with verified alternative: "${newVid.title}"`);
        setTimeout(() => setReplacementNotice(''), 6000);
      } else {
        setReplacementNotice('Searching alternative source... Please try again or select another module video.');
        setTimeout(() => setReplacementNotice(''), 5000);
      }
    } catch (err) {
      console.error('Failed to find alternative video:', err);
      setReplacementNotice('Error searching for replacement. Please choose another video from the playlist.');
      setTimeout(() => setReplacementNotice(''), 5000);
    } finally {
      setFindingAlternative(false);
    }
  };

  const handleSwitchDsaLanguage = async (newLang) => {
    const cur = (videoData?.dsa_language || videoData?.dsaLanguage || '').toLowerCase();
    const target = newLang.toLowerCase();
    if (updatingLang || cur === target || (target === 'c++' && cur === 'cpp') || (target === 'cpp' && cur === 'c++')) return;
    setUpdatingLang(true);
    try {
      await api.updateDsaLanguage(newLang);
      delete cachedVideoDataRef.current[currentTopic];
      await loadVideosForTopic(currentTopic, effectiveModule, true);
    } catch (err) {
      console.error('Failed to switch DSA language:', err);
    } finally {
      setUpdatingLang(false);
    }
  };

  const getEmbedUrl = (url, startSec = 0) => {
    if (!url) return '';
    let vidId = '';
    if (url.includes('v=')) {
      vidId = url.split('v=')[1]?.split('&')[0];
    } else if (url.includes('youtu.be/')) {
      vidId = url.split('youtu.be/')[1]?.split('?')[0];
    }
    if (!vidId) return '';
    let embed = `https://www.youtube.com/embed/${vidId}?autoplay=0`;
    if (startSec && startSec > 0) {
      embed += `&start=${Math.floor(startSec)}`;
    }
    return embed;
  };

  const isUnlocked = videoData?.is_quiz_unlocked;
  const completedCount = videoData?.completed_count || 0;
  const requiredCount = videoData?.required_count || 1;

  if (loading && !videoData) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', minHeight: '60vh', gap: '16px' }}>
        <RefreshCw size={36} color="#818cf8" style={{ animation: 'spin 1s linear infinite' }} />
        <span style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>Loading course content for {currentTopic}...</span>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      
      {/* Topic Header & Breadcrumbs */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <button 
              onClick={() => navigate('/learning')}
              style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.86rem', padding: 0 }}
            >
              Learning Center &gt;
            </button>
            <span style={{ fontSize: '0.86rem', color: '#818cf8', fontWeight: '600' }}>{currentTopic}</span>
          </div>
          <h1 style={{ fontSize: '2.2rem' }}>{currentTopic}</h1>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          {isDsa && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              backgroundColor: 'rgba(0, 0, 0, 0.35)',
              padding: '4px 8px',
              borderRadius: '10px',
              border: '1px solid rgba(255, 255, 255, 0.08)'
            }}>
              <Code2 size={14} color="#818cf8" />
              <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginRight: '4px' }}>Track Language:</span>
              {['C', 'C++', 'Python', 'Java'].map((lang) => {
                const currentLang = (videoData?.dsa_language || videoData?.dsaLanguage || 'C++').toLowerCase();
                const isActive = currentLang === lang.toLowerCase() ||
                  (lang === 'C++' && (currentLang === 'cpp' || currentLang === 'c++')) ||
                  (lang === 'C' && currentLang === 'c');
                return (
                  <button
                    key={lang}
                    onClick={() => handleSwitchDsaLanguage(lang)}
                    disabled={updatingLang}
                    style={{
                      padding: '3px 10px',
                      borderRadius: '6px',
                      fontSize: '0.78rem',
                      fontWeight: isActive ? '700' : '500',
                      backgroundColor: isActive ? 'rgba(99, 102, 241, 0.9)' : 'transparent',
                      color: isActive ? '#fff' : 'var(--text-muted)',
                      border: 'none',
                      cursor: updatingLang ? 'not-allowed' : 'pointer',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    {lang}
                  </button>
                );
              })}
            </div>
          )}
          <span className="badge badge-indigo" style={{ padding: '6px 14px', fontSize: '0.85rem' }}>
            Adapted Level: {videoData?.current_difficulty?.toUpperCase() || 'BEGINNER'}
          </span>
        </div>
      </div>

      {/* Course Progress Summary Bar */}
      {videoData?.course_progress && (
        <div className="glass-card" style={{
          padding: '14px 20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1.25rem',
          flexWrap: 'wrap',
          border: '1px solid rgba(99, 102, 241, 0.25)',
          background: 'rgba(99, 102, 241, 0.04)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontWeight: '600', fontSize: '0.95rem' }}>Course Progress:</span>
            <span style={{ color: '#818cf8', fontWeight: '700', fontSize: '1.1rem' }}>
              {videoData.course_progress.percentage}%
            </span>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-dim)' }}>
              ({videoData.course_progress.completed_modules} of {videoData.course_progress.total_modules || (isDsa ? 14 : 4)} Modules Completed)
            </span>
          </div>
          <div style={{ width: '240px' }} className="progress-track">
            <div 
              className={`progress-fill ${videoData.course_progress.is_completed ? 'progress-fill-emerald' : ''}`}
              style={{ width: `${videoData.course_progress.percentage}%` }} 
            />
          </div>
        </div>
      )}

      {/* ── Phase 0 Check (DSA Only) ── */}
      {isDsa && phase0Data && (
        <div className="glass-card" style={{
          padding: '1.25rem 1.5rem',
          border: '1px solid rgba(99, 102, 241, 0.25)',
          background: 'rgba(99, 102, 241, 0.03)',
          borderRadius: '14px'
        }}>
          <div 
            onClick={() => setPhase0Open(!phase0Open)}
            style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', flexWrap: 'wrap', gap: '8px' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '1.25rem' }}>🔰</span>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                  <h3 style={{ fontSize: '1.05rem', margin: 0, color: '#fff' }}>
                    Phase 0 — Programming-Language Foundation ({videoData?.dsa_language || 'C++'})
                  </h3>
                  <span className="badge badge-indigo" style={{ fontSize: '0.75rem', padding: '2px 8px' }}>
                    Prerequisite Check
                  </span>
                </div>
                <p style={{ margin: '2px 0 0', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  Verify core {videoData?.dsa_language || 'C++'} language syntax & constructs before continuing.
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{ fontSize: '0.82rem', color: '#818cf8', fontWeight: '600' }}>
                {Object.values(phase0Checked).filter(Boolean).length} / {phase0Data.topics?.length || 0} Confirmed
              </span>
              <button 
                type="button"
                onClick={(e) => { e.stopPropagation(); setPhase0Open(!phase0Open); }}
                style={{
                  background: 'rgba(255, 255, 255, 0.04)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px',
                  color: '#fff',
                  padding: '5px 12px',
                  fontSize: '0.8rem',
                  cursor: 'pointer'
                }}
              >
                {phase0Open ? 'Collapse ▲' : 'Review Checklist ▼'}
              </button>
            </div>
          </div>

          {phase0Open && (
            <div style={{ marginTop: '1.2rem', paddingTop: '1rem', borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '8px' }}>
                {(phase0Data.topics || []).map((topicItem, tIdx) => {
                  const isChecked = !!phase0Checked[topicItem];
                  return (
                    <label 
                      key={tIdx} 
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px',
                        padding: '8px 12px',
                        borderRadius: '8px',
                        background: isChecked ? 'rgba(16, 185, 129, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                        border: isChecked ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(255, 255, 255, 0.06)',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease'
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={(e) => {
                          const next = { ...phase0Checked, [topicItem]: e.target.checked };
                          setPhase0Checked(next);
                          localStorage.setItem(`skillpath_phase0_${videoData?.dsa_lang_code || 'python'}`, JSON.stringify(next));
                        }}
                        style={{ accentColor: '#10b981', cursor: 'pointer' }}
                      />
                      <span style={{ fontSize: '0.85rem', color: isChecked ? '#fff' : 'var(--text-muted)', fontWeight: isChecked ? '600' : '400' }}>
                        {topicItem}
                      </span>
                    </label>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

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
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Module Tabs (Instant Switching) */}
      <div style={{
        display: 'flex',
        gap: '8px',
        borderBottom: '1px solid var(--border-color)',
        paddingBottom: '8px',
        overflowX: 'auto',
        scrollbarWidth: 'thin'
      }}>
        {(isDsa ? DSA_MODULES : DEFAULT_MODULES).map((m) => {
          const isActive = effectiveModule === m.key;
          const syllabusMod = videoData?.syllabus?.modules?.[m.key];
          const displayLabel = syllabusMod?.title || m.fallbackLabel;
          return (
            <button
              key={m.key}
              onClick={() => handleModuleChange(m.key)}
              style={{
                background: isActive ? 'linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(168, 85, 247, 0.25) 100%)' : 'transparent',
                border: isActive ? '1px solid rgba(99, 102, 241, 0.45)' : '1px solid rgba(255, 255, 255, 0.05)',
                borderRadius: '10px',
                padding: isDsa ? '8px 14px' : '10px 18px',
                color: isActive ? '#fff' : 'var(--text-muted)',
                fontWeight: isActive ? '700' : '500',
                fontSize: isDsa ? '0.84rem' : '0.92rem',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                whiteSpace: 'nowrap'
              }}
            >
              <span>{m.icon}</span>
              <span>{displayLabel}</span>
            </button>
          );
        })}
      </div>

      {/* ── Main Content Area: Player on Left, Video List on Right ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) 380px', gap: '1.75rem' }}>
        {/* Left Column: Active Video Player & Navigation Controls */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {activeVideo ? (
            <div className="glass-card" style={{ padding: '1.5rem' }}>
              {resumeSeconds > 0 && (
                <div style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  backgroundColor: 'rgba(99, 102, 241, 0.15)',
                  border: '1px solid rgba(99, 102, 241, 0.35)',
                  borderRadius: '20px',
                  padding: '4px 12px',
                  fontSize: '0.8rem',
                  color: '#c7d2fe',
                  marginBottom: '12px'
                }}>
                  <Play size={12} fill="#818cf8" color="#818cf8" />
                  <span>Resuming playback from <strong>{Math.floor(resumeSeconds / 60)}:{String(Math.floor(resumeSeconds % 60)).padStart(2, '0')}</strong></span>
                </div>
              )}

              {/* Embedded Player */}
              <div style={{
                position: 'relative',
                paddingBottom: '56.25%',
                height: 0,
                borderRadius: '14px',
                overflow: 'hidden',
                backgroundColor: '#000',
                marginBottom: '1rem'
              }}>
                {getEmbedUrl(activeVideo.url, resumeSeconds) ? (
                  <iframe
                    key={activeVideo.id || activeVideo.url}
                    src={getEmbedUrl(activeVideo.url, resumeSeconds)}
                    title={activeVideo.title}
                    style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 0 }}
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                  />
                ) : (
                  <div style={{ position: 'absolute', top: '45%', left: '35%', color: 'var(--text-muted)' }}>
                    Video stream available on YouTube
                  </div>
                )}
              </div>

              {/* Replacement Notification Banner */}
              {replacementNotice && (
                <div style={{
                  backgroundColor: replacementNotice.startsWith('✓') ? 'rgba(16, 185, 129, 0.12)' : 'rgba(99, 102, 241, 0.15)',
                  border: replacementNotice.startsWith('✓') ? '1px solid rgba(16, 185, 129, 0.35)' : '1px solid rgba(99, 102, 241, 0.4)',
                  color: replacementNotice.startsWith('✓') ? '#6ee7b7' : '#c7d2fe',
                  padding: '10px 16px',
                  borderRadius: '10px',
                  fontSize: '0.86rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  marginBottom: '12px'
                }}>
                  <Sparkles size={16} />
                  <span>{replacementNotice}</span>
                </div>
              )}

              {/* Video Title & Actions */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1rem' }}>
                <div style={{ flex: 1, minWidth: '240px' }}>
                  <h2 style={{ fontSize: '1.25rem', marginBottom: '6px' }}>{activeVideo.title}</h2>
                  <div style={{ display: 'flex', gap: '14px', fontSize: '0.84rem', color: 'var(--text-dim)', flexWrap: 'wrap', alignItems: 'center' }}>
                    <span>📺 {activeVideo.channel}</span>
                    <span>⏱ {activeVideo.duration}</span>
                    <span>👁 {activeVideo.views} views</span>
                    <span style={{ color: '#10b981', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <CheckCircle2 size={13} color="#10b981" /> Verified Available
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
                  {/* Find Alternative Video Button */}
                  <button
                    type="button"
                    onClick={() => handleFindAlternative(activeVideo)}
                    disabled={findingAlternative}
                    className="btn-secondary"
                    style={{
                      padding: '10px 14px',
                      fontSize: '0.85rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                      backgroundColor: 'rgba(239, 68, 68, 0.08)',
                      color: '#fca5a5'
                    }}
                    title="If this video is broken, deleted, or cannot be embedded, replace it with an alternative for this topic"
                  >
                    <RefreshCw size={14} style={{ animation: findingAlternative ? 'spin 1s linear infinite' : 'none' }} />
                    <span>{findingAlternative ? 'Finding Alternative...' : 'Video Broken? Replace'}</span>
                  </button>

                  {/* Mark as Watched Button */}
                  <button
                    onClick={() => handleMarkVideoCompleted(activeVideo)}
                    disabled={activeVideo.is_completed || completingVideoId === (activeVideo.id || activeVideo.url)}
                    className={activeVideo.is_completed ? 'btn-emerald' : 'btn-primary'}
                    style={{ padding: '10px 18px', fontSize: '0.9rem' }}
                  >
                    {activeVideo.is_completed ? (
                      <>
                        <CheckCircle2 size={16} />
                        <span>Watched & Completed</span>
                      </>
                    ) : (
                      <>
                        <Check size={16} />
                        <span>{completingVideoId === (activeVideo.id || activeVideo.url) ? 'Recording...' : 'Mark as Watched'}</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Video Navigation Bar (Prev / Next Video Fast Switching) */}
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                paddingTop: '1rem',
                borderTop: '1px solid rgba(255, 255, 255, 0.08)',
                gap: '12px'
              }}>
                <button
                  onClick={handlePrevVideo}
                  disabled={!hasPrevVideo}
                  className="btn-secondary"
                  style={{
                    padding: '8px 16px',
                    fontSize: '0.86rem',
                    opacity: hasPrevVideo ? 1 : 0.4,
                    cursor: hasPrevVideo ? 'pointer' : 'not-allowed'
                  }}
                >
                  <ChevronLeft size={16} />
                  <span>Previous Video</span>
                </button>

                <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
                  Video {currentVideoIndex + 1} of {currentModuleVideos.length}
                </span>

                {hasNextVideo ? (
                  <button
                    onClick={handleNextVideo}
                    className="btn-primary"
                    style={{ padding: '8px 18px', fontSize: '0.86rem' }}
                  >
                    <span>Next Video</span>
                    <ChevronRight size={16} />
                  </button>
                ) : isUnlocked ? (
                  <button
                    onClick={() => navigate(`/quiz/${encodeURIComponent(currentTopic)}?module=${encodeURIComponent(effectiveModule)}`)}
                    className="btn-emerald"
                    style={{ padding: '8px 18px', fontSize: '0.86rem' }}
                  >
                    <Sparkles size={15} />
                    <span>Proceed to Quiz</span>
                    <ArrowRight size={15} />
                  </button>
                ) : (
                  <button
                    disabled
                    className="btn-secondary"
                    style={{ padding: '8px 16px', fontSize: '0.86rem', opacity: 0.5 }}
                  >
                    <span>End of Module</span>
                  </button>
                )}
              </div>
            </div>
          ) : (
            <div className="glass-card" style={{ padding: '3rem', textAlign: 'center' }}>
              <Tv size={48} color="#9ca3af" style={{ margin: '0 auto 1rem' }} />
              <p style={{ color: 'var(--text-muted)' }}>No videos found for this module.</p>
            </div>
          )}

          {/* ── STRICT QUIZ GATING CARD ── */}
          <div className="glass-card" style={{
            padding: '2rem',
            border: isUnlocked 
              ? '1px solid rgba(16, 185, 129, 0.4)' 
              : '1px solid rgba(255, 255, 255, 0.08)',
            background: isUnlocked
              ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(6, 182, 212, 0.06) 100%)'
              : 'var(--bg-card)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  {isUnlocked ? (
                    <CheckCircle2 size={24} color="#10b981" />
                  ) : (
                    <Lock size={24} color="#f59e0b" />
                  )}
                  <h3 style={{ fontSize: '1.25rem' }}>
                    {isUnlocked ? '✓ Videos Completed — Quiz Unlocked!' : '🔒 Quiz Locked'}
                  </h3>
                </div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
                  {isUnlocked
                    ? `You have completed all required videos for this module. Challenge yourself with the 15-question adaptive quiz!`
                    : `Complete all required course videos (${completedCount}/${requiredCount} completed) to unlock the quiz.`}
                </p>
              </div>

              {/* Take Quiz Button */}
              {isUnlocked ? (
                <button
                  onClick={() => navigate(`/quiz/${encodeURIComponent(currentTopic)}?module=${encodeURIComponent(effectiveModule)}`)}
                  className="btn-emerald"
                  style={{ padding: '14px 28px', fontSize: '1rem', fontWeight: '700' }}
                >
                  <Sparkles size={18} />
                  <span>Start 15 Question Quiz</span>
                </button>
              ) : (
                <button
                  disabled
                  className="btn-primary"
                  style={{ opacity: 0.5, cursor: 'not-allowed', padding: '12px 24px' }}
                >
                  <Lock size={16} />
                  <span>Quiz Locked</span>
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Module Videos Playlist */}
        <div className="glass-card" style={{ padding: '1.5rem', height: 'fit-content' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1.05rem' }}>Module Videos</h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
              {completedCount}/{requiredCount} Watched
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {currentModuleVideos.map((video, idx) => {
              const isSelected = activeVideo && (activeVideo.id || activeVideo.url) === (video.id || video.url);
              return (
                <div
                  key={video.id || video.url || idx}
                  onClick={() => handleSelectVideo(video)}
                  style={{
                    display: 'flex',
                    gap: '12px',
                    padding: '10px',
                    borderRadius: '12px',
                    backgroundColor: isSelected ? 'rgba(99, 102, 241, 0.15)' : 'rgba(255, 255, 255, 0.02)',
                    border: isSelected ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid var(--border-color)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {/* Thumbnail */}
                  <div style={{
                    width: '100px',
                    height: '60px',
                    borderRadius: '8px',
                    overflow: 'hidden',
                    backgroundColor: '#000',
                    flexShrink: 0,
                    position: 'relative'
                  }}>
                    {video.thumb ? (
                      <img src={video.thumb} alt={video.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    ) : (
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                        <Play size={18} color="#fff" />
                      </div>
                    )}
                    {video.is_completed && (
                      <div style={{
                        position: 'absolute',
                        top: '4px',
                        right: '4px',
                        backgroundColor: '#10b981',
                        borderRadius: '50%',
                        padding: '2px'
                      }}>
                        <Check size={12} color="#fff" />
                      </div>
                    )}
                  </div>

                  {/* Metadata */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{
                      fontSize: '0.85rem',
                      fontWeight: '600',
                      color: isSelected ? '#fff' : 'var(--text-main)',
                      lineHeight: '1.3',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      marginBottom: '4px'
                    }}>
                      {video.title}
                    </div>
                    <div style={{ fontSize: '0.74rem', color: 'var(--text-dim)', display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
                      <span>⏱ {video.duration}</span>
                      <span style={{ color: '#10b981', display: 'flex', alignItems: 'center', gap: '2px', fontWeight: '500' }}>
                        <CheckCircle2 size={11} color="#10b981" /> Available
                      </span>
                      {video.recommended && (
                        <span style={{ backgroundColor: 'rgba(99, 102, 241, 0.2)', color: '#a5b4fc', padding: '1px 5px', borderRadius: '4px', fontSize: '0.68rem', fontWeight: '600' }}>
                          Recommended
                        </span>
                      )}
                      {video.is_completed && <span style={{ color: '#10b981', fontWeight: '600' }}>✓ Watched</span>}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

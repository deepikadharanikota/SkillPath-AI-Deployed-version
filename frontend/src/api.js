/**
 * api.js
 * Centralized API client for SkillPath AI Backend.
 */

// Configurable API base URL: prioritized VITE_API_URL, fallback to VITE_BACKEND_URL, or local dev port
export const API_URL = (
  import.meta.env.VITE_API_URL || 
  import.meta.env.VITE_BACKEND_URL || 
  (import.meta.env.DEV ? "http://localhost:8002" : "https://skillpath-ai-backend-wpr9.onrender.com")
).replace(/\/$/, "");

export const getToken = () => localStorage.getItem("skillpath_token") || "";
export const setToken = (t) => localStorage.setItem("skillpath_token", t);
export const removeToken = () => localStorage.removeItem("skillpath_token");

async function request(endpoint, options = {}) {
  const token = getToken();
  const headers = { ...(options.headers || {}) };

  if (token) {
    headers["token"] = token;
    if (!headers["Authorization"]) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  // If body is not FormData, add application/json Content-Type
  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(options.body);
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errMsg = "An error occurred";
    try {
      const errData = await response.json();
      errMsg = errData.detail || errData.message || JSON.stringify(errData);
    } catch {
      errMsg = await response.text();
    }
    const err = new Error(errMsg);
    err.status = response.status;
    throw err;
  }

  return response.json();
}

export const api = {
  // ── Auth ──
  login: (username, password) => request("/auth/local-login", { method: "POST", body: { username, password } }),
  register: (username, email, password, target_role) => request("/auth/register", { method: "POST", body: { username, email, password, target_role } }),
  me: () => request("/auth/me"),
  logout: async () => {
    try {
      await request("/auth/logout", { method: "POST" });
    } finally {
      removeToken();
    }
  },

  // ── Resume ──
  getResume: () => request("/resume"),
  getSkillGap: () => request("/resume/skill-gap"),
  uploadResumeFile: (formData) => request("/resume/upload", { method: "POST", body: formData }),
  updateTargetRole: (target_role) => request("/resume/target-role", { method: "PUT", body: { target_role } }),

  // ── Learning & Videos ──
  getState: () => request("/learning/state"),
  getLearningResume: () => request("/learning/resume"),
  saveLearningPosition: (topic, module, video_id, position_seconds, video_title = "") =>
    request("/learning/position", {
      method: "POST",
      body: { topic, module, video_id, position_seconds, video_title },
    }),
  sendTimeHeartbeat: (duration_seconds, topic = null, module = null, client_date = null, timezone = null) => {
    const tz = timezone || Intl.DateTimeFormat().resolvedOptions().timeZone;
    const now = new Date();
    const localDate = client_date || `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    return request("/learning/time-heartbeat", {
      method: "POST",
      body: {
        duration_seconds,
        topic,
        module,
        client_date: localDate,
        timezone: tz,
      },
    });
  },
  getVideos: (topic, module, difficulty) => {
    let url = `/learning/videos?topic=${encodeURIComponent(topic)}&module=${encodeURIComponent(module)}`;
    if (difficulty) url += `&difficulty=${encodeURIComponent(difficulty)}`;
    return request(url);
  },
  completeVideo: (topic, module, video_id) => request("/learning/video/complete", { method: "POST", body: { topic, module, video_id } }),
  reportVideoUnavailable: (topic, module, video_id, reason = "Playback error") =>
    request("/learning/video/report-unavailable", {
      method: "POST",
      body: { topic, module, video_id, reason },
    }),
  getCoverageReport: () => request("/learning/coverage-report"),
  navigateTopic: (topic, module = "intro") => request("/learning/navigate", { method: "POST", body: { topic, module } }),

  // ── Quiz ──
  generateQuiz: (topic, module, difficulty) => {
    let url = `/quiz/generate?topic=${encodeURIComponent(topic)}&module=${encodeURIComponent(module)}`;
    if (difficulty) url += `&difficulty=${encodeURIComponent(difficulty)}`;
    return request(url);
  },
  submitQuiz: (quiz_id, topic, module, answers) => request("/quiz/submit", { method: "POST", body: { quiz_id, topic, module, answers } }),
  getQuizResults: (quiz_id) => request(`/quiz/${quiz_id}/results`),
  getQuizHistory: () => request("/quiz/history"),

  // ── Learning ──
  updateDsaLanguage: (language) => request("/learning/dsa-language", { method: "PUT", body: { language } }),
  getDsaLanguage: () => request("/learning/dsa-language"),
  getDsaCurriculum: () => request("/learning/dsa-curriculum"),
  getDsaPhase0: () => request("/learning/dsa-phase0"),

  // ── Dashboard ──
  getDashboardSummary: () => request("/dashboard/summary"),
  getDashboardOverview: () => request("/dashboard/overview"),
  getDashboardSkills: () => request("/dashboard/skills"),
  getDashboardTimeline: () => request("/dashboard/activity"),
  getDashboardInsights: () => request("/dashboard/insights"),
  getDashboardRecommendations: () => request("/dashboard/recommendations"),
  getDashboardRoadmap: () => request("/dashboard/roadmap"),
  getQuizAnalysis: () => request("/dashboard/quiz-analysis"),

  // ── Catalog ──
  getRoles: () => request("/roles"),
};


import { create } from "zustand";

// ---------------------------------------------------------------------------
// Token helpers
// ---------------------------------------------------------------------------

function loadToken() {
  return localStorage.getItem("mh_token") || null;
}

function saveToken(token) {
  if (token) localStorage.setItem("mh_token", token);
  else localStorage.removeItem("mh_token");
}

function loadSessionId() {
  return localStorage.getItem("mh_active_session_id") || null;
}

function saveSessionId(sessionId) {
  if (sessionId) localStorage.setItem("mh_active_session_id", sessionId);
  else localStorage.removeItem("mh_active_session_id");
}

// ---------------------------------------------------------------------------
// Store
// ---------------------------------------------------------------------------

const useStore = create((set, get) => ({
  // ── Auth ──────────────────────────────────────────────────────────────────
  token: loadToken(),
  currentUser: null, // { id, username, email, display_name, created_at }
  authStatus: "idle", // "idle" | "loading" | "authenticated" | "unauthenticated"

  setAuth: ({ token, user }) => {
    saveToken(token);
    set({ token, currentUser: user, authStatus: "authenticated" });
  },

  logout: () => {
    saveToken(null);
    saveSessionId(null);
    set({
      token: null,
      currentUser: null,
      authStatus: "unauthenticated",
      sessionId: null,
      sessions: [],
      messages: [],
      streamingContent: "",
      isStreaming: false,
      isSending: false,
      showCrisisAlert: false,
      showMoodCheckin: false,
    });
  },

  setAuthStatus: (status) => set({ authStatus: status }),
  setCurrentUser: (user) => set({ currentUser: user }),

  // ── Sessions (history sidebar) ────────────────────────────────────────────
  sessions: [], // [{ session_id, title, created_at, updated_at }]
  setSessions: (sessions) => set({ sessions }),
  deleteSession: (sessionId) =>
    set((state) => ({
      sessions: state.sessions.filter((s) => s.session_id !== sessionId),
    })),

  // ── Chat ─────────────────────────────────────────────────────────────────
  sessionId: loadSessionId(),
  messages: [],
  streamingContent: "",
  isStreaming: false,
  isSending: false,
  isConnected: false,
  showCrisisAlert: false,
  crisisLines: [],
  userLocation: null,
  locationPermission: "idle",
  showSupportResources: false,
  showMoodCheckin: false,

  setSessionId: (id) => {
    saveSessionId(id);
    set({ sessionId: id });
  },
  setIsConnected: (val) => set({ isConnected: val }),

  addMessage: (msg) =>
    set((state) => ({
      messages: [...state.messages, { id: crypto.randomUUID(), ...msg }],
    })),

  appendStreamingToken: (token) =>
    set((state) => ({ streamingContent: state.streamingContent + token })),

  finalizeStreamingMessage: () => {
    const { streamingContent, messages } = get();
    set({
      messages: streamingContent
        ? [
            ...messages,
            {
              id: crypto.randomUUID(),
              role: "assistant",
              content: streamingContent,
            },
          ]
        : messages,
      streamingContent: "",
      isStreaming: false,
      isSending: false,
    });
  },

  clearStreamingContent: () => set({ streamingContent: "" }),
  setIsStreaming: (val) => set({ isStreaming: val }),
  setIsSending: (val) => set({ isSending: val }),
  setShowCrisisAlert: (val) => set({ showCrisisAlert: val }),
  setCrisisLines: (lines) => set({ crisisLines: lines }),
  setUserLocation: (coords) => set({ userLocation: coords }),
  setLocationPermission: (status) => set({ locationPermission: status }),
  setShowSupportResources: (val) => set({ showSupportResources: val }),
  setShowMoodCheckin: (val) => set({ showMoodCheckin: val }),

  resetChat: () =>
    set({
      messages: [],
      streamingContent: "",
      isStreaming: false,
      isSending: false,
      showCrisisAlert: false,
      showMoodCheckin: false,
    }),
}));

// Listen for the global auth-expired event fired by the API client
window.addEventListener("auth:expired", () => {
  useStore.getState().logout();
});

export default useStore;

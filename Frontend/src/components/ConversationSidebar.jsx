import { useEffect, useCallback, useState } from "react";
import {
  PlusIcon,
  MessageSquareIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  Trash2Icon,
} from "lucide-react";
import {
  listSessions,
  getHistory,
  createSession,
  deleteSession as deleteSessionApi,
} from "../api/chat";
import { ConfirmModal } from "./common/ConfirmModal";
import useStore from "../store";

function formatDate(iso) {
  const d = new Date(iso);
  const now = new Date();
  const diffMs = now - d;
  const diffDays = Math.floor(diffMs / 86400000);
  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return `${diffDays}d ago`;
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export function ConversationSidebar({ isOpen, onToggle, onClose }) {
  const sessions = useStore((s) => s.sessions);
  const setSessions = useStore((s) => s.setSessions);
  const deleteSessionFromStore = useStore((s) => s.deleteSession);
  const sessionId = useStore((s) => s.sessionId);
  const setSessionId = useStore((s) => s.setSessionId);
  const addMessage = useStore((s) => s.addMessage);
  const resetChat = useStore((s) => s.resetChat);

  const [pendingDeleteId, setPendingDeleteId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);
  const [deleteError, setDeleteError] = useState(null);

  const loadSessions = useCallback(async () => {
    try {
      const data = await listSessions();
      setSessions(data.sessions || []);
    } catch {
      // silently ignore
    }
  }, [setSessions]);

  // On mount: load sessions and resume the latest one (or create a new one if none exist).
  // The `cancelled` flag prevents React StrictMode's double-mount from firing two
  // createSession() calls simultaneously, which is what caused duplicate sessions.
  useEffect(() => {
    let cancelled = false;
    const init = async () => {
      try {
        const data = await listSessions();
        if (cancelled) return;
        const sessionList = data.sessions || [];
        setSessions(sessionList);
        // Only initialise a session if one isn't already active
        const activeSessionId = useStore.getState().sessionId;
        const activeSessionExists =
          activeSessionId &&
          sessionList.some((session) => session.session_id === activeSessionId);

        if (!activeSessionExists) {
          if (sessionList.length > 0) {
            // Resume the most-recent existing session instead of creating a new one
            setSessionId(sessionList[0].session_id);
          } else {
            // No sessions exist at all – create the first one
            const newSession = await createSession();
            if (!cancelled) setSessionId(newSession.session_id);
          }
        }
      } catch {
        // silently ignore
      }
    };
    init();
    return () => {
      cancelled = true;
    };
  }, [setSessions, setSessionId]); // Stable Zustand actions → runs exactly once on mount

  // Refresh the session list whenever the active session changes (new chat / switch).
  useEffect(() => {
    if (!sessionId) return;
    loadSessions();
  }, [sessionId, loadSessions]);

  useEffect(() => {
    if (!sessionId) return;
    let cancelled = false;

    const loadHistory = async () => {
      resetChat();
      try {
        const data = await getHistory(sessionId);
        if (cancelled) return;
        for (const msg of data.messages || []) {
          addMessage({
            id: msg.id,
            role: msg.role,
            content: msg.content,
            created_at: msg.created_at,
          });
        }
      } catch {
        if (!cancelled) resetChat();
      }
    };

    loadHistory();
    return () => {
      cancelled = true;
    };
  }, [sessionId, resetChat, addMessage]);

  const handleSelectSession = useCallback(
    (sid) => {
      if (sid === sessionId) return;
      resetChat();
      setSessionId(sid);
      onClose?.();
        // history fetch failed — start fresh in this session
    },
    [sessionId, resetChat, setSessionId, onClose],
  );

  const handleNewChat = useCallback(async () => {
    resetChat();
    try {
      const data = await createSession();
      setSessionId(data.session_id);
      await loadSessions();
      onClose?.();
    } catch {
      // ignore
    }
  }, [resetChat, setSessionId, loadSessions, onClose]);

  const handleDeleteClick = useCallback((e, sid) => {
    e.stopPropagation();
    setPendingDeleteId(sid);
  }, []);

  const handleDeleteConfirm = useCallback(async () => {
    const sid = pendingDeleteId;
    setPendingDeleteId(null);
    setDeletingId(sid);
    setDeleteError(null);
    try {
      await deleteSessionApi(sid);
      deleteSessionFromStore(sid);
      if (sid === sessionId) {
        const remainingSessions = useStore
          .getState()
          .sessions.filter((session) => session.session_id !== sid);
        resetChat();
        setSessionId(remainingSessions[0]?.session_id || null);
      }
    } catch (err) {
      setDeleteError(err.message || "Failed to delete session");
      setTimeout(() => setDeleteError(null), 4000);
    } finally {
      setDeletingId(null);
    }
  }, [
    pendingDeleteId,
    sessionId,
    deleteSessionFromStore,
    resetChat,
    setSessionId,
  ]);

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm md:hidden"
          onClick={onClose}
        />
      )}
      <div
        className={`fixed inset-y-0 left-0 z-50 flex w-[min(18rem,86vw)] flex-shrink-0 flex-col border-r border-zinc-800 bg-zinc-950 transition-transform duration-200 md:relative md:z-auto md:translate-x-0 md:transition-all ${
          isOpen ? "translate-x-0 md:w-56" : "-translate-x-full md:w-10"
        }`}
      >
      {/* Toggle button */}
      <button
        onClick={onToggle}
        className="flex items-center justify-center h-12 border-b border-zinc-800 text-zinc-500 hover:text-zinc-200 transition-colors flex-shrink-0"
        title={isOpen ? "Collapse sidebar" : "Expand sidebar"}
      >
        {isOpen ? (
          <ChevronLeftIcon size={15} />
        ) : (
          <ChevronRightIcon size={15} />
        )}
      </button>

      {isOpen && (
        <>
          {/* New chat button */}
          <button
            onClick={handleNewChat}
            className="flex items-center gap-2 mx-2 mt-3 mb-2 px-3 py-2 text-xs text-zinc-400 hover:text-zinc-100 border border-zinc-700 hover:border-zinc-500 rounded-lg transition-all hover:bg-zinc-800/50"
          >
            <PlusIcon size={13} />
            New Chat
          </button>

          <div className="flex-1 overflow-y-auto scrollbar-thin px-2 pb-4 space-y-0.5">
            {sessions.length === 0 && (
              <p className="text-zinc-700 text-xs text-center mt-6 px-2">
                No conversations yet
              </p>
            )}
            {sessions.map((s) => (
              <div
                key={s.session_id}
                className={`group relative flex items-center rounded-lg text-xs transition-all ${
                  s.session_id === sessionId
                    ? "bg-indigo-600/20 border border-indigo-500/30"
                    : "hover:bg-zinc-800/50"
                }`}
              >
                <button
                  onClick={() => handleSelectSession(s.session_id)}
                  className={`flex-1 min-w-0 text-left px-3 py-2 ${
                    s.session_id === sessionId
                      ? "text-indigo-300"
                      : "text-zinc-500 hover:text-zinc-200"
                  }`}
                >
                  <div className="flex items-start gap-1.5">
                    <MessageSquareIcon
                      size={11}
                      className="mt-0.5 flex-shrink-0"
                    />
                    <div className="min-w-0">
                      <p className="truncate font-medium">
                        {s.title || "Conversation"}
                      </p>
                      <p className="text-zinc-600 text-[10px] mt-0.5">
                        {formatDate(s.updated_at)}
                      </p>
                    </div>
                  </div>
                </button>
                <button
                  onClick={(e) => handleDeleteClick(e, s.session_id)}
                  disabled={deletingId === s.session_id}
                  title="Delete conversation"
                  className="flex-shrink-0 mr-1.5 p-1 rounded opacity-0 group-hover:opacity-100 text-zinc-600 hover:text-red-400 hover:bg-red-500/10 transition-all disabled:opacity-30"
                >
                  {deletingId === s.session_id ? (
                    <svg
                      className="animate-spin w-3 h-3"
                      viewBox="0 0 24 24"
                      fill="none"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8v8H4z"
                      />
                    </svg>
                  ) : (
                    <Trash2Icon size={11} />
                  )}
                </button>
              </div>
            ))}
            {deleteError && (
              <p className="text-red-400 text-[10px] text-center mt-2 px-2">
                {deleteError}
              </p>
            )}
          </div>
        </>
      )}

      <ConfirmModal
        isOpen={!!pendingDeleteId}
        title="Delete conversation?"
        message="This will permanently delete the conversation and all its messages. This action cannot be undone."
        onConfirm={handleDeleteConfirm}
        onCancel={() => setPendingDeleteId(null)}
        isLoading={false}
      />
      </div>
    </>
  );
}

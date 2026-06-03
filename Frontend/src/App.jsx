import { useEffect, useCallback, useState } from "react";
import { Header } from "./components/Header";
import { MessageList } from "./components/chat/MessageList";
import { ChatInput } from "./components/chat/ChatInput";
import { CrisisAlert } from "./components/common/CrisisAlert";
import { MoodCheckin } from "./components/common/MoodCheckin";
import { SupportResources } from "./components/common/SupportResources";
import { ConversationSidebar } from "./components/ConversationSidebar";
import { useWebSocket } from "./hooks/useWebSocket";
import { getCurrentUser } from "./api/auth";
import useStore from "./store";

function WelcomeScreen() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center overflow-y-auto px-4 py-8 text-center select-none sm:px-6">
      <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl border border-indigo-500/20 bg-indigo-600/10 sm:mb-6 sm:h-16 sm:w-16">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          className="w-7 h-7 text-indigo-400"
          stroke="currentColor"
          strokeWidth={1.5}
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
        </svg>
      </div>
      <h2 className="mb-3 text-lg font-semibold tracking-tight text-zinc-100 sm:text-xl">
        How are you feeling today?
      </h2>
      <p className="max-w-sm text-sm leading-relaxed text-zinc-500">
        I'm here to listen and support you. Share what's on your mind — this is
        a safe and confidential space.
      </p>
      <div className="mt-6 flex flex-wrap justify-center gap-2 sm:mt-8">
        {[
          "I'm feeling anxious",
          "I need someone to talk to",
          "I'm having a rough day",
        ].map((prompt) => (
          <span
            key={prompt}
            className="px-3 py-1.5 rounded-full border border-zinc-700/80 text-zinc-500 text-xs cursor-default"
          >
            {prompt}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function App() {
  const setAuth = useStore((s) => s.setAuth);
  const setCurrentUser = useStore((s) => s.setCurrentUser);
  const token = useStore((s) => s.token);
  const addMessage = useStore((s) => s.addMessage);
  const setIsSending = useStore((s) => s.setIsSending);
  const resetChat = useStore((s) => s.resetChat);
  const isEmpty = useStore(
    (s) => s.messages.length === 0 && !s.isStreaming && !s.isSending,
  );
  const showMoodCheckin = useStore((s) => s.showMoodCheckin);

  const [sidebarOpen, setSidebarOpen] = useState(() =>
    typeof window === "undefined"
      ? true
      : window.matchMedia("(min-width: 768px)").matches,
  );

  const { sendMessage } = useWebSocket();

  const closeSidebarOnMobile = useCallback(() => {
    if (window.matchMedia("(max-width: 767px)").matches) {
      setSidebarOpen(false);
    }
  }, []);

  useEffect(() => {
    const media = window.matchMedia("(min-width: 768px)");
    const handleChange = (event) => setSidebarOpen(event.matches);
    media.addEventListener("change", handleChange);
    return () => media.removeEventListener("change", handleChange);
  }, []);

  // Bootstrap: load current user profile if token exists
  useEffect(() => {
    if (!token) return;
    getCurrentUser()
      .then((user) => setCurrentUser(user))
      .catch(() => {
        // token invalid — the API client dispatches auth:expired which triggers logout
      });
  }, [token, setCurrentUser]);

  const handleSend = useCallback(
    (text) => {
      addMessage({ role: "user", content: text });
      setIsSending(true);
      sendMessage(text);
    },
    [addMessage, setIsSending, sendMessage],
  );

  return (
    <div className="flex h-dvh min-h-0 bg-zinc-950 overflow-hidden">
      {/* History sidebar */}
      <ConversationSidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen((o) => !o)}
        onClose={closeSidebarOnMobile}
      />

      {/* Main chat area */}
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <Header onMenuClick={() => setSidebarOpen(true)} />
        {isEmpty ? <WelcomeScreen /> : <MessageList />}
        <CrisisAlert />
        <ChatInput onSend={handleSend} />
        <SupportResources />
        {showMoodCheckin && <MoodCheckin />}
      </div>
    </div>
  );
}

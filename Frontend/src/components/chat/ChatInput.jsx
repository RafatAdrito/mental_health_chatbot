import { useRef, useCallback } from "react";
import { SendHorizonalIcon } from "lucide-react";
import useStore from "../../store";

export function ChatInput({ onSend }) {
  const isSending = useStore((s) => s.isSending);
  const isStreaming = useStore((s) => s.isStreaming);
  const isConnected = useStore((s) => s.isConnected);
  const textareaRef = useRef(null);

  const disabled = isSending || isStreaming || !isConnected;

  const submit = useCallback(() => {
    const text = textareaRef.current?.value.trim();
    if (!text || disabled) return;
    onSend(text);
    if (textareaRef.current) {
      textareaRef.current.value = "";
      textareaRef.current.style.height = "auto";
    }
  }, [disabled, onSend]);

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        submit();
      }
    },
    [submit],
  );

  const handleInput = useCallback(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 168) + "px";
  }, []);

  const statusText = !isConnected
    ? "Connecting to server..."
    : isSending || isStreaming
      ? "MindfulChat is responding..."
      : null;

  return (
    <div className="flex-shrink-0 px-3 pb-[calc(1rem+env(safe-area-inset-bottom))] pt-2 sm:px-4 sm:pb-5">
      <div className="max-w-3xl mx-auto space-y-2">
        <div
          className={`flex items-end gap-2 rounded-2xl border px-3 py-2.5 transition-all duration-150 sm:gap-3 sm:px-4 sm:py-3 ${
            disabled
              ? "border-zinc-800 bg-zinc-900/40"
              : "border-zinc-700/80 bg-zinc-900 hover:border-zinc-600 focus-within:border-indigo-500/60"
          }`}
        >
          <textarea
            ref={textareaRef}
            rows={1}
            placeholder={
              isConnected ? "Share what's on your mind..." : "Connecting..."
            }
            disabled={disabled}
            onKeyDown={handleKeyDown}
            onInput={handleInput}
            className="min-w-0 flex-1 resize-none overflow-y-auto bg-transparent text-sm leading-relaxed text-zinc-100 outline-none scrollbar-thin placeholder-zinc-500 disabled:opacity-40"
            style={{ minHeight: "24px", maxHeight: "168px" }}
          />
          <button
            onClick={submit}
            disabled={disabled}
            className="flex items-center justify-center w-8 h-8 rounded-xl bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 disabled:bg-zinc-700 disabled:opacity-40 transition-colors flex-shrink-0 mb-px"
          >
            <SendHorizonalIcon size={14} className="text-white" />
          </button>
        </div>

        <p className="px-2 text-center text-xs leading-relaxed text-zinc-600">
          {statusText ??
            "MindfulChat may make mistakes. In an emergency, please contact a crisis line."}
        </p>
      </div>
    </div>
  );
}

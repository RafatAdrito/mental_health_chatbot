import { useEffect, useRef } from "react";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";
import useStore from "../../store";

export function MessageList() {
  const messages = useStore((s) => s.messages);
  const streamingContent = useStore((s) => s.streamingContent);
  const isStreaming = useStore((s) => s.isStreaming);
  const isSending = useStore((s) => s.isSending);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent, isSending]);

  const showTypingIndicator = isSending && !isStreaming;

  return (
    <div className="flex-1 overflow-y-auto scrollbar-thin">
      <div className="mx-auto max-w-3xl px-3 py-4 sm:px-4 sm:py-6">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} role={msg.role} content={msg.content} />
        ))}
        {streamingContent && (
          <MessageBubble
            role="assistant"
            content={streamingContent}
            isStreaming
          />
        )}
        {showTypingIndicator && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}

import Markdown from "react-markdown";

function UserBubble({ content }) {
  return (
    <div className="flex justify-end mb-4 px-0.5 sm:mb-5 sm:px-1">
      <div className="max-w-[92%] break-words rounded-2xl rounded-tr-sm bg-indigo-600 px-3.5 py-2.5 text-sm leading-relaxed text-white whitespace-pre-wrap sm:max-w-[78%] sm:px-4 sm:py-3">
        {content}
      </div>
    </div>
  );
}

function AssistantBubble({ content, isStreaming }) {
  return (
    <div className="flex justify-start mb-4 px-0.5 sm:mb-5 sm:px-1">
      <div className="max-w-[94%] break-words rounded-2xl rounded-tl-sm bg-zinc-800/80 px-3.5 py-2.5 text-sm leading-relaxed text-zinc-100 sm:max-w-[82%] sm:px-4 sm:py-3">
        <div className="markdown-content">
          <Markdown>{content}</Markdown>
        </div>
        {isStreaming && (
          <span className="inline-block w-0.5 h-4 ml-0.5 bg-indigo-400 cursor-blink rounded-sm align-text-bottom" />
        )}
      </div>
    </div>
  );
}

export function MessageBubble({ role, content, isStreaming = false }) {
  if (role === "user") {
    return <UserBubble content={content} />;
  }
  return <AssistantBubble content={content} isStreaming={isStreaming} />;
}

export function TypingIndicator() {
  return (
    <div className="flex justify-start mb-4 px-1">
      <div className="px-4 py-3.5 rounded-2xl rounded-tl-sm bg-zinc-800/80 flex items-center gap-1.5">
        <span
          className="w-2 h-2 rounded-full bg-zinc-500 animate-bounce"
          style={{ animationDelay: "0ms", animationDuration: "1.1s" }}
        />
        <span
          className="w-2 h-2 rounded-full bg-zinc-500 animate-bounce"
          style={{ animationDelay: "180ms", animationDuration: "1.1s" }}
        />
        <span
          className="w-2 h-2 rounded-full bg-zinc-500 animate-bounce"
          style={{ animationDelay: "360ms", animationDuration: "1.1s" }}
        />
      </div>
    </div>
  );
}

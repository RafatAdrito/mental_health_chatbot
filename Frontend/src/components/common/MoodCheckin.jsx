import { useState } from "react";
import { XIcon, SmileIcon } from "lucide-react";
import { createMoodEntry } from "../../api/mood";
import useStore from "../../store";

const MOOD_LABELS = [
  "Anxious",
  "Depressed",
  "Stressed",
  "Angry",
  "Hopeless",
  "Sad",
  "Overwhelmed",
  "Okay",
  "Calm",
  "Happy",
];

function scoreClass(n, selected) {
  const palette =
    n <= 2
      ? {
          border: "border-red-600",
          bg: "bg-red-900/50",
          text: "text-red-300",
          ring: "ring-red-600/50",
        }
      : n <= 4
        ? {
            border: "border-orange-600",
            bg: "bg-orange-900/50",
            text: "text-orange-300",
            ring: "ring-orange-600/50",
          }
        : n <= 6
          ? {
              border: "border-yellow-600",
              bg: "bg-yellow-900/50",
              text: "text-yellow-300",
              ring: "ring-yellow-600/50",
            }
          : n <= 8
            ? {
                border: "border-lime-600",
                bg: "bg-lime-900/50",
                text: "text-lime-300",
                ring: "ring-lime-600/50",
              }
            : {
                border: "border-emerald-600",
                bg: "bg-emerald-900/50",
                text: "text-emerald-300",
                ring: "ring-emerald-600/50",
              };

  if (selected) {
    return `${palette.border} ${palette.bg} ${palette.text} ring-1 ${palette.ring} ring-offset-1 ring-offset-zinc-900`;
  }
  return "border-zinc-700 bg-zinc-800/50 text-zinc-500 hover:border-zinc-500 hover:text-zinc-300";
}

export function MoodCheckin() {
  const userId = useStore((s) => s.userId);
  const sessionId = useStore((s) => s.sessionId);
  const setShowMoodCheckin = useStore((s) => s.setShowMoodCheckin);

  const [score, setScore] = useState(null);
  const [label, setLabel] = useState("");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [submitted, setSubmitted] = useState(false);

  const canSubmit = score !== null && label !== "" && !submitting;

  const handleSubmit = async () => {
    if (!canSubmit) return;
    setSubmitting(true);
    setError(null);
    try {
      await createMoodEntry({
        userId,
        sessionId,
        moodScore: score,
        moodLabel: label,
        notes: notes.trim() || null,
      });
      setSubmitted(true);
      setTimeout(() => setShowMoodCheckin(false), 1500);
    } catch {
      setError("Could not save mood. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-3 backdrop-blur-sm sm:p-4">
      <div className="max-h-[calc(100dvh-1.5rem)] w-full max-w-sm overflow-y-auto rounded-2xl border border-zinc-700/80 bg-zinc-900 shadow-2xl scrollbar-thin">
        <div className="flex items-center justify-between border-b border-zinc-800 px-4 py-4 sm:px-5">
          <div className="flex items-center gap-2">
            <SmileIcon size={15} className="text-indigo-400" />
            <span className="text-zinc-100 font-semibold text-sm">
              How are you feeling?
            </span>
          </div>
          <button
            onClick={() => setShowMoodCheckin(false)}
            className="text-zinc-500 hover:text-zinc-200 transition-colors"
          >
            <XIcon size={16} />
          </button>
        </div>

        {submitted ? (
          <div className="px-4 py-10 text-center sm:px-5">
            <p className="text-emerald-400 font-medium text-sm">
              Mood logged ✓
            </p>
          </div>
        ) : (
          <div className="space-y-5 px-4 py-5 sm:px-5">
            <div>
              <p className="text-zinc-500 text-xs mb-3">
                Rate your mood (1 = very low, 10 = great)
              </p>
              <div className="grid grid-cols-5 gap-1 sm:grid-cols-10">
                {Array.from({ length: 10 }, (_, i) => i + 1).map((n) => (
                  <button
                    key={n}
                    onClick={() => setScore(n)}
                    className={`h-9 rounded-lg border text-xs font-semibold transition-all sm:h-8 ${scoreClass(n, score === n)}`}
                  >
                    {n}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <p className="text-zinc-500 text-xs mb-3">
                What best describes it?
              </p>
              <div className="flex flex-wrap gap-2">
                {MOOD_LABELS.map((l) => (
                  <button
                    key={l}
                    onClick={() => setLabel(l)}
                    className={`px-3 py-1.5 rounded-full text-xs border transition-all ${
                      label === l
                        ? "border-indigo-500 bg-indigo-600/20 text-indigo-300"
                        : "border-zinc-700 text-zinc-500 hover:border-zinc-500 hover:text-zinc-300"
                    }`}
                  >
                    {l}
                  </button>
                ))}
              </div>
            </div>

            <textarea
              placeholder="Any additional notes? (optional)"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              maxLength={500}
              rows={2}
              className="w-full bg-zinc-800/60 border border-zinc-700 rounded-xl px-3 py-2.5 text-zinc-100 placeholder-zinc-600 text-xs resize-none outline-none focus:border-indigo-500/60 transition-colors"
            />

            {error && <p className="text-red-400 text-xs">{error}</p>}

            <div className="flex flex-col gap-2 min-[360px]:flex-row">
              <button
                onClick={() => setShowMoodCheckin(false)}
                className="flex-1 py-2.5 text-xs text-zinc-500 hover:text-zinc-300 border border-zinc-700 hover:border-zinc-500 rounded-xl transition-all"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                disabled={!canSubmit}
                className="flex-1 py-2.5 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 disabled:bg-zinc-700 disabled:text-zinc-500 text-white rounded-xl transition-all"
              >
                {submitting ? "Saving..." : "Log Mood"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

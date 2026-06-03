import { useEffect, useState } from "react";
import { XIcon, PhoneIcon, AlertTriangleIcon } from "lucide-react";
import { getCrisisLines } from "../../api/resources";
import useStore from "../../store";

export function CrisisAlert() {
  const showCrisisAlert = useStore((s) => s.showCrisisAlert);
  const crisisLines = useStore((s) => s.crisisLines);
  const setCrisisLines = useStore((s) => s.setCrisisLines);
  const setShowCrisisAlert = useStore((s) => s.setShowCrisisAlert);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (showCrisisAlert && crisisLines.length === 0 && !loading) {
      setLoading(true);
      getCrisisLines()
        .then((data) => setCrisisLines(data.crisis_lines || []))
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [showCrisisAlert]);

  if (!showCrisisAlert) return null;

  return (
    <div className="flex-shrink-0 px-3 py-2 sm:px-4">
      <div className="max-w-3xl mx-auto">
        <div className="rounded-xl border border-red-800/50 bg-red-950/30 p-3 sm:p-4">
          <div className="flex items-start gap-2.5 sm:gap-3">
            <AlertTriangleIcon
              size={16}
              className="text-red-400 flex-shrink-0 mt-0.5"
            />
            <div className="flex-1 min-w-0">
              <p className="text-red-300 font-semibold text-sm mb-2.5">
                If you're in crisis, please reach out for support:
              </p>
              {loading ? (
                <p className="text-red-300/50 text-xs">
                  Loading crisis lines...
                </p>
              ) : crisisLines.length > 0 ? (
                <ul className="space-y-2">
                  {crisisLines.map((line, i) => (
                    <li
                      key={i}
                      className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5 text-xs"
                    >
                      <PhoneIcon
                        size={10}
                        className="text-red-400 flex-shrink-0 translate-y-px"
                      />
                      <span className="text-red-200 font-medium">
                        {line.name}
                      </span>
                      <span className="text-red-300">{line.contact}</span>
                      {line.available && (
                        <span className="text-red-400/60">
                          {line.available}
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-red-300 text-xs">
                  Please contact emergency services or a trusted person
                  immediately.
                </p>
              )}
            </div>
            <button
              onClick={() => setShowCrisisAlert(false)}
              className="text-red-400/70 hover:text-red-200 transition-colors flex-shrink-0"
            >
              <XIcon size={15} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

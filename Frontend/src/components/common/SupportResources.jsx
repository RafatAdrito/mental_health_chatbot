import { useEffect, useState } from "react";
import { LifeBuoyIcon, XIcon, PhoneIcon, ChevronDownIcon } from "lucide-react";
import { getCrisisLines } from "../../api/resources";
import { NearbyResourceFinder } from "./NearbyResourceFinder";
import useStore from "../../store";

export function SupportResources() {
  const showSupportResources = useStore((s) => s.showSupportResources);
  const setShowSupportResources = useStore((s) => s.setShowSupportResources);
  const crisisLines = useStore((s) => s.crisisLines);
  const setCrisisLines = useStore((s) => s.setCrisisLines);

  const [loadingLines, setLoadingLines] = useState(false);
  const [showNearby, setShowNearby] = useState(false);

  useEffect(() => {
    if (showSupportResources && crisisLines.length === 0 && !loadingLines) {
      setLoadingLines(true);
      getCrisisLines()
        .then((data) => setCrisisLines(data.crisis_lines || []))
        .catch(() => {})
        .finally(() => setLoadingLines(false));
    }
  }, [showSupportResources]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <>
      {/* Persistent floating help button */}
      <button
        onClick={() => setShowSupportResources(true)}
        aria-label="Open support resources"
        className="fixed right-3 bottom-[calc(5.75rem+env(safe-area-inset-bottom))] z-30 flex h-11 w-11 items-center justify-center rounded-full bg-indigo-600 shadow-lg shadow-indigo-900/50 transition-all duration-150 hover:bg-indigo-500 active:scale-95 active:bg-indigo-700 sm:right-4 sm:bottom-24"
      >
        <LifeBuoyIcon size={18} className="text-white" />
      </button>

      {/* Support panel overlay */}
      {showSupportResources && (
        <div className="fixed inset-0 z-50 flex items-end justify-center p-3 sm:items-center sm:p-4">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setShowSupportResources(false)}
          />

          {/* Panel */}
          <div className="relative flex max-h-[calc(100dvh-1.5rem)] w-full max-w-sm flex-col overflow-hidden rounded-2xl border border-zinc-700/80 bg-zinc-900 shadow-2xl sm:max-h-[85vh]">
            <div className="flex flex-shrink-0 items-center justify-between border-b border-zinc-800 px-4 py-4 sm:px-5">
              <div className="flex items-center gap-2">
                <LifeBuoyIcon size={15} className="text-indigo-400" />
                <span className="text-zinc-100 font-semibold text-sm">
                  Support Resources
                </span>
              </div>
              <button
                onClick={() => setShowSupportResources(false)}
                className="text-zinc-500 hover:text-zinc-200 transition-colors"
              >
                <XIcon size={16} />
              </button>
            </div>

            <div className="flex-1 space-y-6 overflow-y-auto p-4 scrollbar-thin sm:p-5">
              {/* Crisis helplines — always shown */}
              <div>
                <p className="text-zinc-500 text-xs font-semibold uppercase tracking-wider mb-3">
                  Crisis Helplines
                </p>
                {loadingLines ? (
                  <p className="text-zinc-600 text-xs">Loading...</p>
                ) : crisisLines.length > 0 ? (
                  <ul className="space-y-3">
                    {crisisLines.map((line, i) => (
                      <li
                        key={i}
                        className="rounded-xl border border-zinc-700/60 bg-zinc-800/40 px-4 py-3 space-y-1"
                      >
                        <div className="flex items-center gap-2">
                          <PhoneIcon
                            size={11}
                            className="text-indigo-400 flex-shrink-0"
                          />
                          <span className="text-zinc-200 text-xs font-semibold">
                            {line.name}
                          </span>
                        </div>
                        <p className="text-indigo-300 text-xs pl-4">
                          {line.contact}
                        </p>
                        <p className="text-zinc-500 text-xs pl-4 leading-relaxed">
                          {line.description}
                        </p>
                        {line.available && (
                          <p className="text-zinc-600 text-xs pl-4">
                            Available: {line.available}
                          </p>
                        )}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-zinc-500 text-xs">
                    Please contact emergency services or a trusted person if you
                    are in crisis.
                  </p>
                )}
              </div>

              {/* Nearby resources — collapsible */}
              <div>
                <button
                  onClick={() => setShowNearby((v) => !v)}
                  className="flex items-center gap-2 w-full text-left mb-3"
                >
                  <p className="text-zinc-500 text-xs font-semibold uppercase tracking-wider flex-1">
                    Nearby Resources
                  </p>
                  <ChevronDownIcon
                    size={13}
                    className={`text-zinc-500 transition-transform duration-200 ${
                      showNearby ? "rotate-180" : ""
                    }`}
                  />
                </button>
                {showNearby && <NearbyResourceFinder />}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

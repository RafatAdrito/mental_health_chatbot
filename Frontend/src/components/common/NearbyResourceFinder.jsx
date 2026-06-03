import { useState } from "react";
import {
  MapPinIcon,
  PhoneIcon,
  ExternalLinkIcon,
  SearchIcon,
} from "lucide-react";
import { getNearbyResources } from "../../api/resources";
import { useGeolocation } from "../../hooks/useGeolocation";
import useStore from "../../store";

const TYPES = [
  { value: "hospital", label: "Hospital" },
  { value: "therapist", label: "Therapist" },
  { value: "clinic", label: "Clinic" },
];

export function NearbyResourceFinder() {
  const userLocation = useStore((s) => s.userLocation);
  const locationPermission = useStore((s) => s.locationPermission);
  const { requestLocation } = useGeolocation();

  const [type, setType] = useState("hospital");
  const [results, setResults] = useState(null);
  const [source, setSource] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!userLocation) return;
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const data = await getNearbyResources(
        userLocation.latitude,
        userLocation.longitude,
        type,
      );
      setResults(data.places || []);
      setSource(data.source);
    } catch (err) {
      const msg = err.message || "";
      if (msg.includes("outside Bangladesh")) {
        setError(
          "Nearby search is supported only within Bangladesh at this time.",
        );
      } else {
        setError("Could not load nearby resources. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      {!userLocation ? (
        <div className="rounded-xl border border-zinc-700/60 bg-zinc-800/40 px-4 py-4 space-y-3">
          <p className="text-zinc-400 text-xs leading-relaxed">
            {locationPermission === "denied"
              ? "Location access was denied. Enable it in your browser settings to find nearby facilities."
              : locationPermission === "unavailable"
                ? "Location is not supported by this browser."
                : "Share your location to find hospitals, therapists, and clinics near you."}
          </p>
          {locationPermission !== "denied" &&
            locationPermission !== "unavailable" && (
              <button
                onClick={requestLocation}
                className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-indigo-600/20 border border-indigo-500/40 text-indigo-300 text-xs hover:bg-indigo-600/30 transition-colors"
              >
                <MapPinIcon size={11} />
                Share Location
              </button>
            )}
        </div>
      ) : (
        <div className="space-y-3">
          <div className="flex flex-col gap-2 min-[360px]:flex-row">
            <div className="flex min-w-0 flex-1 overflow-hidden rounded-lg border border-zinc-700">
              {TYPES.map((t) => (
                <button
                  key={t.value}
                  onClick={() => {
                    setType(t.value);
                    setResults(null);
                    setError(null);
                  }}
                  className={`min-w-0 flex-1 px-1 py-1.5 text-xs transition-colors ${
                    type === t.value
                      ? "bg-indigo-600 text-white"
                      : "text-zinc-500 hover:text-zinc-300 bg-zinc-800/50"
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
            <button
              onClick={handleSearch}
              disabled={loading}
              className="flex flex-shrink-0 items-center justify-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs text-white transition-colors hover:bg-indigo-500 disabled:bg-zinc-700 disabled:opacity-60"
            >
              <SearchIcon size={11} />
              {loading ? "Searching..." : "Search"}
            </button>
          </div>

          {error && <p className="text-red-400 text-xs px-1">{error}</p>}

          {results && results.length === 0 && (
            <p className="text-zinc-500 text-xs px-1">
              No results found nearby. Try a different category.
            </p>
          )}

          {results && results.length > 0 && (
            <div className="space-y-2">
              {source === "mock" && (
                <p className="text-zinc-600 text-xs px-1">
                  Showing sample listings — live results unavailable.
                </p>
              )}
              {results.map((place, i) => (
                <div
                  key={i}
                  className="rounded-xl border border-zinc-700/60 bg-zinc-800/40 px-3 py-3 space-y-1"
                >
                  <p className="text-zinc-200 text-xs font-semibold">
                    {place.name}
                  </p>
                  <p className="text-zinc-500 text-xs">{place.address}</p>
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1 pt-0.5">
                    {place.phone && (
                      <span className="flex items-center gap-1 text-zinc-400 text-xs">
                        <PhoneIcon size={9} />
                        {place.phone}
                      </span>
                    )}
                    {place.maps_link && (
                      <a
                        href={place.maps_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-indigo-400 hover:text-indigo-300 text-xs transition-colors"
                      >
                        <ExternalLinkIcon size={9} />
                        View Map
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

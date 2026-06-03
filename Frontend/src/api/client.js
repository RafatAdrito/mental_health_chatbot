const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function getToken() {
  return localStorage.getItem("mh_token");
}

async function request(path, options = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  if (res.status === 401) {
    // Token is invalid or expired — clear local auth state
    localStorage.removeItem("mh_token");
    // Dispatch a custom event so the store can react without a circular import
    window.dispatchEvent(new Event("auth:expired"));
  }

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // ignore parse failure
    }
    throw new Error(detail);
  }
  return res.json();
}

export { BASE_URL, getToken, request };

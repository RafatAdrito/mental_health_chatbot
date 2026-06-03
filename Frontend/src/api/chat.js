import { request } from "./client";

export async function createSession() {
  return request("/api/v1/chat/session", { method: "POST" });
}

export async function listSessions() {
  return request("/api/v1/chat/sessions");
}

export async function getHistory(sessionId) {
  return request(`/api/v1/chat/history/${sessionId}`);
}

export async function deleteSession(sessionId) {
  return request(`/api/v1/chat/session/${sessionId}`, { method: "DELETE" });
}

export async function sendMessageRest({
  sessionId,
  message,
  latitude,
  longitude,
}) {
  return request("/api/v1/chat", {
    method: "POST",
    body: JSON.stringify({
      session_id: sessionId,
      message,
      latitude: latitude ?? null,
      longitude: longitude ?? null,
    }),
  });
}

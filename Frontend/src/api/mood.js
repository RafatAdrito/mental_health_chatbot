import { request } from "./client";

export async function createMoodEntry({
  sessionId,
  moodScore,
  moodLabel,
  notes,
}) {
  return request("/api/v1/mood", {
    method: "POST",
    body: JSON.stringify({
      session_id: sessionId || null,
      mood_score: moodScore,
      mood_label: moodLabel,
      notes: notes || null,
    }),
  });
}

export async function getMoodHistory({ days = 30, limit = 50 } = {}) {
  return request(`/api/v1/mood?days=${days}&limit=${limit}`);
}

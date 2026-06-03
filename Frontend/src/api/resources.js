import { request } from "./client";

export async function getCrisisLines() {
  return request("/api/v1/resources/crisis-lines");
}

export async function getNearbyResources(
  latitude,
  longitude,
  type = "hospital",
) {
  const params = new URLSearchParams({
    latitude: String(latitude),
    longitude: String(longitude),
    type,
  });
  return request(`/api/v1/resources/nearby?${params}`);
}

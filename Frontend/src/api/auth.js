import { request } from "./client";

export async function signup({ username, email, password, displayName }) {
  return request("/api/v1/auth/signup", {
    method: "POST",
    body: JSON.stringify({
      username,
      email,
      password,
      display_name: displayName || null,
    }),
  });
}

export async function login({ email, password }) {
  return request("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function getCurrentUser() {
  return request("/api/v1/auth/me");
}

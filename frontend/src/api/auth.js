import { request, setToken } from "./client";

export async function login(email, password) {
  const data = await request("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setToken(data.access_token);
}

export async function register(name, email, password) {
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const data = await request("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ name, email, password, timezone }),
  });
  setToken(data.access_token);
}

export const fetchMe = () => request("/api/auth/me");
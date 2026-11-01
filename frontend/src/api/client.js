const API_URL = import.meta.env.VITE_API_URL;
const TOKEN_KEY = "lifeos_token";

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (t) => localStorage.setItem(TOKEN_KEY, t);
export const clearToken = () => localStorage.removeItem(TOKEN_KEY);

let onUnauthorized = () => {};
export function setUnauthorizedHandler(fn) {
  onUnauthorized = fn;
}

function errorMessage(body, status) {
  const d = body?.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) return d.map((x) => x.msg).join("; ");
  return `Request failed (${status})`;
}

export async function request(path, options = {}) {
  const token = getToken();
  const headers = { ...(options.headers || {}) };
  if (options.body) headers["Content-Type"] = "application/json";
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    if (res.status === 401 && token) {
      clearToken(); // expired or invalid token: back to the login screen
      onUnauthorized();
    }
    const body = await res.json().catch(() => ({}));
    throw new Error(errorMessage(body, res.status));
  }
  if (res.status === 204) return null;
  return res.json();
}
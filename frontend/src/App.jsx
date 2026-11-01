import { useEffect, useState } from "react";
import { fetchMe } from "./api/auth";
import { clearToken, getToken, setUnauthorizedHandler } from "./api/client";
import Chat from "./pages/Chat";
import LoginPage from "./pages/LoginPage";
import "./App.css";

export default function App() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(Boolean(getToken()));

  useEffect(() => {
    setUnauthorizedHandler(() => setUser(null));
    if (!getToken()) return;
    fetchMe()
      .then(setUser)
      .catch(() => {})
      .finally(() => setChecking(false));
  }, []);

  function handleLogout() {
    clearToken();
    setUser(null);
  }

  if (checking) return <div className="center-screen"><p className="hint">Loading…</p></div>;
  if (!user) return <LoginPage onAuthenticated={async () => setUser(await fetchMe())} />;
  return <Chat key={user.id} user={user} onLogout={handleLogout} />;
}
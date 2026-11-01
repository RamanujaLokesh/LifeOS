import { useState } from "react";
import { login, register } from "../api/auth";

export default function LoginPage({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "login") await login(email, password);
      else await register(name, email, password);
      await onAuthenticated();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  const isLogin = mode === "login";

  return (
    <div className="center-screen">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1>LifeOS</h1>
        <p className="hint">{isLogin ? "Sign in to continue" : "Create your account"}</p>

        {!isLogin && (
          <input
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            autoComplete="name"
            required
          />
        )}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="username"
          required
        />
        <input
          type="password"
          placeholder={isLogin ? "Password" : "Password (min 10 characters)"}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete={isLogin ? "current-password" : "new-password"}
          required
        />

        {error && <div className="error"><span>{error}</span></div>}

        <button type="submit" disabled={busy}>
          {busy ? "Please wait…" : isLogin ? "Sign in" : "Create account"}
        </button>
        <button
          type="button"
          className="link-btn"
          onClick={() => { setMode(isLogin ? "register" : "login"); setError(""); }}
        >
          {isLogin ? "Need an account? Register" : "Have an account? Sign in"}
        </button>
      </form>
    </div>
  );
}
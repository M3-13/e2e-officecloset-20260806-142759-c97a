import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../App";
import "../App.css";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await api.post("/api/auth/login", { email, password });
      login(data.access_token, { email });
      navigate("/wardrobe", { replace: true });
    } catch (err) {
      setError(err.message || "Login fehlgeschlagen");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-container page-container--centered fade-enter">
      <div className="auth-card">
        <h1 className="auth-card__title">Login</h1>
        <hr className="accent-separator" />

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <div className="auth-form__group">
            <label className="auth-form__label" htmlFor="login-email">
              E-Mail
            </label>
            <input
              id="login-email"
              className="auth-form__input"
              type="email"
              placeholder="deine@email.de"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="auth-form__group">
            <label className="auth-form__label" htmlFor="login-password">
              Passwort
            </label>
            <input
              id="login-password"
              className="auth-form__input"
              type="password"
              placeholder="••••••••"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && <div className="auth-form__submit-error">{error}</div>}

          <button
            className="auth-form__submit"
            type="submit"
            disabled={loading}
          >
            {loading ? "Wird angemeldet..." : "Anmelden"}
          </button>
        </form>

        <p className="auth-card__footer">
          Noch kein Konto?{" "}
          <Link className="auth-card__link" to="/register">
            Jetzt registrieren
          </Link>
        </p>
      </div>
    </div>
  );
}

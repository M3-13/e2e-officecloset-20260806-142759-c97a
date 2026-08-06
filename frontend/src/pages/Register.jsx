import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../App";
import "../App.css";

function validate(email, password, confirm) {
  const errors = {};

  if (!email.trim()) {
    errors.email = "E-Mail ist erforderlich";
  }
  if (!password) {
    errors.password = "Passwort ist erforderlich";
  } else if (password.length < 8) {
    errors.password = "Passwort muss mindestens 8 Zeichen lang sein";
  }
  if (!confirm) {
    errors.confirm = "Bestätigung ist erforderlich";
  } else if (password && confirm && password !== confirm) {
    errors.confirm = "Passwörter stimmen nicht überein";
  }

  return errors;
}

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setServerError("");

    const validationErrors = validate(email, password, confirm);
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length > 0) {
      return;
    }

    setLoading(true);

    try {
      const data = await api.post("/api/auth/register", { email, password });
      login(data.access_token, { email });
      navigate("/wardrobe", { replace: true });
    } catch (err) {
      setServerError(err.message || "Registrierung fehlgeschlagen");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-container page-container--centered fade-enter">
      <div className="auth-card">
        <h1 className="auth-card__title">Registrierung</h1>
        <hr className="accent-separator" />

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <div className="auth-form__group">
            <label className="auth-form__label" htmlFor="register-email">
              E-Mail
            </label>
            <input
              id="register-email"
              className={
                "auth-form__input" +
                (errors.email ? " auth-form__input--error" : "")
              }
              type="email"
              placeholder="deine@email.de"
              autoComplete="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                if (errors.email) setErrors((p) => ({ ...p, email: "" }));
              }}
              required
            />
            {errors.email && (
              <span className="auth-form__error">{errors.email}</span>
            )}
          </div>

          <div className="auth-form__group">
            <label className="auth-form__label" htmlFor="register-password">
              Passwort
            </label>
            <input
              id="register-password"
              className={
                "auth-form__input" +
                (errors.password ? " auth-form__input--error" : "")
              }
              type="password"
              placeholder="Mindestens 8 Zeichen"
              autoComplete="new-password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (errors.password) setErrors((p) => ({ ...p, password: "" }));
              }}
              required
            />
            {errors.password && (
              <span className="auth-form__error">{errors.password}</span>
            )}
          </div>

          <div className="auth-form__group">
            <label className="auth-form__label" htmlFor="register-confirm">
              Passwort bestätigen
            </label>
            <input
              id="register-confirm"
              className={
                "auth-form__input" +
                (errors.confirm ? " auth-form__input--error" : "")
              }
              type="password"
              placeholder="Passwort wiederholen"
              autoComplete="new-password"
              value={confirm}
              onChange={(e) => {
                setConfirm(e.target.value);
                if (errors.confirm) setErrors((p) => ({ ...p, confirm: "" }));
              }}
              required
            />
            {errors.confirm && (
              <span className="auth-form__error">{errors.confirm}</span>
            )}
          </div>

          {serverError && (
            <div className="auth-form__submit-error">{serverError}</div>
          )}

          <button
            className="auth-form__submit"
            type="submit"
            disabled={loading}
          >
            {loading ? "Wird registriert..." : "Registrieren"}
          </button>
        </form>

        <p className="auth-card__footer">
          Bereits registriert?{" "}
          <Link className="auth-card__link" to="/login">
            Jetzt anmelden
          </Link>
        </p>
      </div>
    </div>
  );
}

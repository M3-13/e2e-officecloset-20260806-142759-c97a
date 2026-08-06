const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

let _token = null;
let _logoutHandler = null;

function authHeaders() {
  const headers = { "Content-Type": "application/json" };
  if (_token) {
    headers["Authorization"] = `Bearer ${_token}`;
  }
  return headers;
}

export function setToken(token) {
  _token = token;
}

export function clearToken() {
  _token = null;
}

export function setLogoutHandler(handler) {
  _logoutHandler = handler;
}

export const api = {
  get BASE_URL() {
    return BASE_URL;
  },

  async get(path) {
    const res = await fetch(`${BASE_URL}${path}`, {
      method: "GET",
      headers: authHeaders(),
    });
    if (res.status === 401 && _logoutHandler) {
      _logoutHandler();
    }
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || `Request failed: ${res.status}`);
    }
    if (res.status === 204) return null;
    return res.json();
  },

  async post(path, body) {
    const res = await fetch(`${BASE_URL}${path}`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(body),
    });
    if (res.status === 401 && _logoutHandler) {
      _logoutHandler();
    }
    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      throw new Error(errBody.detail || `Request failed: ${res.status}`);
    }
    return res.json();
  },

  async upload(path, formData) {
    const headers = {};
    if (_token) {
      headers["Authorization"] = `Bearer ${_token}`;
    }
    const res = await fetch(`${BASE_URL}${path}`, {
      method: "POST",
      headers,
      body: formData,
    });
    if (res.status === 401 && _logoutHandler) {
      _logoutHandler();
    }
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || `Upload failed: ${res.status}`);
    }
    return res.json();
  },

  async del(path) {
    const res = await fetch(`${BASE_URL}${path}`, {
      method: "DELETE",
      headers: authHeaders(),
    });
    if (res.status === 401 && _logoutHandler) {
      _logoutHandler();
    }
    if (res.status === 204) return null;
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || `Delete failed: ${res.status}`);
    }
    return res.json();
  },
};

import { createContext, useContext, useState, useCallback, useMemo, useEffect } from "react";
import { Routes, Route, Outlet } from "react-router-dom";
import Navbar from "./components/Navbar";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Wardrobe from "./pages/Wardrobe";
import OutfitCreator from "./pages/OutfitCreator";
import Outfits from "./pages/Outfits";
import { setToken, clearToken, setLogoutHandler } from "./api";
import "./App.css";

const AuthContext = createContext(null);

const TOKEN_KEY = "glamour_wardrobe_token";
const USER_KEY = "glamour_wardrobe_user";

function loadStoredAuth() {
  const token = localStorage.getItem(TOKEN_KEY);
  const userRaw = localStorage.getItem(USER_KEY);
  let user = null;
  if (userRaw) {
    try {
      user = JSON.parse(userRaw);
    } catch {
      user = null;
    }
  }
  if (token && user) {
    setToken(token);
    return { token, user };
  }
  return { token: null, user: null };
}

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(loadStoredAuth);

  const loginHandler = useCallback((token, user) => {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    setToken(token);
    setAuth({ token, user });
  }, []);

  const logoutHandler = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    clearToken();
    setAuth({ token: null, user: null });
  }, []);

  useEffect(() => {
    setLogoutHandler(logoutHandler);
    return () => setLogoutHandler(null);
  }, [logoutHandler]);

  const value = useMemo(
    () => ({
      token: auth.token,
      user: auth.user,
      isAuthenticated: !!auth.token,
      login: loginHandler,
      logout: logoutHandler,
    }),
    [auth.token, auth.user, loginHandler, logoutHandler]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}

function Layout() {
  return (
    <div className="app-layout">
      <Navbar />
      <main style={{ paddingTop: "88px" }}>
        <Outlet />
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Wardrobe />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/wardrobe" element={<Wardrobe />} />
          <Route path="/outfits/create" element={<OutfitCreator />} />
          <Route path="/outfits" element={<Outfits />} />
        </Route>
      </Routes>
    </AuthProvider>
  );
}

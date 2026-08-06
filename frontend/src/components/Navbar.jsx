import { Link, NavLink } from "react-router-dom";
import { useAuth } from "../App";
import styles from "./Navbar.module.css";

export default function Navbar() {
  const { isAuthenticated, logout } = useAuth();

  return (
    <nav className={styles.nav}>
      <div className={styles.inner}>
        <Link to="/" className={styles.logo}>
          My Closet ✨
        </Link>
        <div className={styles.links}>
          <NavLink to="/wardrobe" className={({ isActive }) => isActive ? styles.linkActive : styles.link}>
            Garderobe
          </NavLink>
          <NavLink to="/outfits/create" className={({ isActive }) => isActive ? styles.linkActive : styles.link}>
            Outfit-Creator
          </NavLink>
          <NavLink to="/outfits" className={({ isActive }) => isActive ? styles.linkActive : styles.link}>
            Outfits
          </NavLink>
          {isAuthenticated ? (
            <button onClick={logout} className={styles.linkButton}>
              Logout
            </button>
          ) : (
            <>
              <NavLink to="/login" className={({ isActive }) => isActive ? styles.linkActive : styles.link}>
                Login
              </NavLink>
              <NavLink to="/register" className={({ isActive }) => isActive ? styles.linkActive : styles.link}>
                Registrierung
              </NavLink>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

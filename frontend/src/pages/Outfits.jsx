import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../App";
import styles from "./Outfits.module.css";

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString("de-DE", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

function AuthImage({ src, alt }) {
  const { token } = useAuth();
  const [blobUrl, setBlobUrl] = useState(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let cancelled = false;
    if (!src) {
      setFailed(true);
      return;
    }

    const headers = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    fetch(`${api.BASE_URL}${src}`, { headers })
      .then((res) => {
        if (!res.ok) throw new Error("Failed");
        return res.blob();
      })
      .then((blob) => {
        if (!cancelled) {
          const url = URL.createObjectURL(blob);
          setBlobUrl((prev) => {
            if (prev) URL.revokeObjectURL(prev);
            return url;
          });
        }
      })
      .catch(() => {
        if (!cancelled) setFailed(true);
      });

    return () => {
      cancelled = true;
    };
  }, [src, token]);

  useEffect(() => {
    return () => {
      if (blobUrl) URL.revokeObjectURL(blobUrl);
    };
  }, []);

  if (failed) {
    return <div className={styles.thumbnailPlaceholder}>{alt?.[0] || "?"}</div>;
  }
  if (!blobUrl) {
    return <div className={styles.thumbnailSkeleton} />;
  }
  return (
    <img
      src={blobUrl}
      alt={alt}
      className={styles.thumbnail}
    />
  );
}

function ConfirmDialog({ outfitName, onConfirm, onCancel, loading }) {
  return (
    <div className={styles.overlay} onClick={loading ? undefined : onCancel}>
      <div className={styles.dialog} onClick={(e) => e.stopPropagation()}>
        <h2 className={styles.dialogTitle}>Wirklich löschen?</h2>
        <p className={styles.dialogText}>
          Möchtest du das Outfit <strong>"{outfitName}"</strong> wirklich
          löschen? Diese Aktion kann nicht rückgängig gemacht werden.
        </p>
        <div className={styles.dialogActions}>
          <button
            className={styles.cancelBtn}
            onClick={onCancel}
            disabled={loading}
          >
            Abbrechen
          </button>
          <button
            className={styles.confirmBtn}
            onClick={onConfirm}
            disabled={loading}
          >
            {loading ? "Löschen..." : "Löschen"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Outfits() {
  const [outfits, setOutfits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const fetchOutfits = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.get("/api/outfits");
      setOutfits(data || []);
    } catch (err) {
      setError(err.message || "Fehler beim Laden der Outfits");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchOutfits();
  }, [fetchOutfits]);

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      setDeleting(true);
      await api.del(`/api/outfits/${deleteTarget.id}`);
      setOutfits((prev) => prev.filter((o) => o.id !== deleteTarget.id));
      setDeleteTarget(null);
    } catch (err) {
      setError(err.message || "Fehler beim Löschen des Outfits");
      setDeleteTarget(null);
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="page-container page-container--centered fade-enter">
        <div className={styles.loadingContainer}>
          <div className={styles.spinner} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container page-container--centered fade-enter">
        <div className={styles.errorContainer}>
          <p className={styles.errorText}>{error}</p>
          <button className={styles.retryBtn} onClick={fetchOutfits}>
            Erneut versuchen
          </button>
        </div>
      </div>
    );
  }

  if (outfits.length === 0) {
    return (
      <div className="page-container page-container--centered fade-enter">
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>✨</div>
          <h2 className={styles.emptyTitle}>Noch keine Outfits</h2>
          <p className={styles.emptyText}>Erstelle dein erstes!</p>
          <Link to="/outfits/create" className={styles.emptyLink}>
            Zum Outfit-Creator
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container fade-enter">
      <h1 className="page-title">Outfits</h1>
      <hr className="accent-separator" />
      <div className={styles.gallery}>
        {outfits.map((outfit) => (
          <div key={outfit.id} className={styles.card}>
            <div className={styles.thumbnails}>
              {outfit.items && outfit.items.length > 0 ? (
                outfit.items.map((item) => (
                  <AuthImage
                    key={item.id}
                    src={item.image_url}
                    alt={item.name}
                  />
                ))
              ) : (
                <div className={styles.thumbnailPlaceholder}>—</div>
              )}
            </div>
            <div className={styles.cardBody}>
              <h3 className={styles.outfitName}>{outfit.name}</h3>
              <p className={styles.outfitDate}>
                {formatDate(outfit.created_at)}
              </p>
              <button
                className={styles.deleteBtn}
                onClick={() => setDeleteTarget(outfit)}
              >
                Löschen
              </button>
            </div>
          </div>
        ))}
      </div>

      {deleteTarget && (
        <ConfirmDialog
          outfitName={deleteTarget.name}
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
          loading={deleting}
        />
      )}
    </div>
  );
}

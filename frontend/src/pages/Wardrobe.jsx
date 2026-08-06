import { useState, useEffect, useRef } from "react";
import { api } from "../api";
import { useAuth } from "../App";
import "../App.css";
import styles from "./Wardrobe.module.css";

const CATEGORIES = ["Alle", "Oberteil", "Hose", "Kleid", "Schuhe", "Accessoire"];

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
    return (
      <div className={styles.cardImagePlaceholder}>
        {alt?.[0] || "?"}
      </div>
    );
  }
  if (!blobUrl) {
    return <div className={styles.cardImageSkeleton} />;
  }
  return <img src={blobUrl} alt={alt} />;
}

export default function Wardrobe() {
  const { isAuthenticated } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeCategory, setActiveCategory] = useState("Alle");
  const [refreshKey, setRefreshKey] = useState(0);

  const [name, setName] = useState("");
  const [category, setCategory] = useState("Oberteil");
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState(null);

  const [isDragOver, setIsDragOver] = useState(false);

  const fileInputRef = useRef(null);
  const dragCounter = useRef(0);

  function handleDragEnter(e) {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current++;
    if (dragCounter.current === 1) setIsDragOver(true);
  }

  function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current--;
    if (dragCounter.current === 0) setIsDragOver(false);
  }

  function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    dragCounter.current = 0;

    const file = e.dataTransfer?.files?.[0];
    if (!file) return;

    // Only accept image files
    if (!file.type.startsWith("image/")) return;

    setImageFile(file);
    const reader = new FileReader();
    reader.onloadend = () => setImagePreview(reader.result);
    reader.readAsDataURL(file);

    if (fileInputRef.current) {
      const dt = new DataTransfer();
      dt.items.add(file);
      fileInputRef.current.files = dt.files;
    }
  }

  function clearPreview() {
    setImageFile(null);
    setImagePreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function fetchItems() {
      setLoading(true);
      setError(null);
      try {
        const params =
          activeCategory !== "Alle"
            ? `?category=${encodeURIComponent(activeCategory)}`
            : "";
        const data = await api.get(`/api/wardrobe${params}`);
        if (!cancelled) setItems(data);
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchItems();
    return () => {
      cancelled = true;
    };
  }, [isAuthenticated, activeCategory, refreshKey]);

  function handleFileChange(e) {
    const file = e.target.files[0];
    if (!file) {
      setImageFile(null);
      setImagePreview(null);
      return;
    }
    setImageFile(file);
    const reader = new FileReader();
    reader.onloadend = () => setImagePreview(reader.result);
    reader.readAsDataURL(file);
  }

  async function handleUpload(e) {
    e.preventDefault();
    if (!name.trim() || !imageFile) return;

    setUploading(true);
    setUploadError(null);
    setUploadSuccess(false);

    try {
      const formData = new FormData();
      formData.append("name", name.trim());
      formData.append("category", category);
      formData.append("image", imageFile);

      const newItem = await api.upload("/api/wardrobe", formData);

      if (activeCategory === "Alle" || activeCategory === newItem.category) {
        setItems((prev) => [newItem, ...prev]);
      }

      setName("");
      setImageFile(null);
      setImagePreview(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      setUploadSuccess(true);
      setTimeout(() => setUploadSuccess(false), 3000);
    } catch (err) {
      setUploadError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete() {
    if (!deleteTarget) return;

    setDeleting(true);
    setDeleteError(null);
    try {
      await api.del(`/api/wardrobe/${deleteTarget.id}`);
      setItems((prev) => prev.filter((item) => item.id !== deleteTarget.id));
      setDeleteTarget(null);
    } catch (err) {
      setDeleteError(err.message);
    } finally {
      setDeleting(false);
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="page-container page-container--centered fade-enter">
        <h1 className="page-title">Garderobe</h1>
        <hr className="accent-separator" />
        <p className="page-subtitle">
          Bitte melde dich an, um deine Garderobe zu sehen.
        </p>
      </div>
    );
  }

  return (
    <div className="page-container fade-enter">
      <h1 className="page-title" style={{ textAlign: "center" }}>
        Garderobe
      </h1>
      <hr className="accent-separator" />

      <section className={styles.uploadSection}>
        <h2 className={styles.sectionTitle}>Neues Kleidungsstück</h2>
        <form className={styles.uploadForm} onSubmit={handleUpload}>
          <div className={styles.uploadFields}>
            <div className={styles.field}>
              <label className={styles.label} htmlFor="item-name">
                Name
              </label>
              <input
                id="item-name"
                className={styles.input}
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="z.B. Schwarze Lederjacke"
                required
              />
            </div>

            <div className={styles.field}>
              <label className={styles.label} htmlFor="item-category">
                Kategorie
              </label>
              <select
                id="item-category"
                className={styles.select}
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              >
                {CATEGORIES.filter((c) => c !== "Alle").map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>

            <div className={styles.field}>
              <label className={styles.label}>Bild</label>
              <div
                className={`${styles.uploadZone}${isDragOver ? ` ${styles.uploadZoneDragOver}` : ""}${imagePreview ? ` ${styles.uploadZoneHasPreview}` : ""}`}
                onClick={() => fileInputRef.current?.click()}
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
              >
                {imagePreview ? (
                  <div className={styles.previewWrap}>
                    <img
                      src={imagePreview}
                      alt="Vorschau"
                      className={styles.uploadPreview}
                    />
                    <button
                      type="button"
                      className={styles.previewRemove}
                      onClick={(e) => { e.stopPropagation(); clearPreview(); }}
                      title="Bild entfernen"
                      aria-label="Bild entfernen"
                    >
                      &#10005;
                    </button>
                  </div>
                ) : (
                  <>
                    <div className={styles.uploadIcon}>&#128247;</div>
                    <p className={styles.uploadText}>
                      Bild hier ablegen oder klicken zum Hochladen
                    </p>
                    <p className={styles.uploadHint}>
                      JPEG, PNG, GIF oder WebP – max. 5 MB
                    </p>
                  </>
                )}
                <input
                  ref={fileInputRef}
                  id="item-image"
                  type="file"
                  accept="image/jpeg,image/png,image/gif,image/webp"
                  onChange={handleFileChange}
                  className={styles.fileInput}
                  aria-label="Bild auswählen"
                />
              </div>
            </div>
          </div>

          <button
            type="submit"
            className={styles.btnPrimary}
            disabled={uploading || !name.trim() || !imageFile}
          >
            {uploading ? "Lädt hoch..." : "Hochladen"}
          </button>

          {uploadError && <p className={styles.error}>{uploadError}</p>}
          {uploadSuccess && (
            <p className={styles.success}>
              Kleidungsstück erfolgreich hinzugefügt!
            </p>
          )}
        </form>
      </section>

      <section className={styles.filterSection}>
        <div className={styles.filterPills}>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              className={`${styles.pill}${activeCategory === cat ? ` ${styles.pillActive}` : ""}`}
              onClick={() => setActiveCategory(cat)}
            >
              {cat}
            </button>
          ))}
        </div>
      </section>

      <section className={styles.gallery}>
        {loading ? (
          <div className={styles.emptyState}>
            <div className={styles.spinner} />
            <p className={styles.emptyText}>Lade Garderobe...</p>
          </div>
        ) : error ? (
          <div className={styles.emptyState}>
            <p className={styles.error}>{error}</p>
            <button
              className={styles.btnGhost}
              onClick={() => setRefreshKey((k) => k + 1)}
            >
              Erneut versuchen
            </button>
          </div>
        ) : items.length === 0 ? (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>&#128087;</div>
            <p className={styles.emptyText}>
              {activeCategory === "Alle"
                ? "Deine Garderobe ist noch leer. Füge dein erstes Kleidungsstück hinzu!"
                : `Keine Kleidungsstücke in der Kategorie „${activeCategory}“ gefunden.`}
            </p>
          </div>
        ) : (
          <div className={styles.grid}>
            {items.map((item) => (
              <div key={item.id} className={styles.card}>
                <div className={styles.cardImage}>
                  <AuthImage src={item.image_url} alt={item.name} />
                </div>
                <div className={styles.cardBody}>
                  <h3 className={styles.cardName}>{item.name}</h3>
                  <span className={styles.cardCategory}>{item.category}</span>
                  <button
                    className={styles.cardDelete}
                    onClick={() => setDeleteTarget(item)}
                    title="Löschen"
                    aria-label={`${item.name} löschen`}
                  >
                    &#10005;
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {deleteTarget && (
        <div
          className={styles.overlay}
          onClick={() => setDeleteTarget(null)}
        >
          <div className={styles.dialog} onClick={(e) => e.stopPropagation()}>
            <h2 className={styles.dialogTitle}>
              Kleidungsstück löschen
            </h2>
            <hr className={styles.dialogSeparator} />
            <p className={styles.dialogText}>
              Möchtest du „{deleteTarget.name}“ wirklich löschen? Diese Aktion
              kann nicht rückgängig gemacht werden.
            </p>
            {deleteError && <p className={styles.error}>{deleteError}</p>}
            <div className={styles.dialogActions}>
              <button
                className={styles.btnGhost}
                onClick={() => setDeleteTarget(null)}
                disabled={deleting}
              >
                Abbrechen
              </button>
              <button
                className={styles.btnDanger}
                onClick={handleDelete}
                disabled={deleting}
              >
                {deleting ? "Löscht..." : "Löschen"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

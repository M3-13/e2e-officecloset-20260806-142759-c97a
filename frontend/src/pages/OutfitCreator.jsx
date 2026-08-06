import { useState, useEffect, useCallback, useRef } from "react";
import { api } from "../api";
import styles from "./OutfitCreator.module.css";
import "../App.css";

const ALLE_CATEGORY = "Alle";

function buildImageUrl(imageUrl) {
  if (!imageUrl) return "";
  if (imageUrl.startsWith("http://") || imageUrl.startsWith("https://")) return imageUrl;
  if (imageUrl.startsWith("/")) return `${api.BASE_URL}${imageUrl}`;
  return `${api.BASE_URL}/api/uploads/${imageUrl}`;
}

export default function OutfitCreator() {
  const [allItems, setAllItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFilter, setSelectedFilter] = useState(ALLE_CATEGORY);
  const [selectedItems, setSelectedItems] = useState({});
  const [outfitName, setOutfitName] = useState("");
  const [saving, setSaving] = useState(false);
  const [hint, setHint] = useState(null);
  const [successOutfit, setSuccessOutfit] = useState(null);
  const hintTimerRef = useRef(null);

  const categories = [
    ALLE_CATEGORY,
    ...new Set(allItems.map((item) => item.category).filter(Boolean)),
  ];

  const filteredItems =
    selectedFilter === ALLE_CATEGORY
      ? allItems
      : allItems.filter((item) => item.category === selectedFilter);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await api.get("/api/wardrobe");
        if (!cancelled) {
          setAllItems(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Fehler beim Laden der Garderobe");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const showHint = useCallback((message) => {
    if (hintTimerRef.current) clearTimeout(hintTimerRef.current);
    setHint(message);
    hintTimerRef.current = setTimeout(() => setHint(null), 3000);
  }, []);

  useEffect(() => {
    return () => {
      if (hintTimerRef.current) clearTimeout(hintTimerRef.current);
    };
  }, []);

  const toggleItem = useCallback(
    (item) => {
      const current = selectedItems[item.category];

      if (current && current.id === item.id) {
        setSelectedItems((prev) => {
          const next = { ...prev };
          delete next[item.category];
          return next;
        });
        return;
      }

      if (current && current.id !== item.id) {
        showHint(
          `Die Kategorie \u201e${item.category}\u201c ist bereits mit \u201e${current.name}\u201c besetzt. Entferne es zuerst, um ein anderes St\u00fcck auszuw\u00e4hlen.`
        );
        return;
      }

      setSelectedItems((prev) => ({ ...prev, [item.category]: item }));
    },
    [selectedItems, showHint]
  );

  const removeItem = useCallback((category) => {
    setSelectedItems((prev) => {
      const next = { ...prev };
      delete next[category];
      return next;
    });
  }, []);

  const handleSave = useCallback(async () => {
    const itemIds = Object.values(selectedItems).map((item) => item.id);
    if (itemIds.length === 0) {
      showHint("W\u00e4hle mindestens ein Kleidungsst\u00fcck f\u00fcr dein Outfit aus.");
      return;
    }
    if (!outfitName.trim()) {
      showHint("Gib deinem Outfit einen glamour\u00f6sen Namen.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const result = await api.post("/api/outfits", {
        name: outfitName.trim(),
        item_ids: itemIds,
      });
      setSuccessOutfit(result);
      setSelectedItems({});
      setOutfitName("");
    } catch (err) {
      setError(err.message || "Fehler beim Speichern des Outfits");
    } finally {
      setSaving(false);
    }
  }, [selectedItems, outfitName, showHint]);

  const dismissSuccess = useCallback(() => {
    setSuccessOutfit(null);
  }, []);

  const handleCategoryClick = useCallback((cat) => {
    setSelectedFilter(cat);
  }, []);

  const selectedArray = Object.values(selectedItems);
  const canSave = selectedArray.length > 0 && outfitName.trim().length > 0 && !saving;

  return (
    <div className={`${styles.page} fade-enter`}>
      <div className={styles.header}>
        <h1 className={styles.title}>Outfit-Creator</h1>
        <hr className={styles.separator} />
      </div>

      {error && <div className={styles.error}>{error}</div>}

      {hint && <div className={styles.hintToast}>{hint}</div>}

      {successOutfit && (
        <div className={styles.successOverlay} onClick={dismissSuccess}>
          <div
            className={styles.successCard}
            onClick={(e) => e.stopPropagation()}
          >
            <span className={styles.successIcon}>&#x2728;</span>
            <h2 className={styles.successTitle}>Outfit gespeichert!</h2>
            <p className={styles.successMessage}>
              Dein Outfit <strong>\u201e{successOutfit.name}\u201c</strong> wurde mit{" "}
              {successOutfit.items?.length ?? 0} Kleidungsst\u00fccken glamour\u00f6s in
              deinem Kleiderschrank verewigt.
            </p>
            <button className={styles.successClose} onClick={dismissSuccess}>
              Weiter
            </button>
          </div>
        </div>
      )}

      <div className={styles.layout}>
        <div className={styles.wardrobePanel}>
          <h2 className={styles.panelTitle}>Garderobe</h2>

          <div className={styles.categoryFilters}>
            {categories.map((cat) => (
              <button
                key={cat}
                className={`${styles.filterPill} ${
                  selectedFilter === cat ? styles.filterPillActive : ""
                }`}
                onClick={() => handleCategoryClick(cat)}
              >
                {cat}
              </button>
            ))}
          </div>

          {loading && (
            <div className={styles.loading}>
              <div className={styles.spinner} />
            </div>
          )}

          {!loading && allItems.length === 0 && (
            <div className={styles.emptyWardrobe}>
              <span className={styles.emptyWardrobeIcon}>&#x1F453;</span>
              Deine Garderobe ist noch leer. Lade Kleidungsst\u00fccke hoch, um Outfits zu erstellen.
            </div>
          )}

          {!loading && allItems.length > 0 && filteredItems.length === 0 && (
            <div className={styles.emptyWardrobe}>
              <span className={styles.emptyWardrobeIcon}>&#x1F453;</span>
              Keine Kleidungsst\u00fccke in dieser Kategorie.
            </div>
          )}

          {!loading && filteredItems.length > 0 && (
            <div className={styles.wardrobeGrid}>
              {filteredItems.map((item) => {
                const isSelected =
                  selectedItems[item.category] &&
                  selectedItems[item.category].id === item.id;
                return (
                  <button
                    key={item.id}
                    className={`${styles.wardrobeItem} ${
                      isSelected ? styles.wardrobeItemSelected : ""
                    }`}
                    onClick={() => toggleItem(item)}
                    title={`${item.name} \u2013 ${item.category}`}
                  >
                    <img
                      src={buildImageUrl(item.image_url)}
                      alt={item.name}
                      className={styles.wardrobeItemImage}
                      loading="lazy"
                    />
                    <span className={styles.wardrobeItemName}>
                      {item.name}
                    </span>
                    <span className={styles.wardrobeItemCategory}>
                      {item.category}
                    </span>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        <div className={styles.outfitPanel}>
          <h2 className={styles.panelTitle}>Dein Outfit</h2>

          <div
            className={`${styles.outfitCanvas} ${
              selectedArray.length > 0 ? styles.outfitCanvasHasItems : ""
            }`}
          >
            {selectedArray.length === 0 ? (
              <div className={styles.outfitEmpty}>
                <span className={styles.outfitEmptyIcon}>&#x1F451;</span>
                <p className={styles.outfitEmptyText}>
                  Klicke auf Kleidungsst\u00fccke aus deiner Garderobe, um sie
                  deinem Outfit hinzuzuf\u00fcgen.
                </p>
              </div>
            ) : (
              <div className={styles.outfitItems}>
                {selectedArray.map((item) => (
                  <div key={item.id} className={styles.outfitItemCard}>
                    <button
                      className={styles.removeButton}
                      onClick={() => removeItem(item.category)}
                      aria-label={`${item.name} entfernen`}
                    >
                      &times;
                    </button>
                    <img
                      src={buildImageUrl(item.image_url)}
                      alt={item.name}
                      className={styles.outfitItemImage}
                    />
                    <span className={styles.outfitItemName}>{item.name}</span>
                    <span className={styles.outfitItemCategory}>
                      {item.category}
                    </span>
                  </div>
                ))}
              </div>
            )}

            <input
              className={styles.nameInput}
              type="text"
              placeholder={'Outfit-Name (z. B. \u201eRoter Teppich\u201c)'}
              value={outfitName}
              onChange={(e) => setOutfitName(e.target.value)}
              disabled={saving}
              maxLength={100}
            />

            <button
              className={styles.saveButton}
              onClick={handleSave}
              disabled={!canSave}
            >
              {saving ? "Speichere..." : "Outfit speichern"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

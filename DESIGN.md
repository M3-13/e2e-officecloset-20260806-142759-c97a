# Design — Project Identity

> This document is project-long-lived. Tokens are not changed without
> the Architect's approval. Developers MUST use these tokens
> instead of improvising their own colors/spacings.

## Style Direction

Glamouröse Hollywood-Red-Carpet-Optik: tiefes, warmes Schwarz (#0D0D0D) als Bühnenhintergrund, gediegenes Blattgold (#C9A84C) als Akzent, elegante Serif (Playfair Display) für Headings trifft auf klare Sans-Serif (Inter) für UI-Elemente – wie eine exklusive Backstage-VIP-Lounge mit weichen Spotlight-Übergängen.

## Colors

- `--color-bg`: **#0D0D0D**
- `--color-bg-elevated`: **#1A1A1A**
- `--color-bg-glass`: **rgba(26, 26, 26, 0.85)**
- `--color-fg`: **#F5F0EB**
- `--color-fg-secondary`: **#BFB8AD**
- `--color-accent`: **#C9A84C**
- `--color-accent-hover`: **#DEBF5E**
- `--color-accent-glow`: **rgba(201, 168, 76, 0.25)**
- `--color-border`: **#2E2D2A**
- `--color-muted`: **#7A756E**
- `--color-error`: **#C44E3D**
- `--color-success`: **#5B8C5A**
- `--color-overlay`: **rgba(0, 0, 0, 0.7)**

## Typography

- `font_family`: 'Inter', 'Helvetica Neue', Arial, sans-serif
- `heading_font_family`: 'Playfair Display', 'Cormorant Garamond', Georgia, 'Times New Roman', serif
- `heading_weight`: 700
- `body_weight`: 400
- `size_scale`: xs: 0.75rem; sm: 0.875rem; base: 1rem; lg: 1.125rem; xl: 1.5rem; 2xl: 2rem; 3xl: 2.75rem; hero: 4rem

## Spacing Scale

- `--space-0`: 4px
- `--space-1`: 8px
- `--space-2`: 12px
- `--space-3`: 16px
- `--space-4`: 24px
- `--space-5`: 32px
- `--space-6`: 48px
- `--space-7`: 64px
- `--space-8`: 96px

## Border-Radii

- `--radius-sm`: 4px
- `--radius-md`: 8px
- `--radius-lg`: 16px
- `--radius-xl`: 24px
- `--radius-pill`: 999px

## Components

### Button – Primary

Hintergrund: accent (#C9A84C), Textfarbe: #0D0D0D, padding 12px 28px, radius md (8px), font-weight 600, letter-spacing 0.03em, text-transform uppercase, min-height 48px (mobile tappable). States: default → gold; hover → accent-hover (#DEBF5E) + translateY(-1px) + box-shadow 0 6px 20px accent-glow; active → #B8993C + translateY(0); disabled → opacity 0.4, cursor not-allowed. Übergang: all 0.25s ease.

### Button – Secondary / Ghost

Hintergrund: transparent, Textfarbe: accent (#C9A84C), border 1.5px solid accent, padding 12px 28px, radius md (8px), font-weight 600, letter-spacing 0.03em, min-height 48px. States: default → transparent mit Gold-Rand; hover → bg accent-glow (rgba-Fill) + border accent-hover; active → bg rgba(201,168,76,0.15); disabled → opacity 0.35.

### Button – Danger / Delete

Hintergrund: transparent, Textfarbe: error (#C44E3D), border 1.5px solid error, padding 10px 24px, radius md, font-weight 600, min-height 44px. States: hover → bg rgba(196,78,61,0.12); active → bg rgba(196,78,61,0.22); disabled → opacity 0.35.

### Card – WardrobeItem / OutfitCard

Hintergrund: bg-elevated (#1A1A1A), border 1px solid border (#2E2D2A), radius lg (16px), padding 0 (Bild oben, Textblock 16px), overflow hidden. Hover: border-Farbe wechselt zu accent mit 0.3s ease, box-shadow 0 8px 30px accent-glow, transform scale(1.02). Bildbereich: aspect-ratio 3/4, object-fit cover, mit subtilem vignette-Overlay (linear-gradient, oben transparent → unten rgba(0,0,0,0.4)). Textbereich: padding 16px, Titel in fg, Kategorie-Label in muted, font-size sm.

### Input – Text / Email / Password

Hintergrund: bg-elevated (#1A1A1A), Textfarbe: fg (#F5F0EB), border 1.5px solid border (#2E2D2A), radius md (8px), padding 14px 16px, font-size base, min-height 48px, width 100%. Placeholder: muted (#7A756E), font-style italic. States: default → dunkel mit dezentem Rand; focus → border accent (#C9A84C), box-shadow 0 0 0 3px accent-glow, outline none; error → border error (#C44E3D); disabled → opacity 0.4. Übergang: border-color 0.2s ease, box-shadow 0.2s ease. Label: font-size sm, color fg-secondary, margin-bottom 6px, font-weight 500.

### Modal / Dialog

Overlay: overlay (rgba 0,0,0,0.7) + backdrop-filter blur(6px). Panel: bg-elevated (#1A1A1A), border 1px solid border, radius xl (24px), padding 32px, max-width 520px, zentriert. Eintrittsanimation: fadeIn + scale(0.95→1) über 0.3s ease-out. Schließen-Button (✕): absolut oben rechts, 16px vom Rand, bg transparent, Farbe muted → hover fg, Größe 36×36px, radius pill. Titel: heading_font_family, 2xl, fg, margin-bottom 16px. Trenner: 1px solid border.

### Navigation – Top Bar

Höhe 64px, Hintergrund: rgba(13, 13, 13, 0.92) + backdrop-filter blur(12px), fixiert oben, z-index 100. border-bottom: 1px solid border. Inhalt: max-width 1200px, padding 0 24px, flex zwischen Logo links und Nav-Items rechts. Logo: heading_font_family, 1.5rem, accent (#C9A84C), letter-spacing 0.05em, text-transform uppercase. Nav-Links: font-size sm, fg-secondary, font-weight 500, padding 8px 16px, radius pill. Hover: fg + bg rgba(255,255,255,0.05). Aktiver Link: fg + accent-Farbe, mit 2px accent-underline unten. Mobile: Hamburger-Menü-Icon (fg), Drawer von rechts, bg-glass.

### Gallery – Spotlight Grid

Grid: display grid, grid-template-columns repeat(auto-fill, minmax(260px, 1fr)), gap 24px, padding 24px 0. Jedes Grid-Item (Card) hat beim Hover einen Spotlight-Effekt: ein radialer accent-glow folgt der Mausposition (optional via JS) oder statisch: leichter Glow hinter der Card. Leeres Grid: zentrierter Platzhalter mit muted-Text und dekorativem Gold-Icon (Kleiderbügel-Silhouette), font-size lg, padding 64px 0. Filter-Pills (Kategorie-Filter): bg transparent, border 1px solid border, radius pill, padding 8px 20px, font-size sm, fg-secondary. Aktiv: bg accent, fg #0D0D0D, border accent. Hover (inaktiv): border fg-secondary.

### Outfit Creator – Canvas / Drop Zone

Outfit-Bereich: zentrierte Dropzone oder Anzeigefläche, bg leicht heller als bg (#141414), border 2px dashed border, radius lg, padding 32px, min-height 300px, Übergang border-color 0.3s. Wenn ein Item per Drag oder Klick ausgewählt wird: border wird accent + accent-glow. Leerer Zustand: muted-Text „Ziehe Kleidungsstücke hierher oder klicke sie an“, zentriert. Ausgewählte Items als kleine Vorschaubilder (64×64px, radius sm) nebeneinander mit remove-Button (✕, 18px, muted → error on hover). Speichern-Button (Primary) rechts unten.

### Image Upload – Drop Zone

Upload-Zone: bg-glass, border 2px dashed border, radius lg, padding 48px 24px, zentrierter Inhalt. Icon: Kamera-Symbol in muted, 48px. Text: „Bild hier ablegen oder klicken zum Hochladen“, fg-secondary, margin-top 12px. Hinweistext: „JPEG, PNG, GIF oder WebP – max. 5 MB“, muted, font-size xs, margin-top 8px. Drag-over: border accent, bg accent-glow, Icon färbt accent. Vorschau nach Upload: Bild 200×200px, radius md, border 1px border, mit erneutem Hochladen/Entfernen-Optionen.

### Toast / Notification

Position: fixed, unten rechts, 24px Abstand zum Rand. Hintergrund: bg-elevated (#1A1A1A), border-left 4px solid (accent bei success, error bei Fehler), radius md, padding 16px 20px, max-width 380px, box-shadow 0 8px 32px rgba(0,0,0,0.5). Eintrittsanimation: slideInFromRight + fadeIn, 0.35s ease-out. Auto-dismiss nach 4s (bei Fehlern 6s). Text: fg für Titel (font-weight 600), fg-secondary für Beschreibung (font-size sm). Schließen-Button in muted.

### Loading States

Skeleton-Screens: bg-elevated mit shimmer-Animation (linear-gradient 90°, von border über rgba(255,255,255,0.04) zurück zu border, animiert über 1.5s infinite). Card-Skeleton: Höhe 320px, radius lg. Text-Skeleton: Höhe 16px, radius sm, Breite variabel (60%/80%/40%). Spinner: 28px, border 3px solid border, border-top-color accent, radius 50%, animiert rotate 0.7s linear infinite. Globaler Page-Loader: zentrierter Spinner auf bg mit accent-glow.

## Layout Principles

- Maximale Content-Breite 1200px, zentriert via margin auto, Padding horizontal 24px (Desktop) / 16px (Tablet) / 12px (Mobile).
- Breakpoints: Desktop ≥1024px, Tablet 768–1023px, Mobile <768px. Desktop-First-Ansatz: Basis-Styles für Desktop, @media-Queries für kleinere Screens.
- Grid-System: CSS Grid für Galerien (auto-fill minmax 260px), Flexbox für eindimensionale Layouts (Formulare, Navigation, Outfit-Creator). Gap konsistent aus dem Spacing-System: 24px für Sektionen, 16px innerhalb von Komponenten.
- Vertikaler Rhythmus: Sektions-Abstand 64px (Desktop) / 48px (Mobile). Cards innerhalb einer Sektion haben 24px Abstand. Überschriften haben margin-bottom 16px.
- Seitenstruktur: Top-Navigation (fixiert, 64px) → Main Content (padding-top 88px = Nav-Höhe + 24px Abstand) → optionaler Footer. Jede Hauptseite (Garderobe, Outfits, Creator) folgt demselben Raster.
- Animationen: Alle interaktiven Elemente haben Übergänge von 0.2–0.35s ease/ease-out. Seitenwechsel bekommen ein sanftes Fade (opacity 0→1, 0.25s). Keine übertriebenen Effekte – Eleganz durch Zurückhaltung.
- Touch-Ziele: Alle interaktiven Elemente (Buttons, Filter-Pills, Nav-Links, Schließen-Buttons) haben eine Mindestgröße von 44×44px für mobile Bedienbarkeit.
- Zugänglichkeit: Kontrastverhältnis fg zu bg ≥ 4.5:1 für Fließtext (erfüllt: #F5F0EB auf #0D0D0D = ~18:1). Fokus-Indikatoren via box-shadow accent-glow, sichtbar für Tastaturnavigation. Placeholder-Kontrast zu bg ≥ 3:1.

# Glamouröser Kleiderschrank-Manager

Eine Fullstack-Webanwendung zur digitalen Verwaltung der persönlichen Garderobe. Benutzer können sich registrieren und einloggen, Kleidungsstücke mit Bildern und Kategorien anlegen, die Garderobe durchstöbern und im Outfit-Creator Einzelteile zu gespeicherten Outfits kombinieren – in glamouröser Hollywood-Red-Carpet-Optik.

## Tech Stack

- **Backend**: FastAPI (Python) mit SQLAlchemy ORM
- **Frontend**: React + Vite
- **Datenbank**: SQLite
- **Auth**: JWT (python-jose)
- **Bildspeicher**: Lokales Dateisystem (uploads/)

## Installation

### Backend

```bash
cd backend
py -m pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Ausführen

### Backend (Entwicklung)

```bash
cd backend
$env:JWT_SECRET = (py -c "import secrets; print(secrets.token_hex(32))")   # PowerShell, oder via RUN.json generiert
$env:FRONTEND_ORIGIN = "http://localhost:5173"
py -m uvicorn main:app --port 8000
```

Der Server startet auf `http://localhost:8000`.

### Frontend (Entwicklung)

```bash
cd frontend
npm run dev
```

Die App öffnet sich auf `http://localhost:5173`.

### Mit RUN.json (automatisiert)

Die Datei `RUN.json` im Projekt-Root deklariert, wie der Backend-Service gestartet wird (inkl. Installation, Port, Health-Check und Umgebungsvariablen). Die Tester-Harness (`_office_run_check.py`) liest diese Datei und startet den Service automatisch:

```bash
py _office_run_check.py
```

## API-Endpunkte

### Health

`GET /api/health` → `{"status":"ok"}` (öffentlich)

### Auth (Stub – Ticket #9)

- `POST /api/auth/register` – Registrierung
- `POST /api/auth/login` – Login (erhält JWT)
- `GET /api/auth/me` – Aktueller Benutzer

### Garderobe (Stub – Ticket #5)

- `GET /api/wardrobe` – Alle Kleidungsstücke (auth, optional ?category=)
- `POST /api/wardrobe` – Neues Kleidungsstück anlegen (auth, multipart)
- `GET /api/wardrobe/{id}` – Einzelnes Kleidungsstück (auth)
- `DELETE /api/wardrobe/{id}` – Kleidungsstück löschen (auth)

### Uploads (Stub – Ticket #6)

- `GET /api/uploads/{filename}` – Bild ausliefern (auth)

### Outfits (Stub – Ticket #3)

- `POST /api/outfits` – Outfit speichern (auth)
- `GET /api/outfits` – Alle Outfits anzeigen (auth)
- `DELETE /api/outfits/{id}` – Outfit löschen (auth)

## Umgebungsvariablen

| Variable | Beschreibung | Standard / Quelle |
|---|---|---|
| `DATABASE_URL` | SQLite-Datenbankpfad | `sqlite:///./wardrobe.db` (dev) |
| `JWT_SECRET` | Signierschlüssel für JWT-Tokens | Wird pro Lauf generiert (RUN.json `generate`) |
| `FRONTEND_ORIGIN` | Erlaubte CORS-Origin (Frontend-URL) | `http://localhost:5173` (dev) |
| `PORT` | Port des Backend-Servers | `8000` (via RUN.json) |

## Features

- Benutzerregistrierung und Login mit JWT-Authentifizierung
- CRUD für Kleidungsstücke mit Bild-Upload (Magic-Byte-Prüfung, EXIF-Stripping)
- Galerie-Ansicht der Garderobe mit Kategorie-Filter
- Outfit-Creator zum Kombinieren von Kleidungsstücken
- Outfit-Übersicht mit Löschfunktion
- Glamouröse Hollywood-Optik mit dunklem Hintergrund und goldenen Akzenten

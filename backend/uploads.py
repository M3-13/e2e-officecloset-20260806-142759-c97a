import io
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, Response
from PIL import Image
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db

router = APIRouter(prefix="/api/uploads")
UPLOAD_DIR = "uploads"

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


def detect_content_type(data: bytes) -> str | None:
    head = data[:256]
    if len(head) < 4:
        return None
    if head[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if head[:4] == b"\x89PNG":
        return "image/png"
    if head[:4] == b"GIF8":
        return "image/gif"
    if head[:4] == b"RIFF" and len(head) >= 12 and head[8:12] == b"WEBP":
        return "image/webp"
    return None


def strip_exif(image_bytes: bytes) -> bytes:
    img = Image.open(io.BytesIO(image_bytes))
    fmt = img.format or "JPEG"
    if img.mode in ("P", "PA"):
        img = img.convert("RGBA" if img.mode == "PA" else "RGB")
    clean = Image.new(img.mode, img.size)
    clean.putdata(list(img.getdata()))
    output = io.BytesIO()
    clean.save(output, format=fmt)
    return output.getvalue()


async def save_upload(file: UploadFile, filename: str) -> str:
    contents = await file.read()

    content_type = detect_content_type(contents)
    if content_type is None or content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Ungültiges Bildformat. Erlaubt: JPEG, PNG, GIF, WebP.",
        )

    cleaned = strip_exif(contents)

    ext = os.path.splitext(filename)[1] or ".jpg"
    stored_name = f"{uuid.uuid4().hex}{ext}"

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filepath = os.path.join(UPLOAD_DIR, stored_name)
    with open(filepath, "wb") as f:
        f.write(cleaned)

    return stored_name


@router.post("", status_code=201)
async def create_upload(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> JSONResponse:
    get_current_user(request, db)

    stored_name = await save_upload(file, file.filename or "upload.jpg")
    url = f"/api/uploads/{stored_name}"
    return JSONResponse(status_code=201, content={"filename": stored_name, "url": url})


@router.get("/{filename}")
async def serve_upload(
    request: Request,
    filename: str,
    db: Session = Depends(get_db),
) -> Response:
    get_current_user(request, db)

    safe_name = os.path.basename(filename)
    filepath = os.path.join(UPLOAD_DIR, safe_name)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Datei nicht gefunden")

    with open(filepath, "rb") as f:
        data = f.read()

    content_type = detect_content_type(data) or "application/octet-stream"

    return Response(
        content=data,
        media_type=content_type,
        headers={"X-Content-Type-Options": "nosniff"},
    )

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/uploads")
UPLOAD_DIR = "uploads/"


async def save_upload(file, filename: str) -> str:
    raise HTTPException(status_code=501, detail="uploads #6 implements this")


@router.get("/{filename}")
async def serve_upload_stub(filename: str):
    raise HTTPException(status_code=501, detail="uploads #6 implements this")

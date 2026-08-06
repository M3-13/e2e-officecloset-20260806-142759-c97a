import os
from enum import StrEnum

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel

from auth import get_current_user
from database import get_db
from models import ClothingItem
from uploads import save_upload

router = APIRouter(prefix="/api/wardrobe")


class CategoryEnum(StrEnum):
    oberteil = "Oberteil"
    hose = "Hose"
    kleid = "Kleid"
    schuhe = "Schuhe"
    accessoire = "Accessoire"


class ClothingItemResponse(BaseModel):
    id: int
    name: str
    category: str
    image_url: str
    created_at: str

    model_config = {"from_attributes": True}


@router.post("", response_model=ClothingItemResponse, status_code=201)
async def create_item(
    name: str = Form(...),
    category: str = Form(...),
    image: UploadFile = File(...),
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    if category not in [e.value for e in CategoryEnum]:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid category '{category}'. Must be one of: {', '.join(e.value for e in CategoryEnum)}",
        )

    filename = await save_upload(image, image.filename or "upload.jpg")

    item = ClothingItem(
        user_id=current_user.id,
        name=name,
        category=category,
        image_filename=filename,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return _to_response(item)


@router.get("", response_model=list[ClothingItemResponse])
async def list_items(
    category: str | None = Query(None),
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(ClothingItem).filter(ClothingItem.user_id == current_user.id)
    if category:
        query = query.filter(ClothingItem.category == category)
    items = query.order_by(ClothingItem.created_at.desc()).all()
    return [_to_response(item) for item in items]


@router.get("/{item_id}", response_model=ClothingItemResponse)
async def get_item(
    item_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = db.query(ClothingItem).filter(ClothingItem.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return _to_response(item)


@router.delete("/{item_id}", status_code=204)
async def delete_item(
    item_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = db.query(ClothingItem).filter(ClothingItem.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    filepath = os.path.join("uploads", item.image_filename)
    if os.path.isfile(filepath):
        os.remove(filepath)

    db.delete(item)
    db.commit()


def _to_response(item: ClothingItem) -> dict:
    return {
        "id": item.id,
        "name": item.name,
        "category": item.category,
        "image_url": f"/api/uploads/{item.image_filename}",
        "created_at": item.created_at.isoformat() if item.created_at else "",
    }

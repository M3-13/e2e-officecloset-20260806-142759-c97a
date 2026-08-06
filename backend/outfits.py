from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models import ClothingItem, Outfit, OutfitItem, User
from schemas.outfits import OutfitCreate, OutfitItemResponse, OutfitResponse

router = APIRouter(prefix="/api/outfits")


def _get_current_user(request: Request, db=Depends(get_db)):
    from auth import get_current_user

    return get_current_user(request, db)


@router.post("", status_code=201, response_model=OutfitResponse)
def create_outfit(
    data: OutfitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    if not data.item_ids:
        raise HTTPException(status_code=400, detail="At least one item is required")

    items = db.query(ClothingItem).filter(ClothingItem.id.in_(data.item_ids)).all()

    if len(items) != len(set(data.item_ids)):
        missing = set(data.item_ids) - {item.id for item in items}
        raise HTTPException(
            status_code=404,
            detail=f"Items not found: {sorted(missing)}",
        )

    for item in items:
        if item.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="One or more items do not belong to you")

    outfit = Outfit(user_id=current_user.id, name=data.name)
    db.add(outfit)
    db.flush()

    for item in items:
        db.add(OutfitItem(outfit_id=outfit.id, clothing_item_id=item.id))

    db.commit()
    db.refresh(outfit)

    items_response = [
        OutfitItemResponse(
            id=item.id,
            name=item.name,
            category=item.category,
            image_url=f"/api/uploads/{item.image_filename}",
        )
        for item in items
    ]

    return OutfitResponse(
        id=outfit.id,
        name=outfit.name,
        items=items_response,
        created_at=outfit.created_at,
    )


@router.get("", response_model=list[OutfitResponse])
def list_outfits(
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    outfits = db.query(Outfit).filter(Outfit.user_id == current_user.id).all()

    result: list[OutfitResponse] = []
    for outfit in outfits:
        outfit_items = db.query(OutfitItem).filter(OutfitItem.outfit_id == outfit.id).all()
        items_response: list[OutfitItemResponse] = []
        for oi in outfit_items:
            item = oi.clothing_item
            if item:
                items_response.append(
                    OutfitItemResponse(
                        id=item.id,
                        name=item.name,
                        category=item.category,
                        image_url=f"/api/uploads/{item.image_filename}",
                    )
                )
        result.append(
            OutfitResponse(
                id=outfit.id,
                name=outfit.name,
                items=items_response,
                created_at=outfit.created_at,
            )
        )

    return result


@router.delete("/{outfit_id}", status_code=204)
def delete_outfit(
    outfit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id).first()

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    if outfit.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this outfit")

    db.delete(outfit)
    db.commit()

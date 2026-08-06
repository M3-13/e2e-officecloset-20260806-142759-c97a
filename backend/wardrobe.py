from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/wardrobe")


@router.get("")
async def list_items_stub():
    raise HTTPException(status_code=501, detail="wardrobe #5 implements this")


@router.post("")
async def create_item_stub():
    raise HTTPException(status_code=501, detail="wardrobe #5 implements this")


@router.get("/{item_id}")
async def get_item_stub(item_id: int):
    raise HTTPException(status_code=501, detail="wardrobe #5 implements this")


@router.delete("/{item_id}")
async def delete_item_stub(item_id: int):
    raise HTTPException(status_code=501, detail="wardrobe #5 implements this")

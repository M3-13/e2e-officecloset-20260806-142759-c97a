from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/outfits")


@router.get("")
async def list_outfits_stub():
    raise HTTPException(status_code=501, detail="outfits #3 implements this")


@router.post("")
async def create_outfit_stub():
    raise HTTPException(status_code=501, detail="outfits #3 implements this")


@router.delete("/{outfit_id}")
async def delete_outfit_stub(outfit_id: int):
    raise HTTPException(status_code=501, detail="outfits #3 implements this")

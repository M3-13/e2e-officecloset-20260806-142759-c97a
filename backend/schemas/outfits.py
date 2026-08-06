from datetime import datetime

from pydantic import BaseModel


class OutfitCreate(BaseModel):
    name: str
    item_ids: list[int]


class OutfitItemResponse(BaseModel):
    id: int
    name: str
    category: str
    image_url: str

    model_config = {"from_attributes": True}


class OutfitResponse(BaseModel):
    id: int
    name: str
    items: list[OutfitItemResponse]
    created_at: datetime

    model_config = {"from_attributes": True}

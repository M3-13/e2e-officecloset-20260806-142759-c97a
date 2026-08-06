from datetime import datetime

from pydantic import BaseModel


class ClothingItemCreate(BaseModel):
    name: str
    category: str


class ClothingItemResponse(BaseModel):
    id: int
    name: str
    category: str
    image_url: str
    created_at: datetime

    model_config = {"from_attributes": True}

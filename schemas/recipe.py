from typing import List, Optional

from pydantic import BaseModel, Field

from schemas.material import Material


class CreateRecipe(BaseModel):
    name: str
    building_id: int
    #amountOutputted: float = Field(..., gt=0)
    custom_power_consumption: Optional[int] = Field(None, gt=0)
    ingredients: Optional[dict[int, float]]
    outputs: dict[int, float] = Field(None, min_items=1)

class Recipe(CreateRecipe):
    id: int

    class Config:
        from_attributes = True

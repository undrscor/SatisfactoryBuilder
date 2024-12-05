from typing import List, Optional

from pydantic import BaseModel, Field

from schemas.material import Material


class CreateBuilding(BaseModel):
    name: str = Field(..., description="Name of the building")
    power_consumption: Optional[int] = Field(None, description="Power consumption in MW")
    required_materials: dict[int, int] = Field(None, min_items=1)

class Building(CreateBuilding):
    id: int

    class Config:
        from_attributes = True


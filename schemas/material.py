from pydantic import BaseModel, Field
from typing_extensions import Optional


class CreateMaterial(BaseModel):
    name: str = Field(..., description="Name of the material")
    #type = Optional[str]


class Material(CreateMaterial):
    id: int

    class Config:
        from_attributes = True
        #frozen = True



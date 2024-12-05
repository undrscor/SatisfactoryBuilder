from pydantic import BaseModel


class CreatePlayer(BaseModel):
    name: str
    password: str


class Player(BaseModel):
    id: int
    name: str

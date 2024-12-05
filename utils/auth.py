import sqlalchemy as sql
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from models.player import PlayerModel
from utils.db import SessionLocal

security = HTTPBasic()


def get_player_id(credentials: HTTPBasicCredentials = Depends(security)) -> int:
    with SessionLocal() as session:
        q = (
            sql.select(PlayerModel.id)
            .where(PlayerModel.name == credentials.username)
            .where(PlayerModel.password == credentials.password)
        )
        player_id = session.execute(q).scalar()

        if player_id is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return player_id

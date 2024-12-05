import sqlalchemy as sql
from fastapi import APIRouter

from utils.db import SessionLocal
from models.player import PlayerModel
from schemas.player import CreatePlayer, Player

player_router = APIRouter()


@player_router.post("", response_model=Player)
def create_player(new_player: CreatePlayer):
    with SessionLocal() as session, session.begin():
        q = (
            sql.insert(PlayerModel)
            .values(
                {
                    PlayerModel.name: new_player.name,
                    PlayerModel.password: new_player.password,
                }
            )
            .returning(PlayerModel.id)
        )
        player_id = session.execute(q).scalar()
    return {
        "id": player_id,
        "name": new_player.name,
    }


@player_router.get("", response_model=list[Player])
def get_players():
    with SessionLocal() as session, session.begin():
        q = sql.select(PlayerModel.id, PlayerModel.name)
        return session.execute(q).mappings().fetchall()

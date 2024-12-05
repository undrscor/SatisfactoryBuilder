import sqlalchemy as sql
from fastapi import APIRouter

from models.building import BuildingModel
from schemas.building import Building, CreateBuilding
from utils.db import SessionLocal

building_router = APIRouter()


@building_router.post("", response_model=Building)
def create_building(new_building: CreateBuilding):
    with SessionLocal() as session, session.begin():
        q = (
            sql.insert(BuildingModel)
            .values({BuildingModel.name: new_building.name,
                     BuildingModel.power_consumption: new_building.power_consumption})
            .returning(BuildingModel.id)
        )
        building_id = session.execute(q).scalar()
    return {
        "id": building_id,
        "name": new_building.name,
    }


@building_router.get("", response_model=list[Building])
def get_buildings():
    with SessionLocal() as session, session.begin():
        q = sql.select(BuildingModel.id, BuildingModel.name)
        return session.execute(q).mappings().fetchall()

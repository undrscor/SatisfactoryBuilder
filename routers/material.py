import sqlalchemy as sql
from fastapi import APIRouter

from utils.db import SessionLocal
from models.material import MaterialModel
from schemas.material import CreateMaterial, Material

material_router = APIRouter()


@material_router.post("", response_model=Material)
def create_material(new_material: CreateMaterial):
    with SessionLocal() as session, session.begin():
        q = (
            sql.insert(MaterialModel)
            .values({MaterialModel.name: new_material.name})
            .returning(MaterialModel.id)
        )
        material_id = session.execute(q).scalar()
    return {
        "id": material_id,
        "name": new_material.name,
    }


@material_router.get("", response_model=list[Material])
def get_materials():
    with SessionLocal() as session, session.begin():
        q = sql.select(MaterialModel.id, MaterialModel.name)
        return session.execute(q).mappings().fetchall()


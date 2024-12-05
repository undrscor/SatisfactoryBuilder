from .base import Model
import sqlalchemy as sql


class M2MBuildingMaterialsModel(Model):
    __tablename__ = "building_materials"

    building_id = sql.Column(
        sql.Integer, sql.ForeignKey("buildings.id"), primary_key=True
    )
    material_id = sql.Column(sql.Integer, sql.ForeignKey("materials.id"), primary_key=True)
    count = sql.Column(sql.Integer)

    __table_args__ = (
        sql.PrimaryKeyConstraint(
            building_id, material_id, name="m2m_building_materials"
        ),
    )


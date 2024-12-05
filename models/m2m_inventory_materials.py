from .base import Model
import sqlalchemy as sql


class M2MInventoryMaterialsModel(Model):
    __tablename__ = "inventory_materials"

    material_id = sql.Column(
        sql.Integer, sql.ForeignKey("materials.id"), primary_key=True
    )
    inventory_id = sql.Column(
        sql.Integer, sql.ForeignKey("players.id"), primary_key=True
    )
    count = sql.Column(sql.Integer)

    __table_args__ = (
        sql.PrimaryKeyConstraint(
            material_id, inventory_id, name="m2m_inventory_materials"
        ),
    )

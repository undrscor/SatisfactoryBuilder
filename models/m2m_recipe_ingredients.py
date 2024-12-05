import sqlalchemy as sql

from .base import Model


class M2MRecipeInputsModel(Model):
    __tablename__ = "recipe_inputs"

    recipe_id = sql.Column(sql.Integer, sql.ForeignKey("recipes.id"), primary_key=True)
    material_id = sql.Column(sql.Integer, sql.ForeignKey("materials.id"), primary_key=True)
    count = sql.Column(sql.Integer)

    __table_args__ = (
        sql.PrimaryKeyConstraint(recipe_id, material_id, name="m2m_recipe_inputs"),
    )

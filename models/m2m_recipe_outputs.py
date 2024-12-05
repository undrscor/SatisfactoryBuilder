from .base import Model
import sqlalchemy as sql


class M2MRecipeOutputsModel(Model):
    __tablename__ = "recipe_outputs"

    recipe_id = sql.Column(sql.Integer, sql.ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    material_id = sql.Column(sql.Integer, sql.ForeignKey("materials.id", ondelete="CASCADE"), primary_key=True)
    count = sql.Column(sql.Integer, nullable=False)


    __table_args__ = (
        sql.PrimaryKeyConstraint(recipe_id, material_id, name="m2m_recipe_outputs"),
    )

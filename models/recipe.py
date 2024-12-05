from .base import Model
import sqlalchemy as sql


class RecipeModel(Model):
    __tablename__ = "recipes"

    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String, unique=True)
    #amountOutputted = sql.Column(sql.Float)
    building_id = sql.Column(sql.Integer)
    custom_power_consumption = sql.Column(sql.Integer, nullable=True) #for quantum encoder, whos power consumption is based on the recipe used


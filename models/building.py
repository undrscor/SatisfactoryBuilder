import sqlalchemy as sql

from .base import Model


class BuildingModel(Model):
    __tablename__ = "buildings"
    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String, unique=True)
    power_consumption = sql.Column(sql.Integer)
    #testname = sql.Column(sql.String)

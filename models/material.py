import sqlalchemy as sql

from .base import Model

class MaterialModel(Model):
    __tablename__ = "materials"
    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String, unique=True)
    #type = sql.Column(sql.String, nullable=True)

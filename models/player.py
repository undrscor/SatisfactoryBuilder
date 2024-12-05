import sqlalchemy as sql

from .base import Model


class PlayerModel(Model):
    __tablename__ = "players"
    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String, unique=True)
    password = sql.Column(sql.String)

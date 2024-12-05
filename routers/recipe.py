import sqlalchemy as sql
from fastapi import APIRouter

from utils.db import SessionLocal
from models.recipe import RecipeModel
from schemas.recipe import CreateRecipe, Recipe

recipe_router = APIRouter()


@recipe_router.post("", response_model=Recipe)
def create_recipe(new_recipe: CreateRecipe):
    with SessionLocal() as session, session.begin():
        q = (
            sql.insert(RecipeModel)
            .values(
                {
                    RecipeModel.name: new_recipe.name,
                    #RecipeModel.amountOutputted: new_recipe.amountOutputted,
                    RecipeModel.building_id: new_recipe.building_id,
                    RecipeModel.custom_power_consumption: new_recipe.custom_power_consumption
                }
            )
            .returning(RecipeModel.id)
        )
        recipe_id = session.execute(q).scalar()
    return {
        "id": recipe_id,
        "name": new_recipe.name,
        #"amount": new_recipe.amountOutputted,
        "building_id": new_recipe.building_id,
        "custom_power_consumption": new_recipe.custom_power_consumption,
    }


@recipe_router.get("", response_model=list[Recipe])
def get_recipes():
    with SessionLocal() as session, session.begin():
        q = sql.select(
            RecipeModel.id,
            RecipeModel.name,
            #RecipeModel.amountOutputted,
            RecipeModel.building_id,
            RecipeModel.custom_power_consumption,
        )
        return session.execute(q).mappings().fetchall()

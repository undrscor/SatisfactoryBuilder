from typing import List

import sqlalchemy as sql

from models import (
    M2MBuildingMaterialsModel,
    M2MRecipeInputsModel,
    M2MRecipeOutputsModel,
    MaterialModel,
    RecipeModel,
)
from models.building import BuildingModel
from schemas.building import Building, CreateBuilding
from schemas.material import CreateMaterial, Material
from schemas.recipe import CreateRecipe, Recipe


def ingest_materials(session, materials_data: List[CreateMaterial]):
    q = (
        sql.insert(MaterialModel)
        .values(
            [
                {MaterialModel.name: material_data.name}
                for material_data in materials_data
            ]
        )
        .returning(MaterialModel.id, MaterialModel.name)
    )
    material_que = session.execute(q).mappings().fetchall()

    return {
        material.name: Material(
            id=material.id,
            name=material.name,
        )
        for material in material_que
    }


def ingest_buildings(session, buildings_data: List[CreateBuilding]):
    buildings = {}
    for building_data in buildings_data:
        q = (
            sql.insert(BuildingModel)
            .values(
                {
                    BuildingModel.name: building_data.name,
                    BuildingModel.power_consumption: building_data.power_consumption,
                }
            )
            .returning(BuildingModel.id)
        )
        building_id = session.execute(q).scalar()

        q = sql.insert(M2MBuildingMaterialsModel).values(
            [
                {
                    M2MBuildingMaterialsModel.building_id: building_id,
                    M2MBuildingMaterialsModel.material_id: material_id,
                    M2MBuildingMaterialsModel.count: count,
                }
                for material_id, count in building_data.required_materials.items()
            ]
        )
        session.execute(q)

        building = Building(
            id=building_id,
            name=building_data.name,
            power_consumption=building_data.power_consumption,
            required_materials=building_data.required_materials,
        )
        buildings[building_data.name] = building
    return buildings


def ingest_recipes(session, recipes_data: List[CreateRecipe]):
    recipes = {}
    for recipe_data in recipes_data:
        print(f"Processing recipe: {recipe_data.name}")
        q = (
            sql.insert(RecipeModel)
            .values(
                {
                    RecipeModel.name: recipe_data.name,
                    RecipeModel.building_id: recipe_data.building_id,
                    RecipeModel.custom_power_consumption: recipe_data.custom_power_consumption,
                }
            )
            .returning(RecipeModel.id)
        )
        recipe_id = session.execute(q).scalar()
        print(recipe_id)
        if recipe_id is None:
            raise ValueError(f"Recipe {recipe_data.name} not found")

        if recipe_data.ingredients is not None:
            q = sql.insert(M2MRecipeInputsModel).values(
                [
                    {
                        M2MRecipeInputsModel.recipe_id: recipe_id,
                        M2MRecipeInputsModel.material_id: material_id,
                        M2MRecipeInputsModel.count: count,
                    }
                    for material_id, count in recipe_data.ingredients.items()
                ]
            )
            session.execute(q)

        q = sql.insert(M2MRecipeOutputsModel).values(
            [
                {
                    M2MRecipeOutputsModel.recipe_id: recipe_id,
                    M2MRecipeOutputsModel.material_id: material_id,
                    M2MRecipeOutputsModel.count: count,
                }
                for material_id, count in recipe_data.outputs.items()
            ]
        )
        session.execute(q)

        recipe = Recipe(
            id=recipe_id,
            name=recipe_data.name,
            building_id=recipe_data.building_id,
            custom_power_consumption=recipe_data.custom_power_consumption,
            ingredients=recipe_data.ingredients,
            outputs=recipe_data.outputs,
        )
        recipes[recipe_data.name] = recipe

    return recipes


# learning dicts
# new_dict = {}
# for item in old_dict.items():
#     new_dict[old_dict_info] = old_dict_key
# return new_dict
# return {old_dict_info : old_dict_key for old_dict_key, old_dict_info in old_dict.items()}

import sys
import time

import sqlalchemy as sql

from models import (
    BuildingModel,
    M2MBuildingMaterialsModel,
    M2MRecipeInputsModel,
    M2MRecipeOutputsModel,
    MaterialModel,
    RecipeModel,
)
from utils.db import SessionLocal


def main():
    print("")
    planner = FactoryPlanner()

    concrete = planner.build_factory("concrete", 60)
    # for item in concrete:
    #     print(item, "required: ", concrete[item])
    # print()

    plate = planner.build_factory("reinforced iron plate", 10)
    for _ in range(3):
        time.sleep(1)
        sys.stdout.write('.')
        sys.stdout.flush()
    time.sleep(1)
    print("\n")

    # for item in concrete:
    #     print(item, "required: ", concrete[item])
    # print()

    for item in plate:
        print(item, "required: ", plate[item])
    print()

    # result = planner.build_factory("dark matter residue", 60)
    # for item in concrete:
    #     print(item,"required: ", result[item])
    # print()
    print("Done!")


class FactoryPlanner:
    def __init__(self):
        self.buildings_required = {}
        self.energy_required = 0
        self.materials_required = {}

    def build_factory(self, target_material: str, target_rate: float):
        # Print the base message without dots
        sys.stdout.write(f"Starting factory breakdown for {target_material} at {target_rate}/min")
        sys.stdout.flush()

        # Print the dots with delay
        for _ in range(3):
            time.sleep(0.8)
            sys.stdout.write('.')
            sys.stdout.flush()
        print("\n")
        time.sleep(1)
        target_material = target_material.strip().replace(" ", "_").lower()
        with SessionLocal() as session, session.begin():
            q = sql.select(MaterialModel.id).where(
                MaterialModel.name == target_material
            )
            material_id = session.execute(q).scalar()
            if not material_id:
                raise ValueError(f"Material {target_material} not found")
            self.recursive_build(material_id, target_rate, session)

        return {
            "buildings": self.buildings_required,
            "energy": self.energy_required,
            "materials": self.materials_required,
        }

    def recursive_build(self, material_id: int, rate: float, session):
        # Get recipe and basic info
        recipe_info = self.get_info(material_id, session)
        material_name = recipe_info[0]["material_name"]
        if not recipe_info:
            # This is a raw material
            print("this is raw as hell: ", material_name)
            return
        if len(recipe_info) > 1:
            print(f"multiple recipes found for {material_name} (need {rate}/min), which would you like to use? (type number)")
            i = 1
            for potential_recipe in recipe_info:
                print(
                    f"{i}: \"{potential_recipe['recipe_name']}\", {potential_recipe['output_rate']}/min with {potential_recipe['building_name']}"
                )
                i += 1
            chosen_recipe = input()
            recipe = recipe_info[int(chosen_recipe) - 1]
        else:
            recipe = recipe_info[0]
            print(
                f"recipe found for {material_name}: {recipe['output_rate']}/min with {recipe['building_name']}")

        recipe_multiplier = rate / recipe["output_rate"]

        self.buildings_required[recipe["building_name"]] = (
            self.buildings_required.get(recipe["building_name"], 0) + recipe_multiplier
        )

        energy_cost = (
            (recipe["building_power_consumption"] or 0)
            + (recipe["custom_power_consumption"] or 0)
        ) * recipe_multiplier
        self.energy_required += energy_cost

        building_materials = self.get_materials(recipe["building_id"], session)
        for material in building_materials:
            self.materials_required[material["name"]] = self.materials_required.get(
                material["name"], 0
            ) + (material["count"] * recipe_multiplier)

        ingredients = self.get_ingredients(recipe["recipe_id"], session)
        for ingredient in ingredients:
            # print(
            #     "needed ingredients: ",
            #     ingredient["material_id"],
            #     " at rate: ",
            #     recipe_multiplier * ingredient["rate"],
            #     print()
            # )
            time.sleep(1)
            self.recursive_build(
                ingredient["material_id"],
                ingredient["rate"] * recipe_multiplier,
                session,
            )

        #print()

    def get_info(self, material_id: int, session):
        q = (
            sql.select(
                MaterialModel.name.label("material_name"),
                RecipeModel.id.label("recipe_id"),
                RecipeModel.name.label("recipe_name"),
                RecipeModel.building_id.label("building_id"),
                BuildingModel.name.label("building_name"),
                BuildingModel.power_consumption.label("building_power_consumption"),
                RecipeModel.custom_power_consumption.label("custom_power_consumption"),
                M2MRecipeOutputsModel.count.label("output_rate"),
            )
            .select_from(
                sql.join(
                    RecipeModel,
                    M2MRecipeOutputsModel,
                    RecipeModel.id == M2MRecipeOutputsModel.recipe_id,
                ).join(
                    BuildingModel,
                    RecipeModel.building_id == BuildingModel.id,
                ).join(
                    MaterialModel,
                    M2MRecipeOutputsModel.material_id == MaterialModel.id,
                )
            )
            .where(M2MRecipeOutputsModel.material_id == material_id)
        )
        recipe: list[dict] = session.execute(q).mappings().fetchall()
        # print(recipe)
        return recipe

    def get_materials(self, building_id: int, session):
        q = (
            sql.select(
                MaterialModel.name.label("name"),
                M2MBuildingMaterialsModel.count.label("count"),
            )
            .select_from(
                sql.join(
                    M2MBuildingMaterialsModel,
                    MaterialModel,
                    M2MBuildingMaterialsModel.material_id == MaterialModel.id,
                )
            )
            .where(M2MBuildingMaterialsModel.building_id == building_id)
        )
        materials: list[dict] = session.execute(q).mappings().fetchall()
        # print(materials)
        return materials

    def get_ingredients(self, recipe_id: int, session):
        q = sql.select(
            M2MRecipeInputsModel.material_id.label("material_id"),
            M2MRecipeInputsModel.count.label("rate"),
        ).where(M2MRecipeInputsModel.recipe_id == recipe_id)
        ingredients: list[dict] = session.execute(q).mappings().fetchall()
        # print(ingredients)
        return ingredients

    def get_material_name(self, material_id: int):
        """Helper method to get material name from ID"""
        pass


if __name__ == "__main__":
    main()

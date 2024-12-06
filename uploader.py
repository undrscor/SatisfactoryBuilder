from sqlalchemy import sql

from ingestor import ingest_buildings, ingest_materials, ingest_recipes
from models import MaterialModel
from schemas.building import CreateBuilding
from schemas.material import CreateMaterial
from schemas.recipe import CreateRecipe
from scrapper import (
    get_building_info,
    get_building_links,
    get_materials,
    get_raw_material_info,
    get_raw_materials,
    get_recipes,
)
from utils.db import SessionLocal


def main():
    upload()


def upload():
    materials = get_materials()
    # print(materials)
    formatted_materials = [
        CreateMaterial(name=material) for material in materials
    ]
    print(formatted_materials)

    all_buildings = []
    for link in get_building_links():
        # print(link)
        all_buildings.extend(get_building_info(link))
    # print(all_buildings)

    recipes = get_recipes()
    # print(recipes)

    raw_recipes = []
    for material in get_raw_materials():
        # print(material)
        raw_recipes.extend(get_raw_material_info(material))
        # print(raw_material_info)
    # print(raw_recipes)

    with SessionLocal() as session, session.begin():
        try:
            ingested_materials = ingest_materials(session, formatted_materials)
            print(ingested_materials)

            formatted_buildings = [
                CreateBuilding(
                    name=name,
                    power_consumption=power,
                    required_materials={
                        ingested_materials[material_name].id: amount
                        for material_name, amount in materials.items()
                    },
                )
                for name, power, materials in all_buildings
            ]
            print(formatted_buildings)
            ingested_buildings = ingest_buildings(session, formatted_buildings)
            print(ingested_buildings)

            formatted_recipes = [
                CreateRecipe(
                    name=recipe,
                    building_id=ingested_buildings[building_name].id,
                    custom_power_consumption=custom_power,
                    ingredients={
                        ingested_materials[material_name].id: amount
                        for material_name, amount in inputs.items()
                    } or None,
                    outputs={
                        ingested_materials[material_name].id: amount
                        for material_name, amount in outputs.items()
                    },
                )
                for recipe, building_name, custom_power, inputs, outputs in recipes
            ]
            print(formatted_recipes)
            ingested_recipes = ingest_recipes(session, formatted_recipes)
            print(ingested_recipes)

            formatted_raw_recipes = [
                CreateRecipe(
                    name=recipe,
                    building_id=ingested_buildings[building_name].id,
                    custom_power_consumption=None,
                    ingredients=None,
                    outputs={ingested_materials[material].id: rate},
                )
                for recipe, building_name, material, rate in raw_recipes
            ]
            print(formatted_raw_recipes)
            ingested_raw_recipes = ingest_recipes(session, formatted_raw_recipes)
            print(ingested_raw_recipes)

            #session.rollback()

        except Exception as e:
            session.rollback()
            raise ValueError(f"Database ingestion failed: {str(e)}")



if __name__ == "__main__":
    main()

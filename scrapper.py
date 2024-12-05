import httpx
from lxml import html
from lxml.html import HtmlElement
from yarl import URL

from ingestor import ingest_buildings, ingest_materials, ingest_recipes
from schemas.building import CreateBuilding
from schemas.material import CreateMaterial
from schemas.recipe import CreateRecipe
from utils.db import SessionLocal

# url = "https://satisfactory.wiki.gg/wiki/Buildings"
base_url = URL("https://satisfactory.wiki.gg/")



def main():
    pass

def get_building_links():
    resp = httpx.get(str(base_url / "wiki/Buildings"))
    tree = html.fromstring(resp.content)
    elements = tree.xpath('//*[@aria-labelledby="Buildings"]/table/tbody/tr')
    # print(elements)
    for element in elements:
        element: HtmlElement
        category = element.xpath("th/text()")
        if category and category[0].strip() == "Production":
            buildings = element.xpath(".//a/@href")
            for building in buildings:
                buildings = element.xpath(".//a/@href")
                building_links = {
                    base_url / building.lstrip("/").split("#")[0]
                    for building in buildings
                }
                # print (buildingset)
                return building_links


def get_building_info(url: URL):
    resp = httpx.get(str(url))
    tree = html.fromstring(resp.content)
    buildings = []
    # Look for asides in the active article
    asides = tree.xpath('//article[@class="tabber__panel"]//aside')

    # If no active article found, fall back to regular aside search
    if not asides:
        asides = tree.xpath("//aside")

    for aside in asides:
        building_name = aside.xpath("h2/text()")[0].strip().replace(" ", "_").lower()
        power_consumption = None
        if building_name == "quantum_encoder":
            power_consumption = 1000
        elif building_name == "converter":
            power_consumption = 250
        else:
            power_text = aside.xpath(
                ".//section//div//h3[contains(., 'Power')]/following-sibling::div[@class='pi-data-value pi-font']/text()"
            )
            if power_text:
                try:
                    power_consumption = int(
                        power_text[0].replace("\xa0", "").replace("MW", "")
                    )
                except ValueError:
                    print(f"Could not parse power value: {power_text}")

        resources = {}
        ingredients = aside.xpath(".//section[.//h2[contains(text(), 'Ingre')]]//b")
        # print(ingredients)
        for ingredient in ingredients:
            amount = int(ingredient.xpath("text()")[0].replace(" × ", ""))
            name = ingredient.xpath(".//a[last()]/@title")[0].replace(" ", "_").lower()
            if name == "portable_miner":
                resources["iron_plate"] = resources.get("iron_plate", 0) + (amount * 2)
                resources["iron_rod"] = resources.get("iron_rod", 0) + (amount * 4)
            else:
                resources[name] = resources.get(name, 0) + amount

        building_info = (building_name, power_consumption, resources)
        buildings.append(building_info)
    return buildings


def get_materials():
    resp = httpx.get(str(base_url / "wiki/Template:ItemNav"))
    tree = html.fromstring(resp.content)
    materials = tree.xpath(
        '//*[@aria-labelledby="Items_and_Fluids"]/table/tbody//a[img]/following-sibling::a/@title'
    )
    materials = {material.strip().replace(" ", "_").lower() for material in materials}
    return list(materials)


def get_raw_materials():
    resp = httpx.get(str(base_url / "wiki/Template:ItemNav"))
    tree = html.fromstring(resp.content)

    elements = tree.xpath('//*[@aria-labelledby="Items_and_Fluids"]/table/tbody/tr')
    raw_materials_set = set()

    for element in elements:
        element: HtmlElement
        category = element.xpath("th/text()")

        if category and category[0].strip() == "Resources":
            raw_resources = element.xpath(".//th[text()='Raw resources']/..//a/@href")
            for material in raw_resources:
                if material not in raw_materials_set:
                    raw_materials_set.add(material)
                    yield base_url / material.lstrip("/")


RAW_LIQUIDS = {
    "crude_oil": {"oil_extractor": 120},
    "nitrogen_gas": {
        "resource_well_extractor": 60,
    },
    "water": {"water_extractor": 120},
}


def get_raw_material_info(url: URL):
    resp = httpx.get(str(url))
    tree = html.fromstring(resp.content)
    material_data = []
    name = tree.xpath('//h1[@id="firstHeading"]//text()')[0].strip().replace(" ", "_").lower()
    # print(name)

    if name in RAW_LIQUIDS:
        for building, rate in RAW_LIQUIDS[name].items():
            material_data.append((name, building, name, rate))
    else:
        ore_table = tree.xpath(
            '//article[@data-mw-tabber-title="100% Clock Speed"]//table[@class="wikitable"]'
        )
        if not ore_table:
            return material_data
        # print(ore_table)
        rows = ore_table[0].xpath(".//tr")
        named_rows = {
            row.xpath(".//th//text()")[0].strip(): row.xpath(".//td/text()")
            for row in rows
        }

        for i, rate in enumerate(named_rows["Normal"], 1):  # enumerate starting at 1
            miner = (
                f"{name}_mk.{i}",
                f"miner_mk.{i}",
                name,
                float(rate),
            )
            material_data.append(miner)

    # print(material_data)
    return material_data


RECIPES_TO_SKIP = {
    "biomass_",
    "unpackage_",
    "_fireworks",
    "_protein",
    "_inhaler",
    "power_shard_",
    "_(burning)",
    "turbo_rifle_ammo",
    # ... add more recipes to skip
}


def get_recipes():
    resp = httpx.get(str(base_url / "wiki/Recipes"))
    tree = html.fromstring(resp.content)
    elements = tree.xpath(
        '//table[contains(@class, "wikitable") and contains(@class, "recipetable")]/tbody/tr'
    )
    recipes = []
    converter_recipes = []

    for element in elements:
        element: HtmlElement

        # Check for recipe badges (FICSMAS, alternative, etc.)
        badges = element.xpath('.//td[1]//span[contains(@class, "recipe-badge")]')
        if badges:
            continue  # Skip if recipe has any badges

        # Get recipe name
        name_texts = element.xpath("td[1]/text()")
        if not name_texts:
            continue
        recipe_name = name_texts[0].strip().replace(" ", "_").lower()

        # skip unwanted recipes
        if any(skip in recipe_name for skip in RECIPES_TO_SKIP):
            continue

        try:
            building_elements = element.xpath(
                './/td[3]//div[@class="recipe-building"]/a/text()'
            )
            if not building_elements:
                print(f"No building found for {recipe_name}")
                continue
            building_name = building_elements[0].strip().replace(" ", "_").lower()
            custom_power_consumption = None
            # Skip Equipment Workshop recipes
            if building_name == "equipment_workshop":
                continue
            if building_name == "quantum_encoder":
                custom_power_consumption = 1000
            if building_name == "converter":
                custom_power_consumption = 250
            # Get custom power consumption for particle accelerator
            if building_name == "particle_accelerator":
                custom_power_elements = element.xpath(
                    'td[3]//div[@class="recipe-building"]/span/text()'
                )
                if not custom_power_elements:
                    print(f"Error finding custom power consumption: ")
                    continue
                power_text = custom_power_elements[0]
                try:
                    power_parts = power_text.split("-")
                    if len(power_parts) > 1:
                        firstnum = int(
                            power_parts[0]
                            .strip()
                            .replace(",", "")
                            .replace("MW", "")
                            .replace(" ", "")
                        )
                        secondnum = int(
                            power_parts[1]
                            .strip()
                            .replace(",", "")
                            .replace("MW", "")
                            .replace(" ", "")
                        )
                        custom_power_consumption = (firstnum + secondnum) / 2
                except ValueError as e:
                    print(f"Error parsing power consumption: {e}")

            # Get ingredients
            ingredients = {}
            ingredient_items = element.xpath('.//td[2]//div[@class="recipe-item"]')
            for item in ingredient_items:
                item_name = (
                    item.xpath('.//span[@class="item-name"]/text()')[0]
                    .strip()
                    .replace(" ", "_")
                    .lower()
                )
                rate = float(
                    item.xpath('.//span[@class="item-minute"]/text()')[0]
                    .strip()
                    .replace("\xa0", "")
                    .replace("/min", "")
                    .replace(",", "")
                )
                ingredients[item_name] = rate

            # Get outputs
            outputs = {}
            output_items = element.xpath('.//td[4]//div[@class="recipe-item"]')
            for item in output_items:
                item_name = (
                    item.xpath('.//span[@class="item-name"]/text()')[0]
                    .strip()
                    .replace(" ", "_")
                    .lower()
                )
                rate = float(
                    item.xpath('.//span[@class="item-minute"]/text()')[0]
                    .strip()
                    .replace("\xa0", "")
                    .replace("/min", "")
                    .replace(",", "")
                )
                outputs[item_name] = rate

            recipe_data = (
                recipe_name,
                building_name,
                custom_power_consumption,
                ingredients,
                outputs,
            )

            # Sort into appropriate category
            if building_name == "converter":
                converter_recipes.append(recipe_data)
            else:
                recipes.append(recipe_data)

        except Exception as e:
            print(
                f"Error processing recipe {name_texts[0] if name_texts else 'unknown'}: {e}"
            )
            continue

    #final_recipes = {"recipes": recipes, "converter_recipes": converter_recipes}
    #return recipes + converter_recipes
    return recipes


if __name__ == "__main__":
    main()

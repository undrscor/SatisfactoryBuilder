import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from routers.building import building_router
from routers.material import material_router
from routers.player import player_router
from routers.recipe import recipe_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return RedirectResponse("/docs")


app.include_router(building_router, prefix="/building", tags=["Building"])
app.include_router(material_router, prefix="/material", tags=["Material"])
app.include_router(player_router, prefix="/player", tags=["Player"])
app.include_router(recipe_router, prefix="/recipe", tags=["Recipe"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

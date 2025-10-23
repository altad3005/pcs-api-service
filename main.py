from procyclingstats import Race, RaceStartlist, Stage, Ranking

import os
from fastapi import FastAPI, Request, HTTPException, status
app = FastAPI()

API_TOKEN = os.getenv("API_TOKEN", "super-secret-token")  # ou via ton .env

@app.middleware("http")
async def verify_token(request: Request, call_next):
    # Autorise la page d'accueil et docs publiques
    if request.url.path in ["/", "/docs", "/openapi.json"]:
        return await call_next(request)

    # Récupère le token depuis les headers
    token = request.headers.get("x-api-key")
    if token != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API token"
        )

    return await call_next(request)

@app.get("/race/{race_id}/{year}")
def get_race_info(race_id: str, year: str):
    """
    Exemple: /race/tour-de-france/2025
    Retourne les informations générales d'une course
    """
    race = Race(f"race/{race_id}/{year}")
    return race.parse()


@app.get("/race/{race_id}/{year}/startlist")
def get_startlist(race_id: str, year: str):
    """
    Exemple: /race/tour-de-france/2025/startlist
    Retourne la liste de départ d'une course
    """
    startlist = RaceStartlist(f"race/{race_id}/{year}/startlist")
    riders = startlist.startlist()
    return riders


@app.get("/race/{race_id}/{year}/gc")
def get_gc(race_id: str, year: str):
    """
    Exemple: /race/tour-de-france/2025/gc
    Retourne le classement général d'une course
    (utilise la dernière étape si c’est un GT)
    """
    race = Race(f"race/{race_id}/{year}")
    stages = race.stages()

    if not stages:
        # Si c'est une course d'un jour, retourner les résultats directs
        stage = Stage(f"race/{race_id}/{year}/result")
        return stage.results()

    # Prendre la dernière étape pour avoir le GC final
    last_stage_url = stages[-1]["stage_url"]
    stage = Stage(last_stage_url)

    return stage.gc() or []


@app.get("/race/{race_id}/{year}/stage/{stage_number}")
def get_stage_results(race_id: str, year: str, stage_number: str):
    """
    Exemple: /race/tour-de-france/2025/stage/1
    Retourne les résultats d'une étape spécifique
    """
    stage = Stage(f"race/{race_id}/{year}/stage-{stage_number}")
    return stage.results()


@app.get("/race/{race_id}/{year}/stages")
def get_stages_list(race_id: str, year: str):
    """
    Exemple: /race/tour-de-france/2025/stages
    Retourne la liste de toutes les étapes d'une course
    """
    race = Race(f"race/{race_id}/{year}")
    return race.stages()


@app.get("/ranking/individual")
def get_individual_ranking():
    """
    Exemple: /ranking/individual?limit=10
    Retourne le classement PCS individuel mondial
    """
    ranking = Ranking("rankings/me/individual")
    data = ranking.individual_ranking(
        "rider_name",
        "rank",
        "points",
        "nationality",
        "team_name",
    )
    return data


@app.get("/")
def root():
    """
    Documentation des endpoints disponibles
    """
    return {
        "message": "API ProcyclingStats",
        "endpoints": {
            "race_info": "/race/{race_id}/{year}",
            "startlist": "/race/{race_id}/{year}/startlist",
            "gc": "/race/{race_id}/{year}/gc",
            "stage_results": "/race/{race_id}/{year}/stage/{stage_number}",
            "stages_list": "/race/{race_id}/{year}/stages",
            "individual_ranking": "/ranking/individual",
        },
        "example": {
            "Tour de France 2025 startlist": "/race/tour-de-france/2025/startlist",
            "Tour de France 2025 GC": "/race/tour-de-france/2025/gc",
            "Tour de France 2025 Stage 1": "/race/tour-de-france/2025/stage/1",
            "Individual Ranking": "/ranking/individual?limit=10",
        },
    }

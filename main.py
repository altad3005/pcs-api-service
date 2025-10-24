from procyclingstats import Race, RaceStartlist, Stage, Ranking
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
app = FastAPI()

API_TOKEN = os.getenv("API_TOKEN")

@app.middleware("http")
async def verify_token(request: Request, call_next):
    public_paths = ["/", "/docs", "/openapi.json", "/favicon.ico"]
    if any(request.url.path.startswith(p) for p in public_paths):
        return await call_next(request)

    expected_token = os.getenv("API_TOKEN")
    if not expected_token:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "code": 500,
                "message": "Server misconfiguration: API_TOKEN is not set",
            },
        )

    token = request.headers.get("x-api-key") or request.headers.get("X-API-Key")
    if token != expected_token:
        return JSONResponse(
            status_code=401,
            content={
                "status": "error",
                "code": 401,
                "message": "Unauthorized: Invalid or missing API token",
                "hint": "Use header 'x-api-key' with your API token",
            },
        )

    return await call_next(request)




@app.get("/race/{race_id}/{year}")
def get_race_info(race_id: str, year: str):
    """Retourne les informations générales d'une course"""
    race = Race(f"race/{race_id}/{year}")
    return race.parse()


@app.get("/race/{race_id}/{year}/startlist")
def get_startlist(race_id: str, year: str):
    """Retourne la liste de départ d'une course"""
    startlist = RaceStartlist(f"race/{race_id}/{year}/startlist")
    return startlist.startlist()


@app.get("/race/{race_id}/{year}/gc")
def get_gc(race_id: str, year: str):
    """Retourne le classement général d'une course"""
    race = Race(f"race/{race_id}/{year}")
    stages = race.stages()

    if not stages:
        stage = Stage(f"race/{race_id}/{year}/result")
        return stage.results()

    last_stage_url = stages[-1]["stage_url"]
    stage = Stage(last_stage_url)
    return stage.gc() or []


@app.get("/race/{race_id}/{year}/stage/{stage_number}")
def get_stage_results(race_id: str, year: str, stage_number: str):
    """Retourne les résultats d'une étape spécifique"""
    stage = Stage(f"race/{race_id}/{year}/stage-{stage_number}")
    return stage.results()


@app.get("/race/{race_id}/{year}/stages")
def get_stages_list(race_id: str, year: str):
    """Retourne la liste de toutes les étapes d'une course"""
    race = Race(f"race/{race_id}/{year}")
    return race.stages()


@app.get("/ranking/individual")
def get_individual_ranking():
    """Retourne le classement PCS individuel mondial"""
    ranking = Ranking("rankings/me/individual")
    return ranking.individual_ranking(
        "rider_name", "rank", "points", "nationality", "team_name"
    )


@app.get("/")
def root():
    """Documentation des endpoints disponibles"""
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

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.tasks import router as tasks_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="CloudOps Pro",
    description="DevOps Task Management API",
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

app.include_router(tasks_router)


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(BASE_DIR / "templates" / "dashboard.html")


@app.get("/health/live", tags=["Health"])
def liveness():
    return {"status": "alive"}

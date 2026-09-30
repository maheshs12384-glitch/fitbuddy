import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .database import init_db
from .routes import BASE_DIR, router

app = FastAPI(title="FitBuddy - AI Fitness Plan Generator")
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
init_db()
app.include_router(router)

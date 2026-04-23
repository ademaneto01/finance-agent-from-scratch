from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import search, agent

from database.connection import Base, engine
import database.models  # noqa: F401  (ensure models are registered on Base)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(engine)
        logger.info("Database tables verified/created")
    except Exception as exc:
        logger.error(f"Failed to create database tables: {exc}")
    yield


app = FastAPI(title="Financial Search API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(agent.router)


@app.get("/")
def root():
    return {"status": "online"}

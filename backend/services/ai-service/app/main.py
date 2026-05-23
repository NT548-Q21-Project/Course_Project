from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import Base, create_database_if_not_exists, engine
from app.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        create_database_if_not_exists()
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        import logging

        logging.error(f"Startup error: {e}")
        raise
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
def health_check():
    return {
        "service": "ai-service",
        "status": "ok",
    }
Instrumentator().instrument(app).expose(app)

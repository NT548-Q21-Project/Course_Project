from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.core.config import settings
from app.db.session import Base, create_database_if_not_exists, engine
from app.router import router as recruitment_router


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
Instrumentator().instrument(app).expose(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recruitment_router)


@app.get("/health")
def health_check():
    return {"service": "recruitment-service", "status": "ok"}

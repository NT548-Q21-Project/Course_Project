from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import Base, create_database_if_not_exists, engine
from app.router import router as recruitment_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database_if_not_exists()
    Base.metadata.create_all(bind=engine)
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

app.include_router(recruitment_router)


@app.get("/health")
def health_check():
    return {"service": "recruitment-service", "status": "ok"}

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_database_if_not_exists() -> None:
    # Lấy db name từ DATABASE_URL
    db_name = settings.DATABASE_URL.split("/")[-1]

    # Connect vào postgres default db
    postgres_url = settings.DATABASE_URL.rsplit("/", 1)[0] + "/postgres"
    temp_engine = create_engine(postgres_url, isolation_level="AUTOCOMMIT")

    with temp_engine.connect() as conn:
        result = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
            {"db_name": db_name},
        )
        if not result.fetchone():
            conn.execute(text(f"CREATE DATABASE {db_name}"))

    temp_engine.dispose()

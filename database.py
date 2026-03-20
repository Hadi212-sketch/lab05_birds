import os
from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

if os.getenv("ENVIRONMENT") == "DOCKER":
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
else:
    POSTGRES_HOST = "127.0.0.1"

DATABASE_URL = (
    f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

engine = create_engine(DATABASE_URL)


def get_session():
    """Yield a database session for dependency injection."""
    with Session(engine) as session:
        yield session


def start_db():
    """Create all tables defined in SQLModel metadata."""
    SQLModel.metadata.create_all(engine)

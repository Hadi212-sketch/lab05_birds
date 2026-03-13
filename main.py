from fastapi import FastAPI

from database import start_db

app = FastAPI(
    title="Birds API",
    description="A FastAPI project for managing bird species, individual birds, and birdspotting observations.",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    """Create database tables on application startup."""
    start_db()


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint — health check."""
    return {"message": "Hello World"}

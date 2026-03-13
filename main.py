from fastapi import FastAPI

from database import start_db
from routers import birds, species

app = FastAPI(
    title="Birds API",
    description="A FastAPI project for managing bird species, individual birds, and birdspotting observations.",
    version="1.0.0",
)

app.include_router(species.router)
app.include_router(birds.router)


@app.on_event("startup")
def on_startup():
    """Create database tables on application startup."""
    start_db()


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint — health check."""
    return {"message": "Hello World"}

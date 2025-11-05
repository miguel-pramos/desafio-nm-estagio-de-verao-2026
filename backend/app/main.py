from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .config.settings import get_settings
from .routers import auth, chat, health
from .services.embedding import chroma_db_populated, create_vector_store


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler: optional ingestion on startup using settings."""

    if settings.INGEST_ON_STARTUP:
        base_url = settings.INGEST_BASE_URL

        if base_url:
            if not chroma_db_populated() or settings.INGEST_FORCE:
                await create_vector_store(base_url)
                

    yield


app = FastAPI(lifespan=lifespan)

# Session middleware is required for OAuth state management
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET,  # Reuse JWT secret for session signing
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(chat.router)

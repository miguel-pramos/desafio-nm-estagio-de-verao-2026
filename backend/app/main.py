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
    logger = logging.getLogger(__name__)

    if settings.INGEST_ON_STARTUP:
        raw = settings.INGEST_URLS or ""
        urls = [u.strip() for u in raw.split(",") if u.strip()]

        if not urls:
            logger.warning(
                "INGEST_ON_STARTUP is true but INGEST_URLS is empty; nothing to ingest"
            )
        else:
            if chroma_db_populated() and not settings.INGEST_FORCE:
                logger.info(
                    "Chroma DB already populated and INGEST_FORCE is false; skipping ingestion"
                )
            else:
                try:
                    logger.info("Starting vectorstore ingestion for %d urls", len(urls))
                    await create_vector_store(urls)
                    logger.info("Vectorstore ingestion complete")
                except Exception as e:
                    logger.exception("Vectorstore ingestion failed: %s", e)

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

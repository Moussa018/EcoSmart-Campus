import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import router as v1_router
from app.auth.routes import router as auth_router
from app.config import settings
from app.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        f"Démarrage de {settings.APP_NAME} en mode [{settings.APP_ENV}]",
        extra={"extra_data": {"port": settings.PORT, "debug": settings.DEBUG}}
    )
    yield
    logger.info(f"Arrêt propre de {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Plateforme IoT & IA de pilotage énergétique et environnemental pour campus universitaire.\n\n"
        "**Sprint 1 - Socle & Dérisquage de l'agent :**\n"
        "- Authentification JWT & Contrôle d'accès par rôle (RF01)\n"
        "- Contrat OpenAPI & Données factices pour le frontend (T01, T06)\n"
        "- Prototype de l'assistant LangChain avec appel d'outils (T09, RF24, RF25)\n"
        "- Journalisation structurée JSON (RNF5)"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configuration CORS pour le frontend React Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def json_logging_middleware(request: Request, call_next):
    """Middleware de journalisation JSON de chaque requête HTTP (RNF5 / T02)."""
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)

    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms} ms)",
        extra={"extra_data": {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "client_ip": request.client.host if request.client else "unknown",
        }}
    )
    return response


# Inclusion des routeurs
app.include_router(auth_router, prefix="/api/v1")
app.include_router(v1_router, prefix="/api/v1")


@app.get("/", tags=["Racine"])
async def root():
    return {
        "message": f"Bienvenue sur l'API {settings.APP_NAME}",
        "documentation": "/docs",
        "openapi": "/openapi.json",
        "sprint": 1,
    }

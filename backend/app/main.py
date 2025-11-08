"""
FastAPI Haupt-Anwendung
DSGVO-konformes Patientenaktensystem
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time

from app.core.config import settings
from app.core.database import init_db
from app.api import auth, patients

# Lifecycle-Management


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle-Manager für Startup/Shutdown

    Startup:
    - Initialisiere Datenbank
    - Lade Konfiguration

    Shutdown:
    - Schließe Verbindungen
    """
    # Startup
    print("🚀 Starte Patientenaktensystem...")
    try:
        init_db()
        print("✅ Datenbank initialisiert")
    except Exception as e:
        print(f"❌ Datenbank-Fehler: {e}")

    yield

    # Shutdown
    print("👋 Fahre Patientenaktensystem herunter...")


# FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="DSGVO-konformes digitales Patientenaktensystem für Osteopathiepraxis",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan
)

# CORS-Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request-Timing-Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Fügt Process-Time-Header hinzu"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler für Validierungsfehler"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "message": "Validierungsfehler"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler für allgemeine Fehler"""
    if settings.DEBUG:
        # In Debug-Modus: Zeige vollständige Exception
        import traceback
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Interner Serverfehler",
                "detail": str(exc),
                "traceback": traceback.format_exc()
            }
        )
    else:
        # In Produktion: Verstecke Details
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Interner Serverfehler",
                "detail": "Bitte kontaktieren Sie den Support"
            }
        )


# API Routes
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(patients.router, prefix=settings.API_V1_PREFIX)


# Health Check
@app.get("/health")
async def health_check():
    """
    Health-Check-Endpoint für Monitoring

    Returns:
        Status und Version
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "service": settings.PROJECT_NAME
    }


# Root Endpoint
@app.get("/")
async def root():
    """
    Root-Endpoint mit API-Info

    Returns:
        API-Informationen
    """
    return {
        "message": "DSGVO-konformes Patientenaktensystem API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
        "health": "/health"
    }


# Startup-Event
@app.on_event("startup")
async def startup_event():
    """Wird beim Startup ausgeführt"""
    print(f"""
    ╔════════════════════════════════════════════════════════════╗
    ║  🏥 {settings.PROJECT_NAME:^53} ║
    ╠════════════════════════════════════════════════════════════╣
    ║  Version: {settings.VERSION:^48} ║
    ║  API Docs: {settings.API_V1_PREFIX + '/docs':^47} ║
    ║  DSGVO-konform: ✅                                         ║
    ║  Verschlüsselung: AES-256 ✅                               ║
    ║  Audit-Logging: ✅                                         ║
    ╚════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

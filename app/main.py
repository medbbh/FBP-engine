import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine
from app.routers import auth, declarations, facilities, imports, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="FBP Engine — Performance-Based Financing",
    description="Moteur de calcul FBP/PBF pour systèmes de santé (Mauritanie / INAYA)",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def audit_log_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    print(  # noqa: T201 — intentional audit trail output
        f"[AUDIT] {request.method} {request.url.path} → {response.status_code} ({duration_ms}ms)"
    )
    return response


app.include_router(auth.router)
app.include_router(facilities.router)
app.include_router(declarations.router)
app.include_router(reports.router)
app.include_router(imports.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "version": "0.1.0"}

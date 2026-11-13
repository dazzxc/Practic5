import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    health,
    upload,
    analysis,
    reports,
    visualization,
    export,
    reports_history
)

from app.services.cleanup_service import (
    cleanup_old_uploads,
    cleanup_loop
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.to_thread(cleanup_old_uploads)
    cleanup_task = asyncio.create_task(cleanup_loop())
    try:
        yield
    finally:
        cleanup_task.cancel()
        with suppress(asyncio.CancelledError):
            await cleanup_task


app = FastAPI(
    title="Data Quality API",
    description="API for data profiling and quality analysis",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(analysis.router, prefix="/api", tags=["Analysis"])
app.include_router(reports.router, prefix="/api", tags=["Reports"])
app.include_router(visualization.router, prefix="/api", tags=["Visualization"])
app.include_router(export.router, prefix="/api", tags=["Export"])
app.include_router(reports_history.router, prefix="/api", tags=["History"])
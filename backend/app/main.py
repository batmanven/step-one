from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

from app.config import settings

app = FastAPI(
    title="Content & Design Engine",
    description="Automated marketing asset generation from event media",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

output_dir = Path("outputs")
output_dir.mkdir(exist_ok=True)
(output_dir / "linkedin").mkdir(exist_ok=True)
(output_dir / "instagram").mkdir(exist_ok=True)
(output_dir / "stories").mkdir(exist_ok=True)
(output_dir / "case_studies").mkdir(exist_ok=True)

@app.get("/")
async def root():
    return {
        "message": "Content & Design Engine API",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "process": "/api/v1/process/{dataset_name}"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

from app.api.v1 import router as v1_router
app.include_router(v1_router, prefix="/api/v1")

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.fastapi_port, reload=True)

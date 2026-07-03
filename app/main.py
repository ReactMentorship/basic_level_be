"""FastAPI application entrypoint.

All API routes are mounted under ``/api`` to match the frontend's axios
baseURL (``http://localhost:8000/api``).
"""
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config
from .routers import auth, categories, posts
from .store import seed

app = FastAPI(title="Basic Level BE", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(categories.router)
api_router.include_router(posts.router)
app.include_router(api_router)

# Populate the in-memory store with a default user + sample content.
seed()


@app.get("/")
def root():
    return {"message": "Basic Level BE (FastAPI) is running", "docs": "/docs"}

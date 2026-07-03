"""Application configuration, read from environment variables with sane defaults."""
import os

# --- Auth / JWT ---
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24h

# --- Server ---
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))

# --- CORS (comma-separated origins, or "*" for all) ---
CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "*").split(",")]

# Default credentials seeded on startup (handy for local development)
SEED_USERNAME = os.environ.get("SEED_USERNAME", "admin")
SEED_PASSWORD = os.environ.get("SEED_PASSWORD", "admin123")

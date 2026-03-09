import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load .env file for local development
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import pathlib

from backend.core.database import Base, engine
from backend.api.routes import chat as chat_routes
from backend.api.websockets import chat as chat_websockets

# Ensure GEMINI_API_KEY is available
if "GEMINI_API_KEY" not in os.environ:
    print("WARNING: GEMINI_API_KEY environment variable not set. LLM features will fail.")

# Create database tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat_routes.router)
app.include_router(chat_websockets.router)

# Serve frontend static files
_frontend_dir = pathlib.Path(__file__).parent.parent / "frontend"
if _frontend_dir.exists():
    app.mount("/app", StaticFiles(directory=_frontend_dir, html=True), name="frontend")

@app.get("/")
def read_root():
    """Redirect root to the frontend app."""
    return RedirectResponse(url="/app")

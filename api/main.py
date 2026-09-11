import sys
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ============================================================
# PATH SETUP
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FARMER_ACCESS = PROJECT_ROOT / "farmer-access"
CORE_PATH = FARMER_ACCESS / "core"

if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))


# ============================================================
# CENTRAL ENGINE
# ============================================================

from access_engine import process_message

logger = logging.getLogger("grainflow.api")


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="GrainFlow API",
    description="Backend API for the GrainFlow smart procurement platform.",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://grainflow-frontend.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class FarmerMessage(BaseModel):
    message: str
    session_id: str = "web"


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "success": True,
        "service": "GrainFlow API",
        "status": "running",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/api/health")
def health_check():
    return {
        "success": True,
        "service": "GrainFlow API",
        "backend": "connected",
    }


# ============================================================
# MESSAGE PROCESSING
# ============================================================

@app.post("/api/message")
def grainflow_message(request: FarmerMessage):

    try:

        message = request.message.strip()

        if not message:

            return {
                "success": False,
                "completed": False,
                "message": "Please enter a message.",
            }

        session_id = request.session_id.strip()

        if not session_id:

            session_id = "web"

        result = process_message(
            message,
            session_id,
        )

        if not isinstance(result, dict):

            return {
                "success": False,
                "completed": False,
                "message":
                    "GrainFlow returned an invalid response.",
            }

        return result

    except Exception:
        logger.exception("GrainFlow message processing failed")

        return {
            "success": False,
            "completed": False,
            "message":
                "GrainFlow could not process your request. Please try again.",
        }
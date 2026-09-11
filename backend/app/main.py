from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.modules.dashboard.routes import router as dashboard_router
from backend.app.modules.procurement.router import router as procurement_router
from backend.app.modules.farmer.router import router as farmer_router
from backend.app.db.database import Base, engine
from backend.app.modules.booking.router import router as booking_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GrainFlow Smart Procurement Platform",
    description="AI-powered smart procurement and queue management system",
    version="1.0.0"
)

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

app.include_router(dashboard_router)
app.include_router(farmer_router)
app.include_router(booking_router)
app.include_router(procurement_router)

@app.get("/")
def root():
    return {"message": "GrainFlow API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
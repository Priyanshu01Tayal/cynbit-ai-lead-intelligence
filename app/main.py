"""
Cynbit AI - Main FastAPI Application
Entrypoint for the REST API backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db, SessionLocal
from app.models.lead import LeadModel
from app.routes import leads, analytics, ml
from app.ml.evaluate import is_model_trained
from app.ml.train import train_lead_classifier

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB tables
    init_db()
    
    # Train model if not present
    if not is_model_trained():
        print("[Startup] ML model not found. Training initial baseline model...")
        train_lead_classifier()
        
    # Auto-seed sample leads if database is empty
    db = SessionLocal()
    try:
        count = db.query(LeadModel).count()
        if count == 0:
            print("[Startup] Database is empty. Seeding initial historical leads...")
            from app.routes.leads import seed_historical_leads
            seed_historical_leads(force=True, db=db)
            print("[Startup] Sample leads seeded successfully.")
    except Exception as e:
        print(f"[Startup] Seeding check error: {e}")
    finally:
        db.close()
        
    yield
    # Shutdown logic (if any)

app = FastAPI(
    title="Cynbit AI – Intelligent Lead Qualification & Automation API",
    description="Backend REST API for Cynbit Technologies' AI Lead Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Streamlit frontend and local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(leads.router)
app.include_router(analytics.router)
app.include_router(ml.router)

@app.get("/")
def root():
    return {
        "service": "Cynbit AI Lead Intelligence Platform",
        "status": "online",
        "docs_url": "/docs",
        "version": "1.0.0"
    }

@app.get("/api/health")
def health_check():
    db = SessionLocal()
    try:
        lead_count = db.query(LeadModel).count()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        lead_count = 0
    finally:
        db.close()
        
    return {
        "status": "healthy",
        "database": db_status,
        "lead_count": lead_count,
        "model_loaded": is_model_trained(),
        "environment": settings.ENVIRONMENT
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)

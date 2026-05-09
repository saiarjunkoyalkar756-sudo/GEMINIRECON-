from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import scans, targets, vulnerabilities, users, auth
from core.storage.database import init_db

app = FastAPI(
    title="GEMINIRECON API",
    description="Enterprise-grade AI-assisted reconnaissance and vulnerability assessment platform",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(targets.router, prefix="/targets", tags=["Targets"])
app.include_router(scans.router, prefix="/scans", tags=["Scans"])
app.include_router(vulnerabilities.router, prefix="/vulnerabilities", tags=["Vulnerabilities"])

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "GEMINIRECON API is running", "version": "2.0.0"}

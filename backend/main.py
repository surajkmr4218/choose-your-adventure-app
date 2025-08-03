import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from routers import story, job
from db.database import create_tables

# Create tables on startup
create_tables()

app = FastAPI(
    title="Choose your own adventure game api",
    description="Generate cool stories",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# import ALLOWED_ORIGINS from settings 
# TODO: ADD VERCEL FRONTEND TO .env
allowed_origins = settings.ALLOWED_ORIGINS
if isinstance(allowed_origins, str):
    allowed_origins = [origin.strip() for origin in allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware, 
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(story.router, prefix=settings.API_PREFIX)
app.include_router(job.router, prefix=settings.API_PREFIX)

# Health check endpoint for deployment platforms
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    
    # Use environment variables for production deployment
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    
    # Check if we're in production (Railway sets this automatically)
    is_production = os.getenv("RAILWAY_ENVIRONMENT") or not settings.DEBUG
    
    if is_production:
        uvicorn.run("main:app", host="0.0.0.0", port=port)
    else:
        uvicorn.run("main:app", host=host, port=port, reload=True)
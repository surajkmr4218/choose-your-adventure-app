from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Choose your own adventure game api",
    description="Generate cool stories",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
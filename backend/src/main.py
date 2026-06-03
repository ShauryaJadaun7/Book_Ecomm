from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from src.core.database import engine, Base
from src.core.config import settings 
from src.modules.users.router import router as auth_router
from src.modules.users.models import User 

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=========================================================")
    print(f"Initializing {settings.APP_NAME} startup hooks...")
    async with engine.begin() as transactional_context:
        # Prerequisite structural extensions
        await transactional_context.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto;"))
        # await transactional_context.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;")) # Bypassed temporarily
        await transactional_context.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        
        # Compile database tables from SQLAlchemy classes
        await transactional_context.run_sync(Base.metadata.create_all)
        print("Production table spaces successfully established.")
    print("=========================================================")
    yield
    print("Offloading context pools. System terminating safely...")
    await engine.dispose()

# Initialize the core FastAPI app container
app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

# 1. Configure CORS Middleware (Crucial for React frontend session storage)
app.add_middleware(
    CORSMiddleware,
    # Change the default port addres to 5173 
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Mount your Authentication pipeline routes onto the app instance
app.include_router(auth_router)

# 3. Baseline API server health check route
@app.get("/")
async def health_check():
    return {"status": "online", "application": settings.APP_NAME}


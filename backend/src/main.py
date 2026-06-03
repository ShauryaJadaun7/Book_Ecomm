from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from src.core.database import engine, Base
from src.core.config import settings 

# Import routers and layout blueprints from all active modules
from src.modules.users.router import router as auth_router
from src.modules.marketplace.router import router as books_router  # <-- Add import
from src.modules.wishlist.router import router as wishlist_router  # <-- Add import

# Import all active structural entities so metadata builds correctly
from src.modules.users.models import User 
from src.modules.marketplace.models import Book  # <-- Add import

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=========================================================")
    print(f"🚀 Initializing {settings.APP_NAME} startup hooks...")
    async with engine.begin() as transactional_context:
        await transactional_context.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto;"))
        await transactional_context.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))  
        await transactional_context.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        
        await transactional_context.run_sync(Base.metadata.create_all)
        print("✅ Production table spaces successfully established.")
    print("=========================================================")
    yield
    print("🛑 Offloading context pools...")
    await engine.dispose()

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register endpoints to the gateway application instance
app.include_router(auth_router)
app.include_router(books_router)
app.include_router(wishlist_router) # <-- Mount books router

@app.get("/")
async def health_check():
    return {"status": "online"}

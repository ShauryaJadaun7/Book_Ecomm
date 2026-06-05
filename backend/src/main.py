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
from src.modules.blogs.router import router as blogs_router  # <-- Add import
from src.modules.feed.router import router as feed_router
from src.modules.payments.router import router as payments_router  # <-- Add import
from src.modules.payments.models import Transaction

# Import all active structural entities so metadata builds correctly
from src.modules.users.models import User 
from src.modules.marketplace.models import Book
from src.modules.blogs.models import Blog
from src.modules.wishlist.models import WishlistItem  # <-- Add import
  # <-- Add import
from src.modules.payments.models import Transaction
# Related to the issue of loading books cover in the frontend
from fastapi.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=========================================================")
    print(f"Initializing {settings.APP_NAME} startup hooks...")
    async with engine.begin() as transactional_context:
        await transactional_context.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto;"))
        await transactional_context.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))  
        await transactional_context.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        
        await transactional_context.run_sync(Base.metadata.create_all)
        print("Production table spaces successfully established.")
    print("=========================================================")
    yield
    print("Offloading context pools. System terminating safely...")
    await engine.dispose()

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    # Change the default port addres to 5173 
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register endpoints to the gateway application instance
app.include_router(auth_router)
app.include_router(books_router)
app.include_router(wishlist_router) # <-- Mount books router

# Mount the static directory to serve uploaded images
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def health_check():
    return {"status": "online", "application": settings.APP_NAME}


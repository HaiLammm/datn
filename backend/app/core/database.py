from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# The database URL should be in the format:
# "postgresql+asyncpg://user:password@host:port/database"
# Ensure your DATABASE_URL in .env uses 'postgresql+asyncpg' for async support

# Create an async engine
engine = create_async_engine(str(settings.DATABASE_URL), echo=True, pool_pre_ping=True)

# Create an async session maker
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

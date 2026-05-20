from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def build_engine_kwargs(url: str) -> tuple[str, dict]:
    """Strip asyncpg-incompatible URL params and return (clean_url, connect_args)."""
    connect_args: dict = {}
    for param in ("sslmode=require", "channel_binding=require"):
        if param in url:
            url = url.replace(f"?{param}", "").replace(f"&{param}", "")
            if param.startswith("sslmode"):
                connect_args["ssl"] = "require"
    return url, connect_args


_db_url, _connect_args = build_engine_kwargs(settings.get_database_url())

engine = create_async_engine(
    _db_url,
    echo=settings.ENVIRONMENT == "development",
    pool_pre_ping=True,
    connect_args=_connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

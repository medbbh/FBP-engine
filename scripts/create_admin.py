import asyncio
from app.core.database import build_engine_kwargs
from app.core.config import settings
from app.auth.password import hash_password
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

EMAIL = "admin@fbp.mr"
PASSWORD = "Admin1234!"


async def main():
    url, kwargs = build_engine_kwargs(settings.get_database_url())
    engine = create_async_engine(url, connect_args=kwargs)
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "INSERT INTO users (email, hashed_password, role, is_active) "
                "VALUES (:email, :pw, 'admin', true) "
                "ON CONFLICT (email) DO NOTHING"
            ),
            {"email": EMAIL, "pw": hash_password(PASSWORD)},
        )
    await engine.dispose()
    print(f"Admin ready: {EMAIL} / {PASSWORD}")


asyncio.run(main())

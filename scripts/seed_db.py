"""CLI entry point: python -m scripts.seed_db"""
import asyncio

from app.core.database import AsyncSessionLocal
from app.seed.runner import seed


async def main() -> None:
    async with AsyncSessionLocal() as session:
        await seed(session)


if __name__ == "__main__":
    asyncio.run(main())

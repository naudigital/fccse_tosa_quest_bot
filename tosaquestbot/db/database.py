from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class Database:  # noqa: WPS306
    """Application database."""

    def __init__(self, url: str):
        """Initialize database.

        Args:
            url: Database URL.
        """
        self._engine = create_async_engine(url)
        self._sessionmaker = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session.

        Yields:
            Database session.
        """
        async with self._sessionmaker() as session:
            yield session

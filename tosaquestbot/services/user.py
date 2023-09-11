from typing import TYPE_CHECKING

from sqlalchemy import select

from tosaquestbot.db import models

if TYPE_CHECKING:
    from tosaquestbot.db.database import Database


class UserService:
    """User service."""

    def __init__(self: "UserService", db: "Database"):
        """Initiate service.

        Args:
            db: Database.
        """
        self.db = db

    async def get_user_by_telegram_id(
        self: "UserService",
        telegram_id: int,
    ) -> models.User | None:
        """Get user by telegram id.

        Args:
            telegram_id: Telegram id.

        Returns:
            User or None.
        """
        async with self.db.session() as session:
            return (
                await session.execute(
                    select(models.User).where(models.User.telegram_id == telegram_id),
                )
            ).scalar_one_or_none()

    async def get_user(self: "UserService", user_id: str) -> models.User | None:
        """Get user.

        Args:
            user_id: User id.

        Returns:
            User or None.
        """
        async with self.db.session() as session:
            return (
                await session.execute(
                    select(models.User).where(models.User.id == user_id),
                )
            ).scalar_one_or_none()

    async def add_user(
        self: "UserService",
        telegram_id: int,
        first_name: str,
        username: str | None,
    ) -> models.User:
        """Add user.

        Args:
            telegram_id: Telegram id.
            first_name: First name.
            username: Username.

        Returns:
            User.
        """
        async with self.db.session() as session:
            user = models.User(
                telegram_id=telegram_id,
                first_name=first_name,
                username=username,
            )
            session.add(user)
            await session.commit()
            return user

    async def update_user(
        self: "UserService",
        user: models.User,
    ) -> models.User:
        """Update user.

        Args:
            user: User.

        Returns:
            User.
        """
        async with self.db.session() as session:
            session.add(user)
            await session.commit()
            return user

    async def get_all_users(self: "UserService") -> list[models.User]:
        """Get all users.

        Returns:
            List of users.
        """
        async with self.db.session() as session:
            users_seq = (await session.execute(select(models.User))).scalars().all()
            return list(users_seq)

    async def get_top_users(self: "UserService", count: int) -> list[models.User]:
        """Get top users.

        Args:
            count: Number of users to return.

        Returns:
            List of users.
        """
        async with self.db.session() as session:
            activations = (
                (await session.execute(select(models.Activation))).scalars().all()
            )
            activations_by_user: dict[str, int] = {}
            for activation in activations:
                if str(activation.user_id) not in activations_by_user:
                    activations_by_user[str(activation.user_id)] = 0
                activations_by_user[str(activation.user_id)] += 1

            stmt = select(models.User).where(
                models.User.id.in_(activations_by_user.keys()),
            )
            users = list((await session.execute(stmt)).scalars().all())

            def sort_func(user: models.User) -> int:  # noqa: WPS430
                return activations_by_user[str(user.id)]

            users.sort(key=sort_func, reverse=True)

            return users[:count]

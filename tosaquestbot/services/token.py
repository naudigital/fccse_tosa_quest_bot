from logging import getLogger
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from tosaquestbot.db import models
from tosaquestbot.errors import TokenAlreadyActivatedError, TokenAlreadyExistsError

if TYPE_CHECKING:
    from tosaquestbot.db.database import Database

logger = getLogger(__name__)


class TokenService:
    """Token service."""

    def __init__(self: "TokenService", db: "Database"):
        """Initiate service.

        Args:
            db: Database.
        """
        self.db = db

    async def create_token(self: "TokenService", name: str) -> models.Token:
        """Create token.

        Args:
            name: Token name.

        Returns:
            Token.

        Raises:
            TokenAlreadyExistsError: If token already exists.
        """
        async with self.db.session() as session:
            token = models.Token(name=name)
            session.add(token)
            try:
                await session.commit()
            except IntegrityError:  # noqa: WPS329
                raise TokenAlreadyExistsError
        logger.info("Created token %s", token.id)
        return token

    async def delete_token(self: "TokenService", token_id: str) -> None:
        """Delete token.

        Args:
            token_id: Token id.
        """
        async with self.db.session() as session:
            token = (
                await session.execute(
                    select(models.Token).where(models.Token.id == token_id),
                )
            ).scalar_one_or_none()
            if not token:
                return
            await session.delete(token)
            await session.commit()

    async def update_token(self: "TokenService", token: models.Token) -> models.Token:
        """Update token.

        Args:
            token: Token.

        Returns:
            Token.
        """
        async with self.db.session() as session:
            session.add(token)
            await session.commit()
            return token

    async def activate_token(
        self: "TokenService",
        token: models.Token,
        user: models.User,
    ) -> models.Activation:
        """Activate token.

        Args:
            token: Token.
            user: User.

        Returns:
            Activation.

        Raises:
            TokenAlreadyActivatedError: If token already activated.
        """
        async with self.db.session() as session:
            activation = models.Activation(user_id=user.id, token_id=token.id)
            session.add(activation)
            try:
                await session.commit()
            except IntegrityError:  # noqa: WPS329
                raise TokenAlreadyActivatedError from None
            await session.refresh(activation)
        logger.info("Activated token %s for user %s", token.id, user.id)
        return activation

    async def get_token(self: "TokenService", token_id: str) -> models.Token | None:
        """Get token.

        Args:
            token_id: Token id.

        Returns:
            Token.
        """
        async with self.db.session() as session:
            return (
                await session.execute(
                    select(models.Token).where(models.Token.id == token_id),
                )
            ).scalar_one_or_none()

    async def get_token_by_name(self: "TokenService", name: str) -> models.Token | None:
        """Get token by name.

        Args:
            name: Token name.

        Returns:
            Token.
        """
        async with self.db.session() as session:
            return (
                await session.execute(
                    select(models.Token).where(models.Token.name == name),
                )
            ).scalar_one_or_none()

    async def get_all_tokens(self: "TokenService") -> list[models.Token]:
        """Get all tokens.

        Returns:
            List of tokens.
        """
        async with self.db.session() as session:
            tokens_seq = (await session.execute(select(models.Token))).scalars().all()
            return list(tokens_seq)

    async def get_activations_by_user(
        self: "TokenService",
        user: models.User,
    ) -> list[models.Activation]:
        """Get activations by user.

        Args:
            user: User.

        Returns:
            List of activations.
        """
        async with self.db.session() as session:
            stmt = select(models.Activation).where(models.Activation.user_id == user.id)
            return list(((await session.execute(stmt)).scalars().all()))

    async def get_activation(
        self: "TokenService",
        activation_id: str,
    ) -> models.Activation | None:
        """Get activation.

        Args:
            activation_id: Activation id.

        Returns:
            Activation.
        """
        async with self.db.session() as session:
            return (
                await session.execute(
                    select(models.Activation).where(
                        models.Activation.id == activation_id,
                    ),
                )
            ).scalar_one_or_none()

    async def revoke_activation(
        self: "TokenService",
        activation: models.Activation,
    ) -> None:
        """Revoke activation.

        Args:
            activation: Activation.
        """
        async with self.db.session() as session:
            await session.delete(activation)
            await session.commit()
        logger.info("Revoked activation %s", activation.id)

    async def get_all_activations(self: "TokenService") -> list[models.Activation]:
        """Get all activations.

        Returns:
            List of activations.
        """
        async with self.db.session() as session:
            activations_seq = (
                (await session.execute(select(models.Activation))).scalars().all()
            )
            return list(activations_seq)

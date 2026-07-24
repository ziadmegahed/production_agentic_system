"""ORM model for the ``users`` table."""


from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.data.schemas.base import SQLAlchemyBase

if TYPE_CHECKING:
    from src.data.schemas.chat_session import ChatSession  # noqa: F401

class User(SQLAlchemyBase):

    """ORM representation of the ``users`` table.

    Attributes:
        id (UUID): Primary key, auto-generated via ``uuid4``.
        first_name (str): User's first name, max 100 characters.
        last_name (str): User's last name, max 100 characters.
        email (str): Unique, indexed email address, max 255 characters.
        hashed_password (str): Bcrypt-hashed password, never plain-text.
        is_active (bool): Whether the account is active; defaults to
            ``True``.
        is_verified (bool): Whether the email has been verified; defaults
            to ``False``.
        chat_sessions (list[ChatSession]): One-to-many relationship to
            ``ChatSession``; cascades delete-orphan.
    """


    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )

    first_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
        )
    
    last_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
        )
    

    email: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )           

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        "ChatSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )       

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True
    )

    async def update(self, user_id: UUID, **kwargs) -> User | None:
        """Apply a partial update to an existing user.

        Only keys present in ``kwargs`` are written; ``None`` values are
        skipped so callers can pass ``UserUpdate.model_dump(exclude_unset=True)``.

        Args:
            user_id: UUID of the user to update.
            **kwargs: Column-value pairs to update.

        Returns:
            The updated ``User`` instance, or ``None`` if not found.
        """
        user = await self.get(user_id)
        if user is None:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(user, key, value)
        await self._db_session.flush()
        return user

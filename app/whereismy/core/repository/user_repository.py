# app/whereismy/core/repository/user_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.whereismy.core.models import User, UserRole
from app.whereismy.core.repository.base import BaseRepository
from sqlalchemy import select


class UserRepository(BaseRepository[User]):
    """
    Репозиторий для работы с пользователями (User).
    """
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Найти пользователя по его Telegram ID."""
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Найти пользователя по его имени (для аутентификации)."""
        stmt = select(User).where(User.username == username)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_moderator_by_username(self, username: str) -> User | None:
        """Найти модератора по его имени (для аутентификации)."""
        stmt = select(User).where(User.username == username, User.role == UserRole.MODERATOR)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

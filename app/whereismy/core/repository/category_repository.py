# app/whereismy/core/repository/category_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.whereismy.core.models import Category
from app.whereismy.core.repository.base import BaseRepository

class CategoryRepository(BaseRepository[Category]):
    """
    Репозиторий для работы с категориями (Category).
    """
    def __init__(self, session: AsyncSession):
        super().__init__(session, Category)

    # Можно добавить специфичные методы, например:
    async def get_by_name(self, name: str) -> Category | None:
        """Найти категорию по её имени."""
        from sqlalchemy import select
        stmt = select(Category).where(Category.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

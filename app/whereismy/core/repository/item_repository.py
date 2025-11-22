# app/whereismy/core/repository/item_repository.py
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pgvector.sqlalchemy import Vector
from app.whereismy.core.models import Item
from app.whereismy.core.repository.base import BaseRepository

class ItemRepository(BaseRepository[Item]):
    """
    Репозиторий для работы с объявлениями о находках/потерях (Item).
    """
    def __init__(self, session: AsyncSession):
        super().__init__(session, Item)

    async def create_item_with_vector(self, title: str, description: str, category_id: int, location_id: Optional[int], user_id: int, vector: List[float]) -> Item:
        """Создать объявление с вектором описания."""
        db_item = Item(
            title=title,
            description=description,
            category_id=category_id,
            location_id=location_id,
            author_id=user_id,
            vector=vector # Присваиваем вектор как есть
        )
        return await self.create(db_item)

    async def find_similar_items(self, query_vector: List[float], limit: int = 5) -> List[Item]:
        """
        Найти объявления, похожие на заданный вектор (семантический поиск).
        Использует оператор <-> для косинусного расстояния.
        """
        # Используем raw SQL для оператора <-> pgvector
        # SQLAlchemy не всегда генерирует его идеально через ORM
        stmt = select(Item).order_by(Item.vector.cosine_distance(query_vector)).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    # Пример метода для поиска по тексту (точное совпадение или LIKE)
    async def find_by_title_or_description(self, search_text: str) -> List[Item]:
        """Найти объявления по частичному совпадению в заголовке или описании."""
        stmt = select(Item).where(
            Item.title.ilike(f"%{search_text}%") |
            Item.description.ilike(f"%{search_text}%")
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

# app/whereismy/services/items_service.py
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.whereismy.core.repository.item_repository import ItemRepository
from app.whereismy.core.repository.user_repository import UserRepository # Для проверок
from app.whereismy.core.models import Item, ItemStatus
from app.whereismy.services.embedding_service import embedding_service # Используем глобальный экземпляр

logger = logging.getLogger(__name__)

class ItemsService:
    """
    Сервис для бизнес-логики, связанной с объявлениями (Item).
    """
    def __init__(self, item_repo: ItemRepository, user_repo: UserRepository):
        self.item_repo = item_repo
        self.user_repo = user_repo

    async def create_found_item(self, session: AsyncSession, title: str, description: str, category_id: int, location_id: Optional[int], user_id: int) -> Item:
        """
        Создает новое объявление о находке, векторизуя описание.
        """
        logger.info(f"Создание объявления о находке для пользователя {user_id}.")
        # 1. Векторизуем описание
        vector = await embedding_service.embed_text(description)

        # 2. Создаем объект Item и сохраняем в БД через репозиторий
        new_item = await self.item_repo.create_item_with_vector(
            session=session,
            title=title,
            description=description,
            category_id=category_id,
            location_id=location_id,
            user_id=user_id,
            vector=vector
        )
        logger.info(f"Объявление о находке создано с ID {new_item.id}.")
        return new_item

    async def find_similar_found_items(self, session: AsyncSession, query_description: str, limit: int = 5) -> List[Item]:
        """
        Находит объявления о находке, похожие на заданное описание (семантический поиск).
        """
        logger.info(f"Поиск похожих объявлений для описания: {query_description[:50]}...")
        # 1. Векторизуем поисковый запрос
        query_vector = await embedding_service.embed_text(query_description)

        # 2. Ищем похожие объявления в БД через репозиторий
        # Пока ищем только среди активных объявлений о находке
        similar_items = await self.item_repo.find_similar_items(
            session=session,
            query_vector=query_vector,
            limit=limit
        )
        logger.info(f"Найдено {len(similar_items)} похожих объявлений.")
        return similar_items

    async def archive_item(self, session: AsyncSession, item_id: int, user_id: int) -> bool:
        """
        Архивирует объявление, если оно принадлежит указанному пользователю.
        """
        logger.info(f"Попытка архивации объявления {item_id} пользователем {user_id}.")
        # 1. Получаем объявление
        item = await self.item_repo.get(session, item_id)
        if not item:
            logger.warning(f"Объявление {item_id} не найдено.")
            return False

        # 2. Проверяем, принадлежит ли оно пользователю
        if item.author_id != user_id:
            logger.warning(f"Пользователь {user_id} не является автором объявления {item_id}.")
            return False

        # 3. Проверяем, не архивировано ли оно уже
        if item.status == ItemStatus.ARCHIVED:
            logger.info(f"Объявление {item_id} уже архивировано.")
            return True # Считаем операцию успешной, если цель достигнута

        # 4. Обновляем статус
        item.status = ItemStatus.ARCHIVED
        updated_item = await self.item_repo.update(session, item, item) # Обновляем самим собой
        logger.info(f"Объявление {item_id} архивировано пользователем {user_id}.")
        return True

    async def get_user_items(self, session: AsyncSession, user_id: int) -> List[Item]:
        """
        Получает список объявлений пользователя.
        """
        # Это можно сделать через репозиторий, добавив метод, или через ORM напрямую в сервисе.
        # Пока добавим простой метод в репозиторий ItemRepository.
        # Но для примера, сделаем запрос здесь.
        from sqlalchemy import select
        stmt = select(Item).where(Item.author_id == user_id).where(Item.status != ItemStatus.ARCHIVED)
        result = await session.execute(stmt)
        items = result.scalars().all()
        return items

# app/whereismy/core/repository/base.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase

# Определяем универсальный тип для модели
ModelType = TypeVar("ModelType", bound=DeclarativeBase)

class BaseRepository(ABC, Generic[ModelType]):
    """
    Абстрактный базовый класс для репозиториев.
    Определяет общие методы CRUD.
    """
    def __init__(self, session: AsyncSession, model: type[ModelType]):
        self._session = session
        self._model = model

    async def get(self, id: int) -> Optional[ModelType]:
        """Получить один объект по ID."""
        stmt = select(self._model).where(self._model.id == id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Получить список объектов с пагинацией."""
        stmt = select(self._model).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create(self, obj_in: ModelType) -> ModelType:
        """Создать новый объект."""
        self._session.add(obj_in)
        await self._session.commit()
        await self._session.refresh(obj_in)
        return obj_in

    async def update(self, db_obj: ModelType, obj_in: ModelType) -> ModelType:
        """Обновить существующий объект."""
        for key, value in obj_in.__dict__.items():
            if hasattr(db_obj, key) and key != "_sa_instance_state": # Защита от атрибута SQLAlchemy
                setattr(db_obj, key, value)
        await self._session.commit()
        await self._session.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> bool:
        """Удалить объект по ID."""
        obj = await self.get(id)
        if obj:
            await self._session.delete(obj)
            await self._session.commit()
            return True
        return False

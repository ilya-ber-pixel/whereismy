# app/whereismy/core/models/base.py

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.

    Включает поддержку асинхронных операций (AsyncAttrs) и является
    основой для декларативного стиля (DeclarativeBase).
    """
    __abstract__ = True  # Указывает, что это не таблица, а класс для наследования

    id: Mapped[int] = mapped_column(primary_key=True)
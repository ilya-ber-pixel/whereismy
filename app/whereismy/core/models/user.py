# app/whereismy/core/models/user.py

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

if TYPE_CHECKING:
    from .item import Item


class User(Base):
    """
    Модель пользователя Telegram.
    """
    __tablename__ = 'users'

    # Уникальный ID пользователя из Telegram, может быть очень большим
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(unique=False, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow
    )

    # Отношение "один ко многим": один пользователь может иметь много объявлений
    # back_populates создает двунаправленную связь с моделью Item
    items: Mapped[list["Item"]] = relationship(back_populates="author")
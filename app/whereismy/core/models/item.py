# app/whereismy/core/models/item.py

import datetime
import enum
from typing import TYPE_CHECKING, Optional

import numpy as np
from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

# TYPE_CHECKING позволяет использовать типы для статического анализа,
# избегая циклических импортов во время выполнения.
if TYPE_CHECKING:
    from .user import User
    from .category import Category
    from .location import Location


# Использование Enums делает код более читаемым и надежным,
# предотвращая ошибки с опечатками в строках.
class ItemType(enum.Enum):
    FOUND = "found"
    LOST = "lost"

class ItemStatus(enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"

class ContactMethod(enum.Enum):
    LEFT_AT = "left_at"
    CONTACT_ME = "contact_me"


class Item(Base):
    """
    Модель объявления о находке или потере.
    """
    __tablename__ = 'items'

    # Внешние ключи для связей
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("locations.id"), nullable=True
    )

    # Поля с перечислениями
    type: Mapped[ItemType] = mapped_column(nullable=False, native_enum=False)
    status: Mapped[ItemStatus] = mapped_column(
        default=ItemStatus.ACTIVE,
        server_default=ItemStatus.ACTIVE.value,
        native_enum=False 
    )
    
    # Описательные поля
    description: Mapped[str | None] = mapped_column(nullable=True)
    photo_id: Mapped[str | None] = mapped_column(nullable=True) # file_id из Telegram
    specific_place: Mapped[str | None] = mapped_column(nullable=True)

    # Поля для способа связи
    contact_method: Mapped[ContactMethod] = mapped_column(nullable=False, native_enum=False)
    contact_info: Mapped[str | None] = mapped_column(nullable=True)

    # Векторное поле для семантического поиска.
    # Размерность 384 соответствует модели paraphrase-multilingual-MiniLM-L12-v2.
    vector: Mapped[np.ndarray | None] = mapped_column(Vector(384), nullable=True)

    # Временные метки
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())")
    )
    archived_at: Mapped[datetime.datetime | None] = mapped_column(nullable=True)
    
    # Определяем обратные связи для удобного доступа к связанным объектам из Item
    author: Mapped["User"] = relationship(back_populates="items")
    category: Mapped["Category"] = relationship(back_populates="items")
    location: Mapped[Optional["Location"]] = relationship(back_populates="items")
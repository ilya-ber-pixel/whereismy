# app/whereismy/core/models/category.py

from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

if TYPE_CHECKING:
    from .item import Item


class Category(Base):
    """
    Модель типа (категории) вещи.
    """
    __tablename__ = 'categories'

    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    items: Mapped[list["Item"]] = relationship(back_populates="category")
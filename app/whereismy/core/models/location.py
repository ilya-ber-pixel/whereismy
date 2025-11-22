# app/whereismy/core/models/location.py

from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

if TYPE_CHECKING:
    from .item import Item


class Location(Base):
    """
    Модель корпуса (местоположения).
    """
    __tablename__ = 'locations'

    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)

    items: Mapped[list["Item"]] = relationship(back_populates="location")